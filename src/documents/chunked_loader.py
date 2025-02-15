"""Módulo para carga progresiva de documentos."""
from typing import Dict, Any, List, Generator, Optional
import asyncio
from dataclasses import dataclass
from math import ceil

@dataclass
class ChunkMetadata:
    """Metadatos de un chunk de documento."""
    index: int
    offset: int
    size: int
    page_range: tuple[int, int]
    checksum: str

class DocumentChunker:
    """Gestor de chunks para documentos grandes."""
    
    def __init__(
        self,
        chunk_size: int = 1024 * 1024,  # 1MB por chunk
        max_concurrent_chunks: int = 3
    ):
        self.chunk_size = chunk_size
        self.max_concurrent_chunks = max_concurrent_chunks
    
    def calculate_chunks(
        self,
        total_size: int,
        total_pages: int
    ) -> List[ChunkMetadata]:
        """Calcular metadata de chunks para un documento.
        
        Args:
            total_size: Tamaño total en bytes
            total_pages: Número total de páginas
            
        Returns:
            Lista de metadatos de chunks
        """
        num_chunks = ceil(total_size / self.chunk_size)
        pages_per_chunk = ceil(total_pages / num_chunks)
        
        chunks = []
        for i in range(num_chunks):
            start_offset = i * self.chunk_size
            end_offset = min(start_offset + self.chunk_size, total_size)
            
            start_page = i * pages_per_chunk + 1
            end_page = min(start_page + pages_per_chunk - 1, total_pages)
            
            chunks.append(ChunkMetadata(
                index=i,
                offset=start_offset,
                size=end_offset - start_offset,
                page_range=(start_page, end_page),
                checksum=""  # Se calculará al cargar el contenido
            ))
        
        return chunks

class ProgressiveLoader:
    """Cargador progresivo de documentos."""
    
    def __init__(
        self,
        chunker: DocumentChunker,
        cache_manager: Any  # DocumentCache
    ):
        self.chunker = chunker
        self.cache = cache_manager
    
    async def load_document_metadata(
        self,
        doc_id: str,
        drive_service: Any
    ) -> Dict[str, Any]:
        """Cargar metadatos del documento.
        
        Args:
            doc_id: ID del documento
            drive_service: Servicio de Google Drive
            
        Returns:
            Dict con metadatos
        """
        # Intentar obtener de caché
        cached = await self.cache.get_document(doc_id)
        if cached:
            return cached
        
        # Obtener de Google Drive
        metadata = await drive_service.get_file_metadata(doc_id)
        
        # Calcular chunks
        chunks = self.chunker.calculate_chunks(
            total_size=metadata['size'],
            total_pages=metadata['pageCount']
        )
        
        # Preparar metadatos
        doc_metadata = {
            'id': doc_id,
            'name': metadata['name'],
            'mimeType': metadata['mimeType'],
            'size': metadata['size'],
            'pageCount': metadata['pageCount'],
            'chunks': [vars(chunk) for chunk in chunks],
            'lastModified': metadata['modifiedTime']
        }
        
        # Guardar en caché
        await self.cache.set_document(doc_id, doc_metadata)
        return doc_metadata
    
    async def load_chunk(
        self,
        doc_id: str,
        chunk: ChunkMetadata,
        drive_service: Any
    ) -> str:
        """Cargar un chunk específico.
        
        Args:
            doc_id: ID del documento
            chunk: Metadatos del chunk
            drive_service: Servicio de Google Drive
            
        Returns:
            Contenido del chunk
        """
        # Intentar obtener de caché
        cached = await self.cache.get_chunk(doc_id, chunk.index)
        if cached:
            return cached
        
        # Cargar de Google Drive
        content = await drive_service.download_file_range(
            file_id=doc_id,
            start=chunk.offset,
            end=chunk.offset + chunk.size
        )
        
        # Guardar en caché
        await self.cache.set_chunk(doc_id, chunk.index, content)
        return content
    
    async def load_pages(
        self,
        doc_id: str,
        start_page: int,
        end_page: int,
        drive_service: Any
    ) -> Generator[str, None, None]:
        """Cargar rango de páginas de forma progresiva.
        
        Args:
            doc_id: ID del documento
            start_page: Página inicial
            end_page: Página final
            drive_service: Servicio de Google Drive
            
        Yields:
            Contenido de cada chunk necesario
        """
        # Cargar metadatos
        metadata = await self.load_document_metadata(doc_id, drive_service)
        
        # Identificar chunks necesarios
        needed_chunks = [
            ChunkMetadata(**chunk)
            for chunk in metadata['chunks']
            if (
                chunk['page_range'][0] <= end_page
                and chunk['page_range'][1] >= start_page
            )
        ]
        
        # Cargar chunks en paralelo con límite de concurrencia
        semaphore = asyncio.Semaphore(self.chunker.max_concurrent_chunks)
        
        async def load_chunk_with_semaphore(chunk: ChunkMetadata):
            async with semaphore:
                return await self.load_chunk(doc_id, chunk, drive_service)
        
        tasks = [
            load_chunk_with_semaphore(chunk)
            for chunk in needed_chunks
        ]
        
        for chunk_content in asyncio.as_completed(tasks):
            yield await chunk_content
    
    async def prefetch_next_chunk(
        self,
        doc_id: str,
        current_chunk: int,
        drive_service: Any
    ) -> None:
        """Precargar siguiente chunk en segundo plano.
        
        Args:
            doc_id: ID del documento
            current_chunk: Índice del chunk actual
            drive_service: Servicio de Google Drive
        """
        metadata = await self.load_document_metadata(doc_id, drive_service)
        if current_chunk + 1 < len(metadata['chunks']):
            next_chunk = ChunkMetadata(**metadata['chunks'][current_chunk + 1])
            asyncio.create_task(
                self.load_chunk(doc_id, next_chunk, drive_service)
            )
