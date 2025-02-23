import pytest
import os
import uuid
from datetime import datetime, timedelta

from src.integrations.slack.database import SlackDatabase

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    db_path = f'db/test_slack_database_{uuid.uuid4()}.sqlite'
    db = SlackDatabase(db_path)
    yield db
    db.close()
    os.unlink(db_path)

def test_create_case(temp_db):
    """Test creating a new case"""
    case_description = "Test case for Slack integration"
    case = temp_db.create_case(case_description)
    
    assert case['description'] == case_description
    assert 'id' in case
    assert 'case_number' in case
    assert case['status'] == "En Proceso"
    assert datetime.fromisoformat(case['created_at'])

def test_add_document(temp_db):
    """Test adding a document to a case"""
    # First create a case
    case = temp_db.create_case("Document test case")
    
    # Add a document
    doc = temp_db.add_document(
        case_id=case['id'], 
        filename="test_document.pdf", 
        filetype="pdf", 
        size=1024
    )
    
    assert doc['filename'] == "test_document.pdf"
    assert doc['filetype'] == "pdf"
    assert doc['size'] == 1024
    assert doc['case_id'] == case['id']
    assert datetime.fromisoformat(doc['uploaded_at'])

def test_schedule_hearing(temp_db):
    """Test scheduling a hearing for a case"""
    # First create a case
    case = temp_db.create_case("Hearing test case")
    
    # Schedule a hearing
    hearing_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    hearing = temp_db.schedule_hearing(
        case_id=case['id'], 
        hearing_date=hearing_date
    )
    
    assert hearing['case_id'] == case['id']
    assert hearing['hearing_date'] == hearing_date
    assert datetime.fromisoformat(hearing['scheduled_at'])

def test_get_case(temp_db):
    """Test retrieving a case with its documents and hearings"""
    # Create a case
    case = temp_db.create_case("Full case retrieval test")
    
    # Add a document
    doc = temp_db.add_document(
        case_id=case['id'], 
        filename="document.pdf", 
        filetype="pdf", 
        size=2048
    )
    
    # Schedule a hearing
    hearing_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
    hearing = temp_db.schedule_hearing(
        case_id=case['id'], 
        hearing_date=hearing_date
    )
    
    # Retrieve the case
    retrieved_case = temp_db.get_case(case['id'])
    
    assert retrieved_case is not None
    assert retrieved_case['case']['id'] == case['id']
    assert retrieved_case['case']['description'] == "Full case retrieval test"
    
    # Check documents
    assert len(retrieved_case['documents']) == 1
    assert retrieved_case['documents'][0]['filename'] == "document.pdf"
    
    # Check hearings
    assert len(retrieved_case['hearings']) == 1
    assert retrieved_case['hearings'][0]['hearing_date'] == hearing_date

def test_multiple_cases_and_case_numbering(temp_db):
    """Test creating multiple cases and verifying case number generation"""
    year = datetime.now().year
    
    # Create multiple cases
    case1 = temp_db.create_case("First test case")
    case2 = temp_db.create_case("Second test case")
    
    # Verify case numbers
    assert case1['case_number'] == f"{year}-001"
    assert case2['case_number'] == f"{year}-002"
    
    # Verify unique IDs
    assert case1['id'] != case2['id']
