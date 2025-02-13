"""
Agentes judiciales con integración Gather.town
"""
from typing import Dict, Optional
from src.agents.judge import JudgeAgent
from src.agents.prosecutor import ProsecutorAgent
from src.agents.defender import DefenderAgent
from src.agents.secretary import SecretaryAgent
from src.agents.core.messaging import Message, MessageType
from src.integrations.gather_integration import GatherCourtIntegration

class GatherEnabledAgent:
    """Mixin para agregar funcionalidad de Gather a los agentes"""
    
    def __init__(self, gather_integration: GatherCourtIntegration, space_id: str):
        self.gather = gather_integration
        self.space_id = space_id
        
    def broadcast_to_gather(self, message: str, area: Optional[str] = None):
        """
        Transmitir un mensaje en el espacio de Gather
        TODO: Implementar cuando tengamos acceso a la API de WebSocket de Gather
        """
        pass

class GatherJudgeAgent(JudgeAgent, GatherEnabledAgent):
    def __init__(self, name: str, gather_integration: GatherCourtIntegration, space_id: str):
        JudgeAgent.__init__(self, name)
        GatherEnabledAgent.__init__(self, gather_integration, space_id)
    
    def handle_decision(self, message: Message):
        # Procesar la decisión normalmente
        super().handle_decision(message)
        
        # Transmitir la decisión en Gather
        self.broadcast_to_gather(
            f"El Juez ha emitido una decisión: {message.content.get('decision', 'No especificada')}"
        )

class GatherProsecutorAgent(ProsecutorAgent, GatherEnabledAgent):
    def __init__(self, name: str, gather_integration: GatherCourtIntegration, space_id: str):
        ProsecutorAgent.__init__(self, name)
        GatherEnabledAgent.__init__(self, gather_integration, space_id)
    
    def handle_request(self, message: Message):
        # Procesar la solicitud normalmente
        super().handle_request(message)
        
        # Transmitir la acción en Gather
        self.broadcast_to_gather(
            f"El Fiscal está procesando una solicitud de {message.sender}"
        )

class GatherDefenderAgent(DefenderAgent, GatherEnabledAgent):
    def __init__(self, name: str, gather_integration: GatherCourtIntegration, space_id: str):
        DefenderAgent.__init__(self, name)
        GatherEnabledAgent.__init__(self, gather_integration, space_id)
    
    def handle_request(self, message: Message):
        # Procesar la solicitud normalmente
        super().handle_request(message)
        
        # Transmitir la acción en Gather
        self.broadcast_to_gather(
            f"El Defensor está procesando una solicitud de {message.sender}"
        )

class GatherSecretaryAgent(SecretaryAgent, GatherEnabledAgent):
    def __init__(self, name: str, gather_integration: GatherCourtIntegration, space_id: str):
        SecretaryAgent.__init__(self, name)
        GatherEnabledAgent.__init__(self, gather_integration, space_id)
    
    def schedule_hearing(self, hearing_type: str, case_data: Dict, participants: list):
        # Programar la audiencia normalmente
        super().schedule_hearing(hearing_type, case_data, participants)
        
        # Transmitir la programación en Gather
        self.broadcast_to_gather(
            f"Se ha programado una audiencia de tipo {hearing_type} para el caso {case_data.get('id', 'No especificado')}"
        )
