import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import Mock

from src.agents.base.messaging import (
    Message,
    MessageHandler,
    MessageBroker,
    MessageQueue
)

class TestMessageHandler(MessageHandler):
    """Test implementation of MessageHandler"""
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        return Message(
            content=f"Handled: {message.content}",
            message_type="response",
            sender="test_handler"
        )
    
    async def format_message(self, message: Message) -> Dict[str, Any]:
        return message.to_dict()

class TestMessageBroker(MessageBroker):
    """Test implementation of MessageBroker"""
    
    def __init__(self):
        self.handlers = {}
        self.sent_messages = {}
        self.broadcast_messages = {}
    
    async def send_message(self, message: Message, destination: str) -> bool:
        self.sent_messages[destination] = message
        return True
    
    async def broadcast_message(
        self,
        message: Message,
        destinations: list[str]
    ) -> Dict[str, bool]:
        result = {}
        for dest in destinations:
            self.broadcast_messages[dest] = message
            result[dest] = True
        return result
    
    async def register_handler(self, message_type: str, handler: MessageHandler):
        self.handlers[message_type] = handler

class TestMessageQueue(MessageQueue):
    """Test implementation of MessageQueue"""
    
    def __init__(self):
        self.messages = []
    
    async def enqueue(self, message: Message):
        self.messages.append(message)
    
    async def dequeue(self) -> Optional[Message]:
        if self.messages:
            return self.messages.pop(0)
        return None
    
    async def peek(self) -> Optional[Message]:
        if self.messages:
            return self.messages[0]
        return None
    
    async def clear(self):
        self.messages = []
    
    async def size(self) -> int:
        return len(self.messages)

def test_message_creation():
    """Test message creation and initialization"""
    # Test with minimal parameters
    message = Message(
        content="Test content",
        message_type="test",
        sender="test_sender"
    )
    assert message.content == "Test content"
    assert message.message_type == "test"
    assert message.sender == "test_sender"
    assert isinstance(message.timestamp, datetime)
    assert message.metadata == {}
    
    # Test with all parameters
    timestamp = datetime.now()
    metadata = {"key": "value"}
    message = Message(
        content="Test content",
        message_type="test",
        sender="test_sender",
        timestamp=timestamp,
        metadata=metadata
    )
    assert message.timestamp == timestamp
    assert message.metadata == metadata

def test_message_serialization():
    """Test message serialization to/from dictionary"""
    original = Message(
        content="Test content",
        message_type="test",
        sender="test_sender",
        metadata={"key": "value"}
    )
    
    # Convert to dict
    message_dict = original.to_dict()
    assert message_dict["content"] == "Test content"
    assert message_dict["message_type"] == "test"
    assert message_dict["sender"] == "test_sender"
    assert message_dict["metadata"] == {"key": "value"}
    
    # Convert back to Message
    reconstructed = Message.from_dict(message_dict)
    assert reconstructed.content == original.content
    assert reconstructed.message_type == original.message_type
    assert reconstructed.sender == original.sender
    assert reconstructed.metadata == original.metadata

@pytest.mark.asyncio
async def test_message_handler():
    """Test message handler implementation"""
    handler = TestMessageHandler()
    message = Message(
        content="Test message",
        message_type="test",
        sender="test_sender"
    )
    
    # Test message handling
    response = await handler.handle_message(message)
    assert response.content == "Handled: Test message"
    assert response.message_type == "response"
    assert response.sender == "test_handler"
    
    # Test message formatting
    formatted = await handler.format_message(message)
    assert formatted == message.to_dict()

@pytest.mark.asyncio
async def test_message_broker():
    """Test message broker implementation"""
    broker = TestMessageBroker()
    handler = TestMessageHandler()
    message = Message(
        content="Test message",
        message_type="test",
        sender="test_sender"
    )
    
    # Test handler registration
    await broker.register_handler("test", handler)
    assert broker.handlers["test"] == handler
    
    # Test message sending
    success = await broker.send_message(message, "destination1")
    assert success
    assert broker.sent_messages["destination1"] == message
    
    # Test message broadcasting
    destinations = ["dest1", "dest2"]
    results = await broker.broadcast_message(message, destinations)
    assert all(results.values())
    for dest in destinations:
        assert broker.broadcast_messages[dest] == message

@pytest.mark.asyncio
async def test_message_queue():
    """Test message queue implementation"""
    queue = TestMessageQueue()
    message1 = Message(
        content="Message 1",
        message_type="test",
        sender="sender1"
    )
    message2 = Message(
        content="Message 2",
        message_type="test",
        sender="sender2"
    )
    
    # Test initial state
    assert await queue.size() == 0
    assert await queue.peek() is None
    assert await queue.dequeue() is None
    
    # Test enqueue
    await queue.enqueue(message1)
    await queue.enqueue(message2)
    assert await queue.size() == 2
    
    # Test peek
    peeked = await queue.peek()
    assert peeked == message1
    assert await queue.size() == 2  # Size shouldn't change
    
    # Test dequeue
    dequeued = await queue.dequeue()
    assert dequeued == message1
    assert await queue.size() == 1
    
    # Test clear
    await queue.clear()
    assert await queue.size() == 0
    assert await queue.peek() is None
