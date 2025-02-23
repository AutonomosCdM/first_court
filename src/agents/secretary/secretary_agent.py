from typing import Dict, Any, Optional
from datetime import datetime

from src.agents.base.agent import BaseAgent, AgentContext
from src.agents.base.messaging import Message, MessageHandler
from src.core.logging.logger import Logger
from src.core.exceptions.base import AgentError
from src.integrations.database.slack_db import SlackDatabase

class SecretaryAgent(BaseAgent, MessageHandler):
    """Secretary agent implementation"""
    
    def __init__(
        self,
        name: str,
        logger: Logger,
        database: SlackDatabase
    ):
        """Initialize secretary agent
        
        Args:
            name: Agent name
            logger: Logger instance
            database: Database instance
        """
        super().__init__(name, logger)
        self.database = database
    
    async def initialize(self):
        """Initialize agent resources"""
        self.log_action("Initializing secretary agent")
        # Ensure database connection
        with self.database.connection():
            self.log_action("Database connection verified")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message
        
        Args:
            message: Message data
            
        Returns:
            Response data
        """
        await self.validate_context()
        
        try:
            # Convert raw message to Message instance
            msg = Message(
                content=message.get("text", ""),
                message_type=message.get("type", "unknown"),
                sender=message.get("user", "unknown"),
                metadata=message
            )
            
            # Handle message
            response = await self.handle_message(msg)
            if response:
                return await self.format_message(response)
            return {}
            
        except Exception as e:
            self.log_action(
                "Error processing message",
                {"error": str(e)},
                level="ERROR"
            )
            return await self.handle_error(e)
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming message
        
        Args:
            message: Incoming message
            
        Returns:
            Optional response message
        """
        self.log_action(
            "Handling message",
            {"type": message.message_type, "sender": message.sender}
        )
        
        # Handle different message types
        if message.message_type == "case_creation":
            return await self._handle_case_creation(message)
        elif message.message_type == "document_upload":
            return await self._handle_document_upload(message)
        elif message.message_type == "hearing_schedule":
            return await self._handle_hearing_schedule(message)
        else:
            self.log_action(
                "Unknown message type",
                {"type": message.message_type},
                level="WARNING"
            )
            return None
    
    async def format_message(self, message: Message) -> Dict[str, Any]:
        """Format message for sending
        
        Args:
            message: Message to format
            
        Returns:
            Formatted message data
        """
        return {
            "text": message.content,
            "thread_ts": self.context.thread_ts if self.context else None,
            "channel": self.context.channel_id if self.context else None,
            **message.metadata
        }
    
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle agent error
        
        Args:
            error: Exception instance
            
        Returns:
            Error response data
        """
        error_message = Message(
            content=f"Error: {str(error)}",
            message_type="error",
            sender=self.name,
            metadata={"error_type": type(error).__name__}
        )
        return await self.format_message(error_message)
    
    async def _handle_case_creation(self, message: Message) -> Message:
        """Handle case creation request
        
        Args:
            message: Case creation message
            
        Returns:
            Response message
        """
        with self.database.connection(), self.database.transaction():
            case = self.database.create_case(message.content)
            
            return Message(
                content=f"Caso creado: {case['case_number']}",
                message_type="case_created",
                sender=self.name,
                metadata=case
            )
    
    async def _handle_document_upload(self, message: Message) -> Message:
        """Handle document upload
        
        Args:
            message: Document upload message
            
        Returns:
            Response message
        """
        if not self.context or not self.context.case_id:
            raise AgentError(
                "No case context for document upload",
                agent_type=self.name
            )
        
        metadata = message.metadata
        with self.database.connection(), self.database.transaction():
            doc = self.database.add_document(
                case_id=self.context.case_id,
                filename=metadata["filename"],
                filetype=metadata["filetype"],
                size=metadata["size"]
            )
            
            return Message(
                content=f"Documento agregado: {doc['filename']}",
                message_type="document_added",
                sender=self.name,
                metadata=doc
            )
    
    async def _handle_hearing_schedule(self, message: Message) -> Message:
        """Handle hearing schedule request
        
        Args:
            message: Hearing schedule message
            
        Returns:
            Response message
        """
        if not self.context or not self.context.case_id:
            raise AgentError(
                "No case context for hearing schedule",
                agent_type=self.name
            )
        
        with self.database.connection(), self.database.transaction():
            hearing = self.database.schedule_hearing(
                case_id=self.context.case_id,
                hearing_date=message.content
            )
            
            return Message(
                content=f"Audiencia programada para: {hearing['hearing_date']}",
                message_type="hearing_scheduled",
                sender=self.name,
                metadata=hearing
            )
