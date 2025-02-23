import pytest
import os
import uuid
from datetime import datetime, timedelta
from typing import Generator

from src.integrations.database.slack_db import SlackDatabase

@pytest.fixture
def test_db_path(tmp_path) -> Generator[str, None, None]:
    """Create a temporary database path for testing"""
    db_path = str(tmp_path / f"test_slack_db_{uuid.uuid4()}.sqlite")
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def slack_db(test_db_path) -> Generator[SlackDatabase, None, None]:
    """Create a temporary Slack database for testing"""
    database = SlackDatabase(test_db_path)
    yield database
    database.disconnect()

def test_create_case(slack_db: SlackDatabase):
    """Test creating a new case"""
    case_description = "Test case for Slack integration"
    case = slack_db.create_case(case_description)
    
    assert case["description"] == case_description
    assert "id" in case
    assert "case_number" in case
    assert case["status"] == "En Proceso"
    assert datetime.fromisoformat(case["created_at"])

def test_add_document(slack_db: SlackDatabase):
    """Test adding a document to a case"""
    # First create a case
    case = slack_db.create_case("Document test case")
    
    # Add a document
    doc = slack_db.add_document(
        case_id=case["id"],
        filename="test_document.pdf",
        filetype="pdf",
        size=1024
    )
    
    assert doc["filename"] == "test_document.pdf"
    assert doc["filetype"] == "pdf"
    assert doc["size"] == 1024
    assert doc["case_id"] == case["id"]
    assert datetime.fromisoformat(doc["uploaded_at"])

def test_schedule_hearing(slack_db: SlackDatabase):
    """Test scheduling a hearing for a case"""
    # First create a case
    case = slack_db.create_case("Hearing test case")
    
    # Schedule a hearing
    hearing_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    hearing = slack_db.schedule_hearing(
        case_id=case["id"],
        hearing_date=hearing_date
    )
    
    assert hearing["case_id"] == case["id"]
    assert hearing["hearing_date"] == hearing_date
    assert datetime.fromisoformat(hearing["scheduled_at"])

def test_get_case(slack_db: SlackDatabase):
    """Test retrieving a case with its documents and hearings"""
    # Create a case
    case = slack_db.create_case("Full case retrieval test")
    
    # Add a document
    doc = slack_db.add_document(
        case_id=case["id"],
        filename="document.pdf",
        filetype="pdf",
        size=2048
    )
    
    # Schedule a hearing
    hearing_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
    hearing = slack_db.schedule_hearing(
        case_id=case["id"],
        hearing_date=hearing_date
    )
    
    # Retrieve the case
    retrieved_case = slack_db.get_case(case["id"])
    
    assert retrieved_case is not None
    assert retrieved_case["case"]["id"] == case["id"]
    assert retrieved_case["case"]["description"] == "Full case retrieval test"
    
    # Check documents
    assert len(retrieved_case["documents"]) == 1
    assert retrieved_case["documents"][0]["filename"] == "document.pdf"
    
    # Check hearings
    assert len(retrieved_case["hearings"]) == 1
    assert retrieved_case["hearings"][0]["hearing_date"] == hearing_date

def test_multiple_cases_and_case_numbering(slack_db: SlackDatabase):
    """Test creating multiple cases and verifying case number generation"""
    year = datetime.now().year
    
    # Create multiple cases
    case1 = slack_db.create_case("First test case")
    case2 = slack_db.create_case("Second test case")
    
    # Verify case numbers
    assert case1["case_number"] == f"{year}-001"
    assert case2["case_number"] == f"{year}-002"
    
    # Verify unique IDs
    assert case1["id"] != case2["id"]

def test_case_not_found(slack_db: SlackDatabase):
    """Test retrieving a non-existent case"""
    non_existent_id = str(uuid.uuid4())
    result = slack_db.get_case(non_existent_id)
    assert result is None

def test_transaction_rollback_on_error(slack_db: SlackDatabase):
    """Test transaction rollback when an error occurs"""
    # Create initial case
    case = slack_db.create_case("Transaction test case")
    
    # Attempt to create an invalid document (should rollback)
    try:
        with slack_db.connection(), slack_db.transaction():
            # Add valid document
            slack_db.add_document(
                case_id=case["id"],
                filename="valid.pdf",
                filetype="pdf",
                size=1024
            )
            
            # Add invalid document (non-existent case_id)
            slack_db.add_document(
                case_id="invalid_id",
                filename="invalid.pdf",
                filetype="pdf",
                size=1024
            )
    except Exception:
        pass
    
    # Verify no documents were added (transaction rolled back)
    retrieved_case = slack_db.get_case(case["id"])
    assert len(retrieved_case["documents"]) == 0
