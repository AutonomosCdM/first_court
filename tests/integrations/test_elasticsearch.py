"""
Tests para la integración con Elasticsearch
"""
import pytest
from datetime import datetime
from src.integrations.database.elasticsearch_client import ElasticsearchClient

@pytest.fixture
def es_client(mocker):
    """Fixture para crear un cliente de Elasticsearch simulado"""
    mock_es = mocker.MagicMock()
    mock_indices = mocker.MagicMock()
    mock_es.indices = mock_indices
    
    def mock_index(index, document, id=None, **kwargs):
        return {'_id': id or 'test_id', 'result': 'created'}
    
    def mock_search(index, body, **kwargs):
        # Procesar filtros
        filters = body.get('query', {}).get('bool', {}).get('filter', [])
        doc_type = None
        for f in filters:
            if 'term' in f and 'document_type' in f['term']:
                doc_type = f['term']['document_type']
        
        # Procesar highlighting
        highlight = None
        if 'highlight' in body:
            highlight = {
                'description': ['<em>prueba</em> para Elasticsearch']
            }
        
        result = {
            'hits': {
                'total': {'value': 1},
                'hits': [{
                    '_id': '2025-TEST-001',
                    '_source': {
                        'title': 'Caso de Prueba',
                        'description': 'Este es un caso de prueba para Elasticsearch',
                        'document_type': doc_type or 'sentencia'
                    },
                    'highlight': highlight
                }]
            }
        }
        
        # Procesar el resultado para que coincida con el formato esperado
        hits = result['hits']['hits']
        return [{
            **hit['_source'],
            'id': hit['_id'],
            'highlight': hit.get('highlight')
        } for hit in hits]
    
    mock_es.index = mocker.MagicMock(side_effect=mock_index)
    mock_es.search = mocker.MagicMock(side_effect=mock_search)
    
    client = ElasticsearchClient(index_prefix="test_first_court")
    client.client = mock_es
    return client

def test_index_case(es_client):
    """Test para indexar un caso"""
    case = {
        "case_number": "2025-TEST-001",
        "title": "Caso de Prueba",
        "description": "Este es un caso de prueba para Elasticsearch",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    response = es_client.index_document("cases", case, "2025-TEST-001")
    assert response["_id"] == "2025-TEST-001"
    
    # Forzar refresh para que el documento esté disponible para búsqueda
    es_client.client.indices.refresh(index=f"{es_client.index_prefix}_cases")

def test_index_document(es_client):
    """Test para indexar un documento legal"""
    document = {
        "case_id": "2025-TEST-001",
        "title": "Sentencia de Prueba",
        "content": "Este es el contenido de una sentencia de prueba",
        "document_type": "sentencia",
        "created_at": datetime.utcnow().isoformat()
    }
    
    response = es_client.index_document("documents", document)
    assert response["_id"] is not None
    
    # Forzar refresh
    es_client.client.indices.refresh(index=f"{es_client.index_prefix}_documents")

def test_search_cases(es_client):
    """Test para buscar casos"""
    # Buscar casos
    results = es_client.search_documents("prueba", "cases")
    
    assert len(results) == 1
    assert results[0]['title'] == "Caso de Prueba"
    assert "prueba para Elasticsearch" in results[0]['description']

def test_search_with_filters(es_client):
    """Test para buscar con filtros"""
    # Buscar con filtros
    filters = {
        "document_type": "sentencia"
    }
    
    results = es_client.search_documents(
        "prueba",
        "documents",
        filters=filters
    )
    
    assert len(results) == 1
    assert results[0]['document_type'] == 'sentencia'

def test_highlight_results(es_client):
    """Test para verificar highlighting en resultados"""
    # Buscar con highlighting
    results = es_client.search_documents(
        "prueba",
        "documents",
        highlight_fields=["description"]
    )
    
    assert len(results) == 1
    assert 'highlight' in results[0]
    assert '<em>prueba</em>' in results[0]['highlight']['description'][0]
