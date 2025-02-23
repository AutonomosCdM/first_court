import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.agents.judge.judge_agent import JudgeAgent
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
def judge_agent(mock_logger, mock_database):
    """Create a judge agent instance"""
    return JudgeAgent(
        name="test_judge",
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

@pytest.fixture
def mock_case_data():
    """Create mock case data"""
    return {
        "case": {
            "id": "case-123",
            "case_number": "2025-001",
            "description": "Test case",
            "status": "En Proceso"
        },
        "documents": [
            {
                "id": "doc-1",
                "filename": "evidence.pdf",
                "filetype": "pdf",
                "size": 1024
            }
        ],
        "hearings": [
            {
                "id": "hearing-1",
                "hearing_date": "2025-03-15",
                "scheduled_at": "2025-02-20T12:00:00"
            }
        ]
    }

@pytest.mark.asyncio
async def test_initialization(judge_agent, mock_database):
    """Test agent initialization"""
    await judge_agent.initialize()
    
    # Verify database connection was checked
    mock_database.connection.assert_called_once()
    assert judge_agent.name == "test_judge"

@pytest.mark.asyncio
async def test_process_message_without_context(judge_agent):
    """Test processing message without context"""
    with pytest.raises(AgentError) as exc_info:
        await judge_agent.process_message({"text": "test"})
    
    assert "No context set for agent" in str(exc_info.value)
    assert exc_info.value.details["agent_type"] == "test_judge"

@pytest.mark.asyncio
async def test_case_review(judge_agent, agent_context, mock_database, mock_case_data):
    """Test case review handling"""
    judge_agent.set_context(agent_context)
    
    # Mock database response
    mock_database.get_case.return_value = mock_case_data
    
    message = {
        "type": "case_review",
        "text": "Review case",
        "user": "test_user"
    }
    
    response = await judge_agent.process_message(message)
    
    assert "Revisión completada" in response["text"]
    assert response["channel"] == agent_context.channel_id
    assert response["thread_ts"] == agent_context.thread_ts
    mock_database.get_case.assert_called_once_with(agent_context.case_id)

@pytest.mark.asyncio
async def test_decision_request(judge_agent, agent_context, mock_database, mock_case_data):
    """Test decision request handling"""
    judge_agent.set_context(agent_context)
    
    # Mock database response
    mock_database.get_case.return_value = mock_case_data
    
    message = {
        "type": "decision_request",
        "text": "Request decision",
        "user": "test_user"
    }
    
    response = await judge_agent.process_message(message)
    
    assert "Decisión:" in response["text"]
    assert response["metadata"]["case_id"] == agent_context.case_id
    mock_database.get_case.assert_called_once_with(agent_context.case_id)

@pytest.mark.asyncio
async def test_hearing_review(judge_agent, agent_context, mock_database, mock_case_data):
    """Test hearing review handling"""
    judge_agent.set_context(agent_context)
    
    # Mock database response
    mock_database.get_case.return_value = mock_case_data
    
    message = {
        "type": "hearing_review",
        "text": "Review hearing",
        "user": "test_user"
    }
    
    response = await judge_agent.process_message(message)
    
    assert "Revisión de audiencia:" in response["text"]
    assert response["metadata"]["case_id"] == agent_context.case_id
    mock_database.get_case.assert_called_once_with(agent_context.case_id)

@pytest.mark.asyncio
async def test_unknown_message_type(judge_agent, agent_context):
    """Test handling of unknown message type"""
    judge_agent.set_context(agent_context)
    
    message = {
        "type": "unknown_type",
        "text": "test",
        "user": "test_user"
    }
    
    response = await judge_agent.process_message(message)
    
    assert response == {}  # Should return empty dict for unknown types

@pytest.mark.asyncio
async def test_error_handling(judge_agent, agent_context, mock_database):
    """Test error handling during message processing"""
    judge_agent.set_context(agent_context)
    
    # Simulate database error
    mock_database.get_case.side_effect = Exception("Database error")
    
    message = {
        "type": "case_review",
        "text": "Review case",
        "user": "test_user"
    }
    
    response = await judge_agent.process_message(message)
    
    assert "Error: Database error" in response["text"]
    assert response["metadata"]["error_type"] == "Exception"

@pytest.mark.asyncio
async def test_case_review_without_case_context(judge_agent, agent_context):
    """Test case review without case context"""
    # Set context without case_id
    context = AgentContext(
        user_id=agent_context.user_id,
        channel_id=agent_context.channel_id
    )
    judge_agent.set_context(context)
    
    message = {
        "type": "case_review",
        "text": "Review case",
        "user": "test_user"
    }
    
    with pytest.raises(AgentError) as exc_info:
        await judge_agent.process_message(message)
    
    assert "No case context for review" in str(exc_info.value)

@pytest.mark.asyncio
async def test_case_not_found(judge_agent, agent_context, mock_database):
    """Test handling when case is not found"""
    judge_agent.set_context(agent_context)
    
    # Mock database to return None for case
    mock_database.get_case.return_value = None
    
    message = {
        "type": "case_review",
        "text": "Review case",
        "user": "test_user"
    }
    
    with pytest.raises(AgentError) as exc_info:
        await judge_agent.process_message(message)
    
    assert "Case not found" in str(exc_info.value)
    assert exc_info.value.details["case_id"] == agent_context.case_id
