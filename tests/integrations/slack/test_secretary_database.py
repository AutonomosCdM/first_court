import pytest
import uuid
from datetime import datetime

from AgentCourt.EMDB.db import db as DatabaseManager

@pytest.fixture
def database_manager():
    """Create a test database manager for the secretary"""
    return DatabaseManager(agent_name="test_secretary")

def test_case_creation(database_manager):
    """Test case creation and database storage"""
    # Prepare case metadata
    case_id = f"2025-{str(uuid.uuid4())[:3]}"
    case_description = "Test case for database integration"
    
    case_metadata = {
        "id": str(uuid.uuid4()),
        "case_number": case_id,
        "description": case_description,
        "created_at": datetime.now().isoformat(),
        "status": "En Proceso"
    }
    
    # Store case in database
    database_manager.add_to_case(
        id=case_metadata["id"], 
        document=f"Caso {case_id}: {case_description}",
        metadata=case_metadata
    )
    
    # Query the case
    query_result = database_manager.query_case(f"Find case {case_id}")
    
    # Assertions
    assert query_result is not None
    assert case_id in query_result

def test_document_tracking(database_manager):
    """Test document metadata storage"""
    # Prepare document metadata
    case_id = f"2025-{str(uuid.uuid4())[:3]}"
    doc_metadata = {
        "id": str(uuid.uuid4()),
        "filename": "test_document.pdf",
        "filetype": "pdf",
        "size": 1024,
        "case_number": case_id,
        "uploaded_at": datetime.now().isoformat()
    }
    
    # Store document in database
    database_manager.add_to_case(
        id=doc_metadata["id"],
        document=f"Documento {doc_metadata['filename']} para caso {case_id}",
        metadata=doc_metadata
    )
    
    # Query document metadata
    query_result = database_manager.query_case(f"Find document for case {case_id}")
    
    # Debug print
    print(f"Document Query Result: {query_result}")
    print(f"Expected Filename: {doc_metadata['filename']}")
    
    # Assertions
    assert query_result is not None
    assert doc_metadata['filename'] in query_result, f"Filename not found in query result: {query_result}"

def test_hearing_scheduling(database_manager):
    """Test hearing scheduling and database storage"""
    # Prepare hearing metadata
    case_id = f"2025-{str(uuid.uuid4())[:3]}"
    hearing_date = "2025-03-15"
    
    hearing_metadata = {
        "id": str(uuid.uuid4()),
        "case_number": case_id,
        "hearing_date": hearing_date,
        "scheduled_at": datetime.now().isoformat()
    }
    
    # Store hearing information
    database_manager.add_to_case(
        id=hearing_metadata["id"],
        document=f"Audiencia programada para {case_id} el {hearing_date}",
        metadata=hearing_metadata
    )
    
    # Query hearing information
    query_result = database_manager.query_case(f"Find hearing for case {case_id}")
    
    # Debug print
    print(f"Hearing Query Result: {query_result}")
    print(f"Expected Hearing Date: {hearing_date}")
    
    # Assertions
    assert query_result is not None
    assert hearing_date in query_result, f"Hearing date not found in query result: {query_result}"

def test_multiple_case_interactions(database_manager):
    """Test multiple interactions with the same case"""
    # Create initial case
    case_id = f"2025-{str(uuid.uuid4())[:3]}"
    
    # Case creation
    case_metadata = {
        "id": str(uuid.uuid4()),
        "case_number": case_id,
        "description": "Multiinteraction test case",
        "created_at": datetime.now().isoformat(),
        "status": "En Proceso"
    }
    database_manager.add_to_case(
        id=case_metadata["id"], 
        document=f"Caso {case_id}: Multiinteraction test",
        metadata=case_metadata
    )
    
    # Add document
    doc_metadata = {
        "id": str(uuid.uuid4()),
        "filename": "multiinteraction_doc.pdf",
        "case_number": case_id,
        "uploaded_at": datetime.now().isoformat()
    }
    database_manager.add_to_case(
        id=doc_metadata["id"],
        document=f"Documento {doc_metadata['filename']} para caso {case_id}",
        metadata=doc_metadata
    )
    
    # Schedule hearing
    hearing_metadata = {
        "id": str(uuid.uuid4()),
        "case_number": case_id,
        "hearing_date": "2025-04-01",
        "scheduled_at": datetime.now().isoformat()
    }
    database_manager.add_to_case(
        id=hearing_metadata["id"],
        document=f"Audiencia para caso {case_id} el {hearing_metadata['hearing_date']}",
        metadata=hearing_metadata
    )
    
    # Query case with multiple interactions
    case_query = database_manager.query_case(f"Find case {case_id}")
    
    # Debug print
    print(f"Multiple Interactions Query Result: {case_query}")
    print(f"Expected Document: {doc_metadata['filename']}")
    print(f"Expected Hearing Date: {hearing_metadata['hearing_date']}")
    
    # Assertions
    assert case_query is not None, "Case query returned None"
    assert case_id in case_query, f"Case ID {case_id} not found in query result"
    
    # Check for document and hearing information more flexibly
    assert any(doc_metadata['filename'] in doc for doc in [case_query]), f"Document not found in case query: {case_query}"
    assert any(hearing_metadata['hearing_date'] in doc for doc in [case_query]), f"Hearing date not found in case query: {case_query}"

def test_database_query_behavior(database_manager):
    """Investigate database query behavior"""
    # Create multiple documents for the same case
    case_id = f"2025-{str(uuid.uuid4())[:3]}"
    
    # Add multiple documents
    documents = [
        {
            "id": str(uuid.uuid4()),
            "filename": f"document_{i}.pdf",
            "case_number": case_id,
            "uploaded_at": datetime.now().isoformat()
        } for i in range(3)
    ]
    
    for doc_metadata in documents:
        database_manager.add_to_case(
            id=doc_metadata["id"],
            document=f"Documento {doc_metadata['filename']} para caso {case_id}",
            metadata=doc_metadata
        )
    
    # Query case
    case_query = database_manager.query_case(f"Find case {case_id}")
    
    # Debug print
    print(f"Multiple Documents Query Result: {case_query}")
    
    # Assertions to understand query behavior
    assert case_query is not None, "Case query returned None"
    
    # Check if all document names are in the query result
    for doc_metadata in documents:
        assert any(doc_metadata['filename'] in doc for doc in [case_query]), \
            f"Document {doc_metadata['filename']} not found in case query: {case_query}"
