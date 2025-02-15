"""Tests para el sistema de caché de documentos."""
import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json
import zlib

from src.cache.document_cache import DocumentCache

@pytest.fixture
def redis_mock():
    """Mock de cliente Redis."""
    return Mock()

@pytest.fixture
def document_cache(redis_mock):
    """Fixture para DocumentCache."""
    with patch('redis.from_url', return_value=redis_mock):
        cache = DocumentCache()
        cache.redis = redis_mock
        return cache

@pytest.mark.asyncio
async def test_get_document_from_cache(document_cache, redis_mock):
    """Test obtener documento desde caché."""
    # Preparar
    doc_id = "test_doc_1"
    test_data = {
        "id": doc_id,
        "name": "Test Document",
        "content": "Test Content"
    }
    compressed = zlib.compress(json.dumps(test_data).encode())
    redis_mock.get.return_value = compressed
    
    # Ejecutar
    result = await document_cache.get_document(doc_id)
    
    # Verificar
    assert result == test_data
    redis_mock.get.assert_called_once_with(
        document_cache._get_cache_key("doc", doc_id)
    )

@pytest.mark.asyncio
async def test_set_document_with_compression(document_cache, redis_mock):
    """Test guardar documento con compresión."""
    # Preparar
    doc_id = "test_doc_2"
    test_data = {
        "id": doc_id,
        "name": "Large Document",
        "content": "x" * 2000  # Forzar compresión
    }
    
    # Ejecutar
    await document_cache.set_document(doc_id, test_data)
    
    # Verificar
    redis_mock.set.assert_called_once()
    call_args = redis_mock.set.call_args[0]
    assert call_args[0] == document_cache._get_cache_key("doc", doc_id)
    assert len(call_args[1]) < len(json.dumps(test_data))  # Verificar compresión

@pytest.mark.asyncio
async def test_get_chunk(document_cache, redis_mock):
    """Test obtener chunk de documento."""
    # Preparar
    doc_id = "test_doc_3"
    chunk_index = 1
    test_content = "Chunk content"
    compressed = zlib.compress(test_content.encode())
    redis_mock.get.return_value = compressed
    
    # Ejecutar
    result = await document_cache.get_chunk(doc_id, chunk_index)
    
    # Verificar
    assert result == test_content
    redis_mock.get.assert_called_once_with(
        document_cache._get_cache_key(f"chunk:{doc_id}", str(chunk_index))
    )

@pytest.mark.asyncio
async def test_invalidate_document(document_cache, redis_mock):
    """Test invalidar documento y sus chunks."""
    # Preparar
    doc_id = "test_doc_4"
    redis_mock.keys.return_value = [
        f"firstcourt:docs:chunk:{doc_id}:1",
        f"firstcourt:docs:chunk:{doc_id}:2"
    ]
    
    # Ejecutar
    await document_cache.invalidate_document(doc_id)
    
    # Verificar
    redis_mock.delete.assert_called()
    assert redis_mock.delete.call_count == 2  # Documento y chunks

@pytest.mark.asyncio
async def test_compression_threshold(document_cache, redis_mock):
    """Test umbral de compresión."""
    # Preparar
    doc_id = "test_doc_5"
    
    # Datos pequeños (sin compresión)
    small_data = {"id": doc_id, "content": "small"}
    await document_cache.set_document(doc_id, small_data)
    small_call = redis_mock.set.call_args[0][1]
    
    # Datos grandes (con compresión)
    large_data = {"id": doc_id, "content": "x" * 2000}
    await document_cache.set_document(doc_id, large_data)
    large_call = redis_mock.set.call_args[0][1]
    
    # Verificar
    assert len(small_call) < document_cache.compression_threshold
    assert len(large_call) < len(json.dumps(large_data))

@pytest.mark.asyncio
async def test_cache_expiration(document_cache, redis_mock):
    """Test expiración de caché."""
    # Preparar
    doc_id = "test_doc_6"
    test_data = {"id": doc_id, "name": "Test"}
    custom_ttl = 3600  # 1 hora
    
    # Ejecutar
    await document_cache.set_document(doc_id, test_data, ttl=custom_ttl)
    
    # Verificar
    redis_mock.set.assert_called_once()
    assert redis_mock.set.call_args[1]["ex"] == custom_ttl

@pytest.mark.asyncio
async def test_concurrent_access(document_cache, redis_mock):
    """Test acceso concurrente."""
    # Preparar
    doc_ids = [f"test_doc_{i}" for i in range(10)]
    test_data = {"name": "Test"}
    
    # Ejecutar
    tasks = [
        document_cache.set_document(doc_id, test_data)
        for doc_id in doc_ids
    ]
    await asyncio.gather(*tasks)
    
    # Verificar
    assert redis_mock.set.call_count == len(doc_ids)
