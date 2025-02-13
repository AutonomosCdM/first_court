"""
Sistema de mensajería para la comunicación entre agentes judiciales
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import uuid
from dataclasses import dataclass, asdict

class MessagePriority(Enum):
    """Prioridad del mensaje"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class MessageType(Enum):
    """Tipo de mensaje"""
    REQUEST = "request"           # Solicitud de información o acción
    RESPONSE = "response"         # Respuesta a una solicitud
    NOTIFICATION = "notification" # Notificación general
    UPDATE = "update"            # Actualización de estado
    DECISION = "decision"        # Decisión que requiere acción
    ERROR = "error"              # Error en el proceso

@dataclass(frozen=True)
class Message:
    """Clase base para mensajes entre agentes"""
    id: str
    type: MessageType
    priority: MessagePriority
    sender: str
    receiver: str
    subject: str
    content: Dict[str, Any]
    timestamp: datetime
    reference_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(cls, 
               type: MessageType,
               priority: MessagePriority,
               sender: str,
               receiver: str,
               subject: str,
               content: Dict[str, Any],
               reference_id: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        """Crea un nuevo mensaje"""
        return cls(
            id=str(uuid.uuid4()),
            type=type,
            priority=priority,
            sender=sender,
            receiver=receiver,
            subject=subject,
            content=content,
            timestamp=datetime.now(),
            reference_id=reference_id,
            metadata=metadata
        )
    
    def to_dict(self) -> Dict:
        """Convierte el mensaje a diccionario"""
        data = asdict(self)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Crea un mensaje desde un diccionario"""
        data['type'] = MessageType(data['type'])
        data['priority'] = MessagePriority(data['priority'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class MessageQueue:
    """Cola de mensajes para cada agente"""
    def __init__(self):
        self.inbox: List[Message] = []
        self.outbox: List[Message] = []
        self.processed: List[Message] = []
    
    def add_to_inbox(self, message: Message):
        """Agrega un mensaje a la bandeja de entrada"""
        self.inbox.append(message)
        self.inbox.sort(key=lambda x: (x.priority.value, x.timestamp))
    
    def add_to_outbox(self, message: Message):
        """Agrega un mensaje a la bandeja de salida"""
        self.outbox.append(message)
        self.outbox.sort(key=lambda x: (x.priority.value, x.timestamp))
    
    def get_next_inbox_message(self) -> Optional[Message]:
        """Obtiene el siguiente mensaje de la bandeja de entrada"""
        return self.inbox.pop(0) if self.inbox else None
    
    def get_next_outbox_message(self) -> Optional[Message]:
        """Obtiene el siguiente mensaje de la bandeja de salida"""
        return self.outbox.pop(0) if self.outbox else None
    
    def mark_as_processed(self, message: Message):
        """Marca un mensaje como procesado"""
        self.processed.append(message)

class MessageBroker:
    """Broker central para la gestión de mensajes entre agentes"""
    def __init__(self):
        self.queues: Dict[str, MessageQueue] = {}
        self.subscriptions: Dict[str, List[str]] = {}
    
    def register_agent(self, agent_id: str):
        """Registra un nuevo agente en el sistema"""
        if agent_id not in self.queues:
            self.queues[agent_id] = MessageQueue()
            self.subscriptions[agent_id] = []
    
    def subscribe(self, subscriber: str, publisher: str):
        """Suscribe un agente a los mensajes de otro"""
        if subscriber in self.subscriptions:
            if publisher not in self.subscriptions[subscriber]:
                self.subscriptions[subscriber].append(publisher)
    
    def unsubscribe(self, subscriber: str, publisher: str):
        """Desuscribe un agente de los mensajes de otro"""
        if subscriber in self.subscriptions:
            if publisher in self.subscriptions[subscriber]:
                self.subscriptions[subscriber].remove(publisher)
    
    def send_message(self, message: Message):
        """Envía un mensaje a su destinatario"""
        if message.receiver in self.queues:
            self.queues[message.receiver].add_to_inbox(message)
            
            # Notificar a los suscriptores
            for subscriber in self.subscriptions:
                if message.sender in self.subscriptions[subscriber]:
                    notification = Message.create(
                        type=MessageType.NOTIFICATION,
                        priority=message.priority,
                        sender=message.sender,
                        receiver=subscriber,
                        subject=f"Notification: New message from {message.sender}",
                        content={"original_message_id": message.id},
                        reference_id=message.id
                    )
                    self.queues[subscriber].add_to_inbox(notification)
    
    def get_messages(self, agent_id: str) -> List[Message]:
        """Obtiene todos los mensajes pendientes para un agente"""
        if agent_id in self.queues:
            messages = []
            while True:
                message = self.queues[agent_id].get_next_inbox_message()
                if message is None:
                    break
                messages.append(message)
            return messages
        return []

class AgentCommunication:
    """Mixin para agregar capacidades de comunicación a los agentes"""
    def __init__(self, agent_id: str, broker: MessageBroker):
        self.agent_id = agent_id
        self.broker = broker
        self.broker.register_agent(agent_id)
    
    def send_message(self, 
                    receiver: str,
                    subject: str,
                    content: Dict[str, Any],
                    message_type: MessageType = MessageType.NOTIFICATION,
                    priority: MessagePriority = MessagePriority.MEDIUM,
                    reference_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None):
        """Envía un mensaje a otro agente"""
        message = Message.create(
            type=message_type,
            priority=priority,
            sender=self.agent_id,
            receiver=receiver,
            subject=subject,
            content=content,
            reference_id=reference_id,
            metadata=metadata
        )
        self.broker.send_message(message)
    
    def get_messages(self) -> List[Message]:
        """Obtiene los mensajes pendientes del agente"""
        return self.broker.get_messages(self.agent_id)
    
    def subscribe_to(self, publisher: str):
        """Suscribe al agente a los mensajes de otro"""
        self.broker.subscribe(self.agent_id, publisher)
    
    def unsubscribe_from(self, publisher: str):
        """Desuscribe al agente de los mensajes de otro"""
        self.broker.unsubscribe(self.agent_id, publisher)
