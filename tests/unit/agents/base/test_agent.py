import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from src.agents.base.agent import BaseAgent, AgentContext
from src.core.logging.logger import Logger
from src.core.exceptions.base import AgentError

class TestAgent(BaseAgent):
    """Test implementation of BaseAgent"""
    
    def __init__(self, name: str, logger: Logger):
        super().__init__(name, logger)
        self.initialize_called = False
        self.cleanup_called = False
    
    async def initialize(self):
        self.initialize_called = True
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        await self.validate_context()
        return {"processed": True, "original": message}
    
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        return {
            "error": str(error),
            "agent": self.name
        }

@pytest.fixture
def mock_logger():
    """Create a mock logger"""
    logger = Mock(spec=Logger)
    logger.log_with_context = Mock()
    return logger

@pytest.fixture
def test_agent(mock_logger):
    """Create a test agent instance"""
    return TestAgent("test_agent", mock_logger)

@pytest.fixture
def test_context():
    """Create a test context"""
    return AgentContext(
        case_id="case-123",
        user_id="user-456",
        channel_id="channel-789",
        thread_ts="1234567890.123456",
        metadata={"test_key": "test_value"}
    )

@pytest.mark.asyncio
async def test_agent_initialization(test_agent: TestAgent):
    """Test agent initialization"""
    assert test_agent.name == "test_agent"
    assert test_agent.context is None
    assert not test_agent.initialize_called
    
    await test_agent.initialize()
    assert test_agent.initialize_called

def test_agent_context(test_agent: TestAgent, test_context: AgentContext, mock_logger: Mock):
    """Test setting agent context"""
    test_agent.set_context(test_context)
    
    assert test_agent.context == test_context
    mock_logger.log_with_context.assert_called_once_with(
        "INFO",
        "Context set for agent test_agent",
        {
            "case_id": "case-123",
            "user_id": "user-456",
            "channel_id": "channel-789"
        }
    )

@pytest.mark.asyncio
async def test_process_message_without_context(test_agent: TestAgent):
    """Test processing message without context"""
    with pytest.raises(AgentError) as exc_info:
        await test_agent.process_message({"test": "message"})
    
    assert "No context set for agent" in str(exc_info.value)
    assert exc_info.value.details["agent_type"] == "test_agent"

@pytest.mark.asyncio
async def test_process_message_with_context(test_agent: TestAgent, test_context: AgentContext):
    """Test processing message with context"""
    test_agent.set_context(test_context)
    
    message = {"test": "message"}
    result = await test_agent.process_message(message)
    
    assert result["processed"]
    assert result["original"] == message

@pytest.mark.asyncio
async def test_cleanup(test_agent: TestAgent, test_context: AgentContext, mock_logger: Mock):
    """Test agent cleanup"""
    test_agent.set_context(test_context)
    await test_agent.cleanup()
    
    mock_logger.log_with_context.assert_called_with(
        "INFO",
        "Cleaning up agent test_agent",
        {"context": test_context.metadata}
    )

def test_log_action_without_context(test_agent: TestAgent, mock_logger: Mock):
    """Test logging action without context"""
    test_agent.log_action("test_action", {"detail": "value"})
    
    mock_logger.log_with_context.assert_called_once_with(
        "INFO",
        "Agent test_agent - test_action",
        {
            "agent": "test_agent",
            "action": "test_action",
            "detail": "value"
        }
    )

def test_log_action_with_context(
    test_agent: TestAgent,
    test_context: AgentContext,
    mock_logger: Mock
):
    """Test logging action with context"""
    test_agent.set_context(test_context)
    test_agent.log_action("test_action", {"detail": "value"}, level="DEBUG")
    
    mock_logger.log_with_context.assert_called_once_with(
        "DEBUG",
        "Agent test_agent - test_action",
        {
            "agent": "test_agent",
            "action": "test_action",
            "case_id": "case-123",
            "user_id": "user-456",
            "channel_id": "channel-789",
            "detail": "value"
        }
    )

def test_agent_context_metadata_initialization():
    """Test AgentContext metadata initialization"""
    # Test with no metadata
    context = AgentContext(case_id="test")
    assert context.metadata == {}
    
    # Test with None metadata
    context = AgentContext(case_id="test", metadata=None)
    assert context.metadata == {}
    
    # Test with provided metadata
    metadata = {"key": "value"}
    context = AgentContext(case_id="test", metadata=metadata)
    assert context.metadata == metadata

@pytest.mark.asyncio
async def test_error_handling(test_agent: TestAgent):
    """Test agent error handling"""
    error = Exception("Test error")
    result = await test_agent.handle_error(error)
    
    assert result["error"] == "Test error"
    assert result["agent"] == "test_agent"
