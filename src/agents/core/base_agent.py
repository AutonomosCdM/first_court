from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from .messaging import AgentCommunication, MessageBroker, MessageType, MessagePriority, Message
from rich.console import Console
from rich.panel import Panel
import json

console = Console()

class JudicialAgent(ABC, AgentCommunication):
    """Clase base para agentes judiciales"""
    _broker = MessageBroker()
    
    def __init__(self, name: str, llm_config: Dict[str, Any], agent_id: Optional[str] = None):
        self.name = name
        self.role = name
        self.llm_config = llm_config
        self.agent_id = agent_id or f"{self.__class__.__name__}_{name}"
        self.case_history: List[Dict] = []
        
        # Inicializar la comunicación
        AgentCommunication.__init__(self, self.agent_id, self._broker)
    
    def process_messages(self):
        """Procesa los mensajes pendientes del agente"""
        messages = self.get_messages()
        for message in messages:
            try:
                if isinstance(message.type, MessageType):
                    message_type = message.type
                else:
                    message_type = MessageType(message.type)
                
                if message_type == MessageType.REQUEST:
                    self.handle_request(message)
                elif message_type == MessageType.NOTIFICATION:
                    self.handle_notification(message)
                elif message_type == MessageType.DECISION:
                    self.handle_decision(message)
            except Exception as e:
                console.print(f"[red]Error al procesar mensaje: {str(e)}[/red]")
    
    def handle_request(self, message: Message):
        """Maneja una solicitud de otro agente"""
        console.print(f"[blue]Agente {self.name} recibió solicitud de {message.sender}:[/blue]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def handle_notification(self, message: Message):
        """Maneja una notificación de otro agente"""
        console.print(f"[yellow]Agente {self.name} recibió notificación de {message.sender}:[/yellow]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def handle_decision(self, message: Message):
        """Maneja una decisión de otro agente"""
        console.print(f"[red]Agente {self.name} recibió decisión de {message.sender}:[/red]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def request_information(self, receiver: str, subject: str, content: Dict[str, Any], priority: MessagePriority = MessagePriority.MEDIUM):
        """Solicita información a otro agente"""
        self.send_message(
            receiver=receiver,
            subject=subject,
            content=content,
            message_type=MessageType.REQUEST,
            priority=priority
        )
    
    def notify_update(self, receivers: List[str], subject: str, content: Dict[str, Any], priority: MessagePriority = MessagePriority.MEDIUM):
        """Notifica una actualización a otros agentes"""
        for receiver in receivers:
            self.send_message(
                receiver=receiver,
                subject=subject,
                content=content,
                message_type=MessageType.UPDATE,
                priority=priority
            )
    
    def communicate_decision(self, receivers: List[str], subject: str, content: Dict[str, Any], priority: MessagePriority = MessagePriority.HIGH):
        """Comunica una decisión a otros agentes"""
        for receiver in receivers:
            self.send_message(
                receiver=receiver,
                subject=subject,
                content=content,
                message_type=MessageType.DECISION,
                priority=priority
            )
    
    @abstractmethod
    def analyze_case(self, case_data: Dict) -> Dict:
        """Analiza un caso jurídico y genera recomendaciones"""
        pass
        
    @abstractmethod
    def generate_document(self, doc_type: str, context: Dict) -> str:
        """Genera documentos legales formalizados"""
        pass
