"""Gestor optimizado de Google Drive."""
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
import json
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from io import BytesIO

from src.cache.document_cache import DocumentCache
from src.monitoring.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

@dataclass
class DriveQuota:
    """Cuota de uso de Google Drive."""
    limit: int
    used: int
    remaining: int
    reset_time: datetime

class DriveManager:
    """Gestor optimizado de Google Drive."""
    
    def __init__(
        self,
        credentials: Credentials,
        cache: DocumentCache,
        batch_size: int = 10,
        rate_limit: int = 1000  # Requests por minuto
    ):
        self.credentials = credentials
        self.cache = cache
        self.batch_size = batch_size
        self.rate_limiter = RateLimiter(rate_limit, 60)
        
        # Servicios
        self.drive_service = build('drive', 'v3', credentials=credentials)
        self.docs_service = build('docs', 'v1', credentials=credentials)
        
        # Estado
        self._quota: Optional[DriveQuota] = None
        self._token_refresh_task = None
    
    async def _refresh_token_periodically(self):
        """Refrescar token periódicamente."""
        while True:
            # Refrescar 5 minutos antes de expirar
            expiry = self.credentials.expiry
            if expiry:
                delay = (expiry - datetime.utcnow()).total_seconds() - 300
                if delay > 0:
                    await asyncio.sleep(delay)
            
            try:
                # Refrescar token
                self.credentials.refresh(None)
                logger.info("Token de Google Drive refrescado")
            except Exception as e:
                logger.error(f"Error al refrescar token: {e}")
            
            await asyncio.sleep(60)  # Verificar cada minuto
    
    async def start(self):
        """Iniciar gestor."""
        # Iniciar refresh de token
        self._token_refresh_task = asyncio.create_task(
            self._refresh_token_periodically()
        )
        
        # Cargar cuota inicial
        await self.update_quota()
    
    async def stop(self):
        """Detener gestor."""
        if self._token_refresh_task:
            self._token_refresh_task.cancel()
            try:
                await self._token_refresh_task
            except asyncio.CancelledError:
                pass
    
    async def update_quota(self) -> DriveQuota:
        """Actualizar información de cuota."""
        async with self.rate_limiter:
            about = self.drive_service.about().get(fields="storageQuota").execute()
            quota = about.get("storageQuota", {})
            
            self._quota = DriveQuota(
                limit=int(quota.get("limit", 0)),
                used=int(quota.get("usage", 0)),
                remaining=int(quota.get("limit", 0)) - int(quota.get("usage", 0)),
                reset_time=datetime.utcnow() + timedelta(days=1)
            )
            
            return self._quota
    
    async def batch_get_files(
        self,
        file_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Obtener múltiples archivos en batch."""
        # Verificar caché primero
        results = []
        missing_ids = []
        
        for file_id in file_ids:
            cached = await self.cache.get_document(file_id)
            if cached:
                results.append(cached)
            else:
                missing_ids.append(file_id)
        
        if not missing_ids:
            return results
        
        # Procesar en batches
        async with self.rate_limiter:
            for i in range(0, len(missing_ids), self.batch_size):
                batch = missing_ids[i:i + self.batch_size]
                batch_request = self.drive_service.new_batch_http_request()
                
                for file_id in batch:
                    batch_request.add(
                        self.drive_service.files().get(
                            fileId=file_id,
                            fields="id,name,mimeType,size,modifiedTime,capabilities"
                        )
                    )
                
                responses = batch_request.execute()
                
                for file_id, response in zip(batch, responses):
                    if response:
                        # Guardar en caché
                        await self.cache.set_document(file_id, response)
                        results.append(response)
        
        return results
    
    async def stream_upload(
        self,
        file_path: str,
        mime_type: str,
        chunk_size: int = 1024 * 1024  # 1MB
    ) -> Dict[str, Any]:
        """Subir archivo en streaming."""
        async with self.rate_limiter:
            # Crear archivo
            file_metadata = {
                'name': file_path.split('/')[-1],
                'mimeType': mime_type
            }
            
            with open(file_path, 'rb') as f:
                media = MediaIoBaseUpload(
                    f,
                    mimetype=mime_type,
                    chunksize=chunk_size,
                    resumable=True
                )
                
                file = self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,mimeType,size,modifiedTime'
                ).execute()
                
                return file
    
    async def stream_download(
        self,
        file_id: str,
        chunk_size: int = 1024 * 1024  # 1MB
    ) -> AsyncGenerator[bytes, None]:
        """Descargar archivo en streaming."""
        async with self.rate_limiter:
            request = self.drive_service.files().get_media(fileId=file_id)
            
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request, chunksize=chunk_size)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    fh.seek(0)
                    yield fh.read()
                    fh.seek(0)
                    fh.truncate()
    
    async def watch_changes(
        self,
        folder_id: str,
        callback: callable,
        check_interval: int = 60
    ):
        """Observar cambios en una carpeta."""
        page_token = None
        
        while True:
            try:
                async with self.rate_limiter:
                    # Listar cambios
                    response = self.drive_service.changes().list(
                        pageToken=page_token,
                        spaces='drive',
                        fields='nextPageToken, newStartPageToken, changes(fileId, time, removed, file(id, name, modifiedTime))'
                    ).execute()
                    
                    # Procesar cambios
                    for change in response.get('changes', []):
                        if change.get('removed'):
                            # Invalidar caché
                            await self.cache.invalidate_document(change['fileId'])
                        
                        # Notificar cambio
                        await callback(change)
                    
                    # Actualizar token
                    page_token = response.get('nextPageToken')
                    if not page_token:
                        page_token = response.get('newStartPageToken')
                    
                    # Esperar siguiente verificación
                    await asyncio.sleep(check_interval)
                    
            except Exception as e:
                logger.error(f"Error al observar cambios: {e}")
                await asyncio.sleep(check_interval)
    
    async def get_thumbnail(
        self,
        file_id: str,
        size: str = 'w320'
    ) -> Optional[bytes]:
        """Obtener miniatura de archivo."""
        cache_key = f"thumb:{file_id}:{size}"
        
        # Verificar caché
        cached = await self.cache.get_document(cache_key)
        if cached:
            return cached
        
        try:
            async with self.rate_limiter:
                thumbnail = self.drive_service.files().get_media(
                    fileId=file_id,
                    fields=f"thumbnailLink({size})"
                ).execute()
                
                if thumbnail:
                    # Guardar en caché por 1 día
                    await self.cache.set_document(
                        cache_key,
                        thumbnail,
                        ttl=86400
                    )
                    return thumbnail
                
        except Exception as e:
            logger.error(f"Error al obtener miniatura: {e}")
        
        return None
