"""
Clase base para los agentes judiciales
"""
from typing import Dict, List
from src.agents.core.messaging import Message, MessageType, MessagePriority

class JudicialAgent:
    """
    Clase base para los agentes judiciales
    """
    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
        
    def analyze_case(self, case_data: Dict) -> Dict:
        """
        Analiza un caso judicial y genera una evaluación inicial
        """
        raise NotImplementedError
    
    def issue_resolution(self, case_id: str, context: Dict) -> Dict:
        """
        Emite una resolución judicial
        """
        raise NotImplementedError
    
    def review_evidence(self, evidence: List[Dict]) -> Dict:
        """
        Revisa y evalúa las evidencias presentadas
        """
        raise NotImplementedError
    
    def get_case_history(self) -> List[Dict]:
        """
        Retorna el historial de acciones del agente en el caso
        """
        raise NotImplementedError
        
    def handle_request(self, message: Message):
        """
        Maneja solicitudes de otros agentes
        """
        raise NotImplementedError
        
    def handle_notification(self, message: Message):
        """
        Maneja notificaciones de otros agentes
        """
        raise NotImplementedError
        
    def handle_decision(self, message: Message):
        """
        Maneja decisiones de otros agentes
        """
        raise NotImplementedError
        
    def send_message(self, receiver: str, subject: str, content: Dict, message_type: MessageType, priority: MessagePriority):
        """
        Envía un mensaje a otro agente
        """
        raise NotImplementedError
        
    def notify_update(self, receivers: List[str], subject: str, content: Dict, priority: MessagePriority):
        """
        Notifica a otros agentes sobre una actualización
        """
        raise NotImplementedError
