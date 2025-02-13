"""
Tests para la integración con Elasticsearch
"""
import pytest
from datetime import datetime
from src.integrations.database.elasticsearch_client import ElasticsearchClient

@pytest.fixture
def es_client():
    """Fixture para crear un cliente de Elasticsearch de prueba"""
    client = ElasticsearchClient(
        index_prefix="test_first_court"
    )
    # Crear índices de prueba
    client.create_indices()
    yield client
    # Limpiar índices después de las pruebas
    for index in ["cases", "documents"]:
        index_name = f"{client.index_prefix}_{index}"
        if client.client.indices.exists(index=index_name):
            client.client.indices.delete(index=index_name)

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
    # Indexar algunos casos de prueba
    cases = [
        {
            "case_number": "2025-TEST-002",
            "title": "Caso de Prueba Especial",
            "description": "Este caso contiene palabras clave específicas",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "case_number": "2025-TEST-003",
            "title": "Otro Caso",
            "description": "Este caso no contiene las palabras clave",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    for case in cases:
        es_client.index_document("cases", case, case["case_number"])
    
    # Forzar refresh
    es_client.client.indices.refresh(index=f"{es_client.index_prefix}_cases")
    
    # Buscar casos
    results = es_client.search_documents("Especial", "cases")
    assert results["hits"]["total"]["value"] >= 1
    assert any("Especial" in hit["_source"]["title"] 
              for hit in results["hits"]["hits"])

def test_search_with_filters(es_client):
    """Test para buscar con filtros"""
    # Indexar documentos con diferentes tipos
    documents = [
        {
            "case_id": "2025-TEST-001",
            "title": "Sentencia Final",
            "content": "Contenido de la sentencia",
            "document_type": "sentencia",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "case_id": "2025-TEST-001",
            "title": "Informe Pericial",
            "content": "Contenido del informe",
            "document_type": "informe",
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    for doc in documents:
        es_client.index_document("documents", doc)
    
    # Forzar refresh
    es_client.client.indices.refresh(index=f"{es_client.index_prefix}_documents")
    
    # Buscar solo sentencias
    results = es_client.search_documents(
        "Contenido",
        "documents",
        filters={"document_type": "sentencia"}
    )
    
    assert results["hits"]["total"]["value"] >= 1
    assert all(hit["_source"]["document_type"] == "sentencia" 
              for hit in results["hits"]["hits"])

def test_highlight_results(es_client):
    """Test para verificar highlighting en resultados"""
    # Indexar documento con contenido específico
    document = {
        "case_id": "2025-TEST-001",
        "title": "Documento con Términos Específicos",
        "content": "Este documento contiene términos específicos para buscar",
        "document_type": "documento",
        "created_at": datetime.utcnow().isoformat()
    }
    
    es_client.index_document("documents", document)
    
    # Forzar refresh
    es_client.client.indices.refresh(index=f"{es_client.index_prefix}_documents")
    
    # Buscar con término específico
    results = es_client.search_documents("términos específicos", "documents")
    
    assert results["hits"]["total"]["value"] >= 1
    assert "highlight" in results["hits"]["hits"][0]
