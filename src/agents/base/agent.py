from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.core.logging.logger import Logger
from src.core.exceptions.base import AgentError

@dataclass
class AgentContext:
    """Context information for agent operations"""
    case_id: Optional[str] = None
    user_id: Optional[str] = None
    channel_id: Optional[str] = None
    thread_ts: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata if not provided"""
        if self.metadata is None:
            self.metadata = {}

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, logger: Logger):
        """Initialize agent
        
        Args:
            name: Agent name
            logger: Logger instance
        """
        self.name = name
        self.logger = logger
        self.context: Optional[AgentContext] = None
    
    def set_context(self, context: AgentContext):
        """Set agent context
        
        Args:
            context: Agent context
        """
        self.context = context
        self.logger.log_with_context(
            "INFO",
            f"Context set for agent {self.name}",
            {
                "case_id": context.case_id,
                "user_id": context.user_id,
                "channel_id": context.channel_id
            }
        )
    
    @abstractmethod
    async def initialize(self):
        """Initialize agent resources"""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message
        
        Args:
            message: Message data
            
        Returns:
            Response data
        """
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle agent error
        
        Args:
            error: Exception instance
            
        Returns:
            Error response data
        """
        pass
    
    async def validate_context(self):
        """Validate current context
        
        Raises:
            AgentError: If context is invalid
        """
        if not self.context:
            raise AgentError(
                "No context set for agent",
                agent_type=self.name
            )
    
    async def cleanup(self):
        """Cleanup agent resources"""
        self.logger.log_with_context(
            "INFO",
            f"Cleaning up agent {self.name}",
            {"context": self.context.metadata if self.context else None}
        )
    
    def log_action(
        self,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        level: str = "INFO"
    ):
        """Log agent action
        
        Args:
            action: Action description
            details: Optional action details
            level: Log level
        """
        context_info = {
            "agent": self.name,
            "action": action
        }
        if self.context:
            context_info.update({
                "case_id": self.context.case_id,
                "user_id": self.context.user_id,
                "channel_id": self.context.channel_id
            })
        if details:
            context_info.update(details)
        
        self.logger.log_with_context(
            level,
            f"Agent {self.name} - {action}",
            context_info
        )
