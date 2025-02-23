import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.agents.secretary.secretary_agent import SecretaryAgent
from src.agents.base.agent import AgentContext
from src.agents.base.messaging import Message
from src.core.exceptions.base import AgentError
from src.integrations.database.slack_db import SlackDatabase

@pytest.fixture
def mock_logger():
    """Create a mock logger"""
    logger = Mock()
    logger.log_with_context = Mock()
    return logger

@pytest.fixture
def mock_database():
    """Create a mock database"""
    database = Mock(spec=SlackDatabase)
    database.connection = Mock()
    database.transaction = Mock()
    return database

@pytest.fixture
def secretary_agent(mock_logger, mock_database):
    """Create a secretary agent instance"""
    return SecretaryAgent(
        name="test_secretary",
        logger=mock_logger,
        database=mock_database
    )

@pytest.fixture
def agent_context():
    """Create an agent context"""
    return AgentContext(
        case_id="case-123",
        user_id="user-456",
        channel_id="channel-789",
        thread_ts="1234567890.123456"
    )

@pytest.mark.asyncio
async def test_initialization(secretary_agent, mock_database):
    """Test agent initialization"""
    await secretary_agent.initialize()
    
    # Verify database connection was checked
    mock_database.connection.assert_called_once()
    assert secretary_agent.name == "test_secretary"

@pytest.mark.asyncio
async def test_process_message_without_context(secretary_agent):
    """Test processing message without context"""
    with pytest.raises(AgentError) as exc_info:
        await secretary_agent.process_message({"text": "test"})
    
    assert "No context set for agent" in str(exc_info.value)
    assert exc_info.value.details["agent_type"] == "test_secretary"

@pytest.mark.asyncio
async def test_case_creation(secretary_agent, agent_context, mock_database):
    """Test case creation handling"""
    secretary_agent.set_context(agent_context)
    
    # Mock database response
    mock_database.create_case.return_value = {
        "case_number": "2025-001",
        "description": "Test case"
    }
    
    message = {
        "type": "case_creation",
        "text": "Test case",
        "user": "test_user"
    }
    
    response = await secretary_agent.process_message(message)
    
    assert "Caso creado: 2025-001" in response["text"]
    assert response["channel"] == agent_context.channel_id
    assert response["thread_ts"] == agent_context.thread_ts
    mock_database.create_case.assert_called_once_with("Test case")

@pytest.mark.asyncio
async def test_document_upload(secretary_agent, agent_context, mock_database):
    """Test document upload handling"""
    secretary_agent.set_context(agent_context)
    
    # Mock database response
    mock_database.add_document.return_value = {
        "filename": "test.pdf",
        "filetype": "pdf",
        "size": 1024
    }
    
    message = {
        "type": "document_upload",
        "text": "Upload document",
        "user": "test_user",
        "filename": "test.pdf",
        "filetype": "pdf",
        "size": 1024
    }
    
    response = await secretary_agent.process_message(message)
    
    assert "Documento agregado: test.pdf" in response["text"]
    mock_database.add_document.assert_called_once_with(
        case_id=agent_context.case_id,
        filename="test.pdf",
        filetype="pdf",
        size=1024
    )

@pytest.mark.asyncio
async def test_hearing_schedule(secretary_agent, agent_context, mock_database):
    """Test hearing schedule handling"""
    secretary_agent.set_context(agent_context)
    
    hearing_date = "2025-03-15"
    mock_database.schedule_hearing.return_value = {
        "hearing_date": hearing_date
    }
    
    message = {
        "type": "hearing_schedule",
        "text": hearing_date,
        "user": "test_user"
    }
    
    response = await secretary_agent.process_message(message)
    
    assert f"Audiencia programada para: {hearing_date}" in response["text"]
    mock_database.schedule_hearing.assert_called_once_with(
        case_id=agent_context.case_id,
        hearing_date=hearing_date
    )

@pytest.mark.asyncio
async def test_unknown_message_type(secretary_agent, agent_context):
    """Test handling of unknown message type"""
    secretary_agent.set_context(agent_context)
    
    message = {
        "type": "unknown_type",
        "text": "test",
        "user": "test_user"
    }
    
    response = await secretary_agent.process_message(message)
    
    assert response == {}  # Should return empty dict for unknown types

@pytest.mark.asyncio
async def test_error_handling(secretary_agent, agent_context, mock_database):
    """Test error handling during message processing"""
    secretary_agent.set_context(agent_context)
    
    # Simulate database error
    mock_database.create_case.side_effect = Exception("Database error")
    
    message = {
        "type": "case_creation",
        "text": "Test case",
        "user": "test_user"
    }
    
    response = await secretary_agent.process_message(message)
    
    assert "Error: Database error" in response["text"]
    assert response["metadata"]["error_type"] == "Exception"

@pytest.mark.asyncio
async def test_document_upload_without_case_context(secretary_agent, agent_context):
    """Test document upload without case context"""
    # Set context without case_id
    context = AgentContext(
        user_id=agent_context.user_id,
        channel_id=agent_context.channel_id
    )
    secretary_agent.set_context(context)
    
    message = {
        "type": "document_upload",
        "text": "Upload document",
        "user": "test_user",
        "filename": "test.pdf",
        "filetype": "pdf",
        "size": 1024
    }
    
    with pytest.raises(AgentError) as exc_info:
        await secretary_agent.process_message(message)
    
    assert "No case context for document upload" in str(exc_info.value)

@pytest.mark.asyncio
async def test_hearing_schedule_without_case_context(secretary_agent, agent_context):
    """Test hearing schedule without case context"""
    # Set context without case_id
    context = AgentContext(
        user_id=agent_context.user_id,
        channel_id=agent_context.channel_id
    )
    secretary_agent.set_context(context)
    
    message = {
        "type": "hearing_schedule",
        "text": "2025-03-15",
        "user": "test_user"
    }
    
    with pytest.raises(AgentError) as exc_info:
        await secretary_agent.process_message(message)
    
    assert "No case context for hearing schedule" in str(exc_info.value)
