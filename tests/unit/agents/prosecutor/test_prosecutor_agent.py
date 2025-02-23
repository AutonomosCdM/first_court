import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.agents.prosecutor.prosecutor_agent import ProsecutorAgent
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
def prosecutor_agent(mock_logger, mock_database):
    """Create a prosecutor agent instance"""
    return ProsecutorAgent(
        name="test_prosecutor",
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
async def test_initialization(prosecutor_agent, mock_database):
    """Test agent initialization"""
    await prosecutor_agent.initialize()
    
    # Verify database connection was checked
    mock_database.connection.assert_called_once()
    assert prosecutor_agent.name == "test_prosecutor"

@pytest.mark.asyncio
async def test_process_message_without_context(prosecutor_agent):
    """Test processing message without context"""
    with pytest.raises(AgentError) as exc_info:
        await prosecutor_agent.process_message({"text": "test"})
    
    assert "No context set for agent" in str(exc_info.value)
    assert exc_info.value.details["agent_type"] == "test_prosecutor"

@pytest.mark.asyncio
async def test_case_analysis(prosecutor_agent, agent_context, mock_database, mock_case_data):
    """Test case analysis handling"""
    prosecutor_agent.set_context(agent_context)
    
    # Mock database response
    mock_database.get_case.return_value = mock_case_data
    
    message = {
        "type": "case_analysis",
        "text": "Analyze case",
        "user": "test_user"
    }
    
    response = await prosecutor_agent.process_message(message)
    
    assert "Análisis completado" in response["text"]
    assert response["channel"] == agent_context.channel_id
    assert response["thread_ts"] == agent_context.thread_ts
    mock_database.get_case.assert_called_once_with(agent_context.case_id)

@pytest.mark.asyncio
async def test_argument_request(prosecutor_agent, agent_context, mock_database, mock_case_data):
    """Test argument generation handling"""
    prosecutor_agent.set_context(agent_context)
    
    # Mock database response
    mock_database.get_case.return_value = mock_case_data
    
    message = {
        "type": "argument_request",
        "text": "Generate arguments",
        "user": "test_user"
    }
    
    response = await prosecutor_agent.process_message(message)
    
    assert "Argumentos generados" in response["text"]
    assert response["metadata"]["case_id"] == agent_context.case_id
    mock_database.get_case.assert_called_once_with(agent_context.case_id)

@pytest.mark.asyncio
async def test_evidence_review(prosecutor_agent, agent_context, mock_database, mock_case_data):
    """Test evidence review handling"""
    prosecutor_agent.set_context(agent_context)
    
    # Mock database response
    mock_database.get_case.return_value = mock_case_data
    
    message = {
        "type": "evidence_review",
        "text": "Review evidence",
        "user": "test_user"
    }
    
    response = await prosecutor_agent.process_message(message)
    
    assert "Revisión de evidencia" in response["text"]
    assert response["metadata"]["case_id"] == agent_context.case_id
    mock_database.get_case.assert_called_once_with(agent_context.case_id)

@pytest.mark.asyncio
async def test_unknown_message_type(prosecutor_agent, agent_context):
    """Test handling of unknown message type"""
    prosecutor_agent.set_context(agent_context)
    
    message = {
        "type": "unknown_type",
        "text": "test",
        "user": "test_user"
    }
    
    response = await prosecutor_agent.process_message(message)
    
    assert response == {}  # Should return empty dict for unknown types

@pytest.mark.asyncio
async def test_error_handling(prosecutor_agent, agent_context, mock_database):
    """Test error handling during message processing"""
    prosecutor_agent.set_context(agent_context)
    
    # Simulate database error
    mock_database.get_case.side_effect = Exception("Database error")
    
    message = {
        "type": "case_analysis",
        "text": "Analyze case",
        "user": "test_user"
    }
    
    response = await prosecutor_agent.process_message(message)
    
    assert "Error: Database error" in response["text"]
    assert response["metadata"]["error_type"] == "Exception"

@pytest.mark.asyncio
async def test_case_analysis_without_case_context(prosecutor_agent, agent_context):
    """Test case analysis without case context"""
    # Set context without case_id
    context = AgentContext(
        user_id=agent_context.user_id,
        channel_id=agent_context.channel_id
    )
    prosecutor_agent.set_context(context)
    
    message = {
        "type": "case_analysis",
        "text": "Analyze case",
        "user": "test_user"
    }
    
    with pytest.raises(AgentError) as exc_info:
        await prosecutor_agent.process_message(message)
    
    assert "No case context for analysis" in str(exc_info.value)

@pytest.mark.asyncio
async def test_case_not_found(prosecutor_agent, agent_context, mock_database):
    """Test handling when case is not found"""
    prosecutor_agent.set_context(agent_context)
    
    # Mock database to return None for case
    mock_database.get_case.return_value = None
    
    message = {
        "type": "case_analysis",
        "text": "Analyze case",
        "user": "test_user"
    }
    
    with pytest.raises(AgentError) as exc_info:
        await prosecutor_agent.process_message(message)
    
    assert "Case not found" in str(exc_info.value)
    assert exc_info.value.details["case_id"] == agent_context.case_id

@pytest.mark.asyncio
async def test_evidence_review_without_case_context(prosecutor_agent, agent_context):
    """Test evidence review without case context"""
    # Set context without case_id
    context = AgentContext(
        user_id=agent_context.user_id,
        channel_id=agent_context.channel_id
    )
    prosecutor_agent.set_context(context)
    
    message = {
        "type": "evidence_review",
        "text": "Review evidence",
        "user": "test_user"
    }
    
    with pytest.raises(AgentError) as exc_info:
        await prosecutor_agent.process_message(message)
    
    assert "No case context for evidence review" in str(exc_info.value)
