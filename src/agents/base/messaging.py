from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    """Base message structure"""
    content: str
    message_type: str
    sender: str
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary
        
        Returns:
            Dictionary representation of message
        """
        return {
            "content": self.content,
            "message_type": self.message_type,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            Message instance
        """
        return cls(
            content=data["content"],
            message_type=data["message_type"],
            sender=data["sender"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None,
            metadata=data.get("metadata")
        )

class MessageHandler(ABC):
    """Base interface for message handling"""
    
    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming message
        
        Args:
            message: Incoming message
            
        Returns:
            Optional response message
        """
        pass
    
    @abstractmethod
    async def format_message(self, message: Message) -> Dict[str, Any]:
        """Format message for sending
        
        Args:
            message: Message to format
            
        Returns:
            Formatted message data
        """
        pass

class MessageBroker(ABC):
    """Base interface for message routing"""
    
    @abstractmethod
    async def send_message(
        self,
        message: Message,
        destination: str
    ) -> bool:
        """Send message to destination
        
        Args:
            message: Message to send
            destination: Destination identifier
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def broadcast_message(
        self,
        message: Message,
        destinations: list[str]
    ) -> Dict[str, bool]:
        """Broadcast message to multiple destinations
        
        Args:
            message: Message to broadcast
            destinations: List of destination identifiers
            
        Returns:
            Dictionary mapping destinations to success status
        """
        pass
    
    @abstractmethod
    async def register_handler(
        self,
        message_type: str,
        handler: MessageHandler
    ):
        """Register handler for message type
        
        Args:
            message_type: Type of messages to handle
            handler: Handler instance
        """
        pass

class MessageQueue(ABC):
    """Base interface for message queueing"""
    
    @abstractmethod
    async def enqueue(self, message: Message):
        """Add message to queue
        
        Args:
            message: Message to queue
        """
        pass
    
    @abstractmethod
    async def dequeue(self) -> Optional[Message]:
        """Get next message from queue
        
        Returns:
            Next message or None if queue is empty
        """
        pass
    
    @abstractmethod
    async def peek(self) -> Optional[Message]:
        """View next message without removing it
        
        Returns:
            Next message or None if queue is empty
        """
        pass
    
    @abstractmethod
    async def clear(self):
        """Clear all messages from queue"""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Get current queue size
        
        Returns:
            Number of messages in queue
        """
        pass
