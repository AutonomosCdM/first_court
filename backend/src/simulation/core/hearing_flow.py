"""
Maneja el flujo de una audiencia de control de detención
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.simulation.core.agent_adapter import AgentAdapter

class HearingPhase(Enum):
    """Fases de una audiencia de control de detención"""
    PREPARATION = "preparation"
    OPENING = "opening"
    DETENTION_REPORT = "detention_report"
    PROSECUTOR_ARGUMENTS = "prosecutor_arguments"
    DEFENDER_ARGUMENTS = "defender_arguments"
    JUDGE_QUESTIONS = "judge_questions"
    JUDGE_RESOLUTION = "judge_resolution"
    PRECAUTIONARY_MEASURES = "precautionary_measures"
    CLOSING = "closing"

class HearingAction(Enum):
    """Acciones posibles durante la audiencia"""
    SPEAK = "speak"              # Intervención oral
    REQUEST_TURN = "request_turn"  # Pedir la palabra
    OBJECT = "object"            # Objetar
    PRESENT = "present"          # Presentar documento/evidencia
    QUESTION = "question"        # Hacer pregunta
    ANSWER = "answer"            # Responder pregunta
    RESOLVE = "resolve"          # Resolver (juez)

class HearingFlow:
    """
    Maneja el flujo de una audiencia, controlando fases,
    turnos y acciones permitidas
    """
    
    def __init__(self,
                 agents: Dict[str, AgentAdapter],
                 case_data: Dict,
                 hearing_type: str = "control_detencion"):
        self.agents = agents
        self.case_data = case_data
        self.hearing_type = hearing_type
        self.current_phase = HearingPhase.PREPARATION
        self.current_speaker = None
        self.history: List[Dict] = []
        self.start_time = datetime.now()
        self._init_phase_config()
        
    def _init_phase_config(self):
        """
        Inicializa la configuración de fases y acciones permitidas
        """
        self.phase_config = {
            HearingPhase.PREPARATION: {
                "next": HearingPhase.OPENING,
                "allowed_roles": ["judge", "secretary"],
                "allowed_actions": [HearingAction.SPEAK],
                "required_actions": ["verify_parties", "verify_case"]
            },
            HearingPhase.OPENING: {
                "next": HearingPhase.DETENTION_REPORT,
                "allowed_roles": ["judge", "secretary"],
                "allowed_actions": [HearingAction.SPEAK],
                "required_actions": ["announce_case", "verify_parties_rights"]
            },
            HearingPhase.DETENTION_REPORT: {
                "next": HearingPhase.PROSECUTOR_ARGUMENTS,
                "allowed_roles": ["prosecutor"],
                "allowed_actions": [
                    HearingAction.SPEAK,
                    HearingAction.PRESENT
                ],
                "required_actions": ["present_detention_report"]
            },
            HearingPhase.PROSECUTOR_ARGUMENTS: {
                "next": HearingPhase.DEFENDER_ARGUMENTS,
                "allowed_roles": ["prosecutor", "judge", "defender"],
                "allowed_actions": [
                    HearingAction.SPEAK,
                    HearingAction.PRESENT,
                    HearingAction.OBJECT,
                    HearingAction.REQUEST_TURN,
                    HearingAction.QUESTION,
                    HearingAction.ANSWER
                ],
                "required_actions": ["present_arguments"]
            },
            HearingPhase.DEFENDER_ARGUMENTS: {
                "next": HearingPhase.JUDGE_QUESTIONS,
                "allowed_roles": ["defender", "judge", "prosecutor"],
                "allowed_actions": [
                    HearingAction.SPEAK,
                    HearingAction.PRESENT,
                    HearingAction.OBJECT,
                    HearingAction.REQUEST_TURN,
                    HearingAction.QUESTION,
                    HearingAction.ANSWER
                ],
                "required_actions": ["present_defense"]
            },
            HearingPhase.JUDGE_QUESTIONS: {
                "next": HearingPhase.JUDGE_RESOLUTION,
                "allowed_roles": ["judge", "prosecutor", "defender"],
                "allowed_actions": [
                    HearingAction.QUESTION,
                    HearingAction.ANSWER,
                    HearingAction.REQUEST_TURN,
                    HearingAction.SPEAK
                ],
                "required_actions": []
            },
            HearingPhase.JUDGE_RESOLUTION: {
                "next": HearingPhase.PRECAUTIONARY_MEASURES,
                "allowed_roles": ["judge", "prosecutor", "defender"],
                "allowed_actions": [
                    HearingAction.RESOLVE,
                    HearingAction.SPEAK,
                    HearingAction.QUESTION,
                    HearingAction.ANSWER
                ],
                "required_actions": ["announce_resolution"]
            },
            HearingPhase.PRECAUTIONARY_MEASURES: {
                "next": HearingPhase.CLOSING,
                "allowed_roles": ["prosecutor", "defender", "judge"],
                "allowed_actions": [
                    HearingAction.SPEAK,
                    HearingAction.PRESENT,
                    HearingAction.REQUEST_TURN,
                    HearingAction.RESOLVE
                ],
                "required_actions": ["resolve_measures"]
            },
            HearingPhase.CLOSING: {
                "next": None,
                "allowed_roles": ["judge", "secretary"],
                "allowed_actions": [HearingAction.SPEAK],
                "required_actions": ["close_hearing"]
            }
        }
        
    async def process_action(self,
                           role: str,
                           action: HearingAction,
                           content: str,
                           metadata: Optional[Dict] = None) -> Dict:
        """
        Procesa una acción durante la audiencia
        """
        # Validar acción
        if not self._is_action_allowed(role, action):
            return {
                "success": False,
                "error": "Acción no permitida en esta fase o para este rol"
            }
            
        # Procesar con el agente correspondiente
        agent = self.agents[role]
        context = self._prepare_context(action, content, metadata)
        
        response = await agent.process_interaction(
            content=content,
            interaction_type=action.value,
            metadata=context
        )
        
        # Registrar en el historial
        self._record_action(role, action, content, response)
        
        # Verificar si podemos avanzar de fase
        if self._can_advance_phase():
            self._advance_phase()
            
        return {
            "success": True,
            "response": response,
            "current_phase": self.current_phase.value,
            "allowed_actions": self._get_allowed_actions(role)
        }
        
    def _is_action_allowed(self, role: str, action: HearingAction) -> bool:
        """
        Verifica si una acción está permitida
        """
        # Verificar si el rol está permitido en la fase actual
        phase_rules = self.phase_config[self.current_phase]
        if role not in phase_rules["allowed_roles"]:
            return False
            
        # Verificar si la acción está permitida en la fase actual
        if action not in phase_rules["allowed_actions"]:
            return False
            
        return True
        
    def _prepare_context(self,
                        action: HearingAction,
                        content: str,
                        metadata: Optional[Dict]) -> Dict:
        """
        Prepara el contexto para el agente
        """
        context = {
            "hearing_type": self.hearing_type,
            "current_phase": self.current_phase.value,
            "case_data": self.case_data,
            "action": action.value,
            "content": content,
            "history": self.history,
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            context.update(metadata)
            
        return context
        
    def _record_action(self,
                      role: str,
                      action: HearingAction,
                      content: str,
                      response: Dict):
        """
        Registra una acción en el historial
        """
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "action": action.value,
            "content": content,
            "response": response,
            "phase": self.current_phase.value
        })
        
    def _can_advance_phase(self) -> bool:
        """
        Verifica si se pueden completar los requisitos de la fase actual
        """
        required_actions = self.phase_config[self.current_phase]["required_actions"]
        if not required_actions:
            return True
            
        # Obtener acciones completadas en la fase actual
        completed_actions = set()
        for action in self.history:
            for required in required_actions:
                if required in action["content"]:
                    completed_actions.add(required)
                    
        return len(completed_actions) == len(required_actions)
        
    def _advance_phase(self):
        """
        Avanza a la siguiente fase
        """
        next_phase = self.phase_config[self.current_phase]["next"]
        if next_phase:
            self.current_phase = next_phase
            
    def _get_allowed_actions(self, role: str) -> List[str]:
        """
        Obtiene las acciones permitidas para un rol
        """
        if role not in self.phase_config[self.current_phase]["allowed_roles"]:
            return []
            
        return [
            action.value
            for action in self.phase_config[self.current_phase]["allowed_actions"]
        ]
        
    def get_hearing_status(self) -> Dict:
        """
        Obtiene el estado actual de la audiencia
        """
        return {
            "hearing_type": self.hearing_type,
            "current_phase": self.current_phase.value,
            "duration": str(datetime.now() - self.start_time),
            "total_actions": len(self.history),
            "current_speaker": self.current_speaker,
            "phase_progress": self._get_phase_progress(),
            "allowed_actions_by_role": {
                role: self._get_allowed_actions(role)
                for role in self.agents.keys()
            }
        }
        
    def _get_phase_progress(self) -> Dict[str, Any]:
        """
        Calcula el progreso de la fase actual
        """
        required_actions = self.phase_config[self.current_phase]["required_actions"]
        if not required_actions:
            return {
                "completed": True,
                "pending_actions": []
            }
            
        # Obtener acciones completadas
        completed_actions = set()
        for action in reversed(self.history):
            if action.get("phase") == self.current_phase.value:
                content = action["content"]
                completed_actions.update(
                    required
                    for required in required_actions
                    if required in content
                )
                
        return {
            "completed": len(completed_actions) == len(required_actions),
            "pending_actions": list(set(required_actions) - completed_actions)
        }
