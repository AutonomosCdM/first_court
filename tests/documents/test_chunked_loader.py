"""Tests para el sistema de carga progresiva."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from math import ceil
from datetime import datetime, UTC

from src.documents.chunked_loader import (
    DocumentChunker,
    ProgressiveLoader,
    ChunkMetadata
)

@pytest.fixture
def cache_mock():
    """Mock del caché."""
    return AsyncMock()

@pytest.fixture
def drive_service_mock():
    """Mock del servicio de Google Drive."""
    return AsyncMock()

@pytest.fixture
def chunker():
    """Fixture para DocumentChunker."""
    return DocumentChunker(
        chunk_size=1024,  # 1KB para tests
        max_concurrent_chunks=2
    )

@pytest.fixture
def loader(chunker, cache_mock):
    """Fixture para ProgressiveLoader."""
    return ProgressiveLoader(chunker, cache_mock)

def test_calculate_chunks(chunker):
    """Test cálculo de chunks."""
    # Preparar
    total_size = 4096  # 4KB
    total_pages = 10
    
    # Ejecutar
    chunks = chunker.calculate_chunks(total_size, total_pages)
    
    # Verificar
    assert len(chunks) == 4  # 4KB / 1KB
    assert all(isinstance(chunk, ChunkMetadata) for chunk in chunks)
    assert chunks[0].offset == 0
    assert chunks[0].size == 1024
    assert chunks[0].page_range == (1, 3)  # 10 páginas / 4 chunks ≈ 3 páginas/chunk

@pytest.mark.asyncio
async def test_load_document_metadata(loader, cache_mock, drive_service_mock):
    """Test carga de metadatos."""
    # Preparar
    doc_id = "test_doc_1"
    test_metadata = {
        "id": doc_id,
        "name": "Test Document",
        "size": 2048,
        "pageCount": 5,
        "mimeType": "application/pdf",
        "modifiedTime": "2025-02-15T00:00:00Z"
    }
    drive_service_mock.get_file_metadata = AsyncMock(return_value=test_metadata)
    cache_mock.get_document = AsyncMock(return_value=None)
    
    # Ejecutar
    metadata = await loader.load_document_metadata(doc_id, drive_service_mock)
    
    # Verificar
    assert metadata["id"] == doc_id
    assert len(metadata["chunks"]) == 2  # 2048 / 1024
    assert all(isinstance(chunk, dict) for chunk in metadata["chunks"])

@pytest.mark.asyncio
async def test_load_chunk_from_cache(loader, cache_mock, drive_service_mock):
    """Test carga de chunk desde caché."""
    # Preparar
    doc_id = "test_doc_2"
    chunk = ChunkMetadata(
        index=0,
        offset=0,
        size=1024,
        page_range=(1, 3),
        checksum=""
    )
    cached_content = "cached content"
    cache_mock.get_chunk.return_value = cached_content
    
    # Ejecutar
    content = await loader.load_chunk(doc_id, chunk, drive_service_mock)
    
    # Verificar
    assert content == cached_content
    drive_service_mock.download_file_range.assert_not_called()

@pytest.mark.asyncio
async def test_load_chunk_from_drive(loader, cache_mock, drive_service_mock):
    """Test carga de chunk desde Drive."""
    # Preparar
    doc_id = "test_doc_3"
    chunk = ChunkMetadata(
        index=0,
        offset=0,
        size=1024,
        page_range=(1, 3),
        checksum=""
    )
    cache_mock.get_chunk.return_value = None
    drive_content = "drive content"
    drive_service_mock.download_file_range.return_value = drive_content
    
    # Ejecutar
    content = await loader.load_chunk(doc_id, chunk, drive_service_mock)
    
    # Verificar
    assert content == drive_content
    drive_service_mock.download_file_range.assert_called_once_with(
        file_id=doc_id,
        start=0,
        end=1024
    )
    cache_mock.set_chunk.assert_called_once_with(
        doc_id,
        0,
        drive_content
    )

@pytest.mark.asyncio
async def test_load_pages_concurrently(loader, cache_mock, drive_service_mock):
    """Test carga concurrente de páginas."""
    # Preparar
    doc_id = "test_doc_4"
    test_metadata = {
        "id": doc_id,
        "name": "Test Document 4",
        "mimeType": "application/pdf",
        "size": 3072,  # 3KB
        "pageCount": 6,
        "modifiedTime": datetime.now(UTC).isoformat()
    }
    drive_service_mock.get_file_metadata = AsyncMock(return_value=test_metadata)
    cache_mock.get_document = AsyncMock(return_value=None)
    
    # Simular contenido de chunks
    async def mock_load_chunk(doc_id, chunk, service):
        return f"content_{chunk.index}"
    
    with patch.object(loader, 'load_chunk', mock_load_chunk):
        # Ejecutar
        chunks = []
        async for chunk in loader.load_pages(doc_id, 1, 6, drive_service_mock):
            chunks.append(chunk)
        
        # Verificar
        assert len(chunks) == 3  # 3KB / 1KB
        assert all(isinstance(chunk, str) and chunk.startswith("content_") for chunk in chunks)

@pytest.mark.asyncio
async def test_prefetch_next_chunk(loader, cache_mock, drive_service_mock):
    """Test precarga del siguiente chunk."""
    # Preparar
    doc_id = "test_doc_5"
    test_metadata = {
        "id": doc_id,
        "name": "Test Document 5",
        "mimeType": "application/pdf",
        "size": 2048,
        "pageCount": 4,
        "modifiedTime": datetime.now(UTC).isoformat()
    }
    drive_service_mock.get_file_metadata = AsyncMock(return_value=test_metadata)
    cache_mock.get_document = AsyncMock(return_value=None)
    
    # Ejecutar
    await loader.prefetch_next_chunk(doc_id, 0, drive_service_mock)
    
    # Verificar
    drive_service_mock.get_file_metadata.assert_awaited_once()

@pytest.mark.asyncio
async def test_concurrent_chunk_limit(loader, cache_mock, drive_service_mock):
    """Test límite de chunks concurrentes."""
    # Preparar
    doc_id = "test_doc_6"
    test_metadata = {
        "id": doc_id,
        "name": "Test Document 6",
        "mimeType": "application/pdf",
        "size": 4096,  # 4KB
        "pageCount": 8,
        "modifiedTime": datetime.now(UTC).isoformat()
    }
    drive_service_mock.get_file_metadata = AsyncMock(return_value=test_metadata)
    cache_mock.get_document = AsyncMock(return_value=None)
    
    # Simular carga lenta de chunks
    async def slow_load_chunk(doc_id, chunk, service):
        await asyncio.sleep(0.1)
        return f"content_{chunk.index}"
    
    with patch.object(loader, 'load_chunk', slow_load_chunk):
        # Ejecutar
        start_time = asyncio.get_event_loop().time()
        chunks = []
        async for chunk in loader.load_pages(doc_id, 1, 8, drive_service_mock):
            chunks.append(chunk)
        end_time = asyncio.get_event_loop().time()
        
        # Verificar
        assert len(chunks) == 4  # 4KB / 1KB
        # Con 2 chunks concurrentes, debería tomar al menos 0.2s (2 rondas de 0.1s)
        assert end_time - start_time >= 0.2
