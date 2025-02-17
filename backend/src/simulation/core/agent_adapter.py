"""
Adaptador para integrar agentes judiciales con el sistema de simulación
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

try:
    from src.agents.core.base_agent import JudicialAgent
except ImportError:
    from tests.simulation.mocks import MockJudicialAgent as JudicialAgent
from src.simulation.core.simulation_manager import ParticipantRole
from src.simulation.core.evaluation_system import EvaluationSystem

class AgentMode(Enum):
    NORMAL = "normal"          # Modo normal de operación
    SIMULATION = "simulation"  # Modo simulación para entrenamiento
    EVALUATION = "evaluation"  # Modo evaluación con feedback

class SimulationContext:
    """
    Contexto para agentes en modo simulación
    """
    def __init__(self,
                 simulation_id: str,
                 case_data: Dict,
                 student_data: Optional[Dict] = None):
        self.simulation_id = simulation_id
        self.case_data = case_data
        self.student_data = student_data
        self.start_time = datetime.now()
        self.interactions: List[Dict] = []
        self.current_phase = "preparation"

class AgentAdapter:
    """
    Adapta los agentes judiciales para participar en simulaciones
    """
    
    def __init__(self,
                 agent: JudicialAgent,
                 role: ParticipantRole,
                 evaluation_system: Optional[EvaluationSystem] = None):
        self.agent = agent
        self.role = role
        self.mode = AgentMode.NORMAL
        self.context: Optional[SimulationContext] = None
        self.evaluation_system = evaluation_system or EvaluationSystem()
        
    def enter_simulation_mode(self,
                            simulation_id: str,
                            case_data: Dict,
                            student_data: Optional[Dict] = None):
        """
        Configura el agente para modo simulación
        """
        self.mode = AgentMode.SIMULATION
        self.context = SimulationContext(
            simulation_id=simulation_id,
            case_data=case_data,
            student_data=student_data
        )
        
    def exit_simulation_mode(self):
        """
        Retorna el agente a modo normal
        """
        self.mode = AgentMode.NORMAL
        self.context = None
        
    async def process_interaction(self,
                                content: str,
                                interaction_type: str,
                                metadata: Optional[Dict] = None) -> Dict:
        """
        Procesa una interacción en el contexto actual
        """
        if not self.context and self.mode != AgentMode.NORMAL:
            raise ValueError("Agente no está en contexto de simulación")
            
        # Preparar contexto para el agente
        context = self._prepare_agent_context(content, interaction_type, metadata)
        
        # Procesar con el agente
        response = await self.agent.process_messages(context)
        
        # Si estamos en modo simulación, evaluar y agregar feedback
        if self.mode in [AgentMode.SIMULATION, AgentMode.EVALUATION]:
            evaluation = self._evaluate_interaction(content, response, interaction_type)
            response["evaluation"] = evaluation
            
        return response
    
    def _prepare_agent_context(self,
                             content: str,
                             interaction_type: str,
                             metadata: Optional[Dict]) -> Dict:
        """
        Prepara el contexto para el agente
        """
        context = {
            "mode": self.mode.value,
            "role": self.role.value,
            "content": content,
            "type": interaction_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.context:
            context.update({
                "simulation_id": self.context.simulation_id,
                "case_data": self.context.case_data,
                "current_phase": self.context.current_phase,
                "interaction_history": self.context.interactions
            })
            
        if metadata:
            context.update(metadata)
            
        return context
    
    def _evaluate_interaction(self,
                            input_content: str,
                            agent_response: Dict,
                            interaction_type: str) -> Dict:
        """
        Evalúa una interacción para propósitos de simulación
        """
        if not self.context:
            return {}
            
        evaluation_context = {
            "case_type": self.context.case_data.get("type"),
            "phase": self.context.current_phase,
            "previous_interactions": self.context.interactions,
            "student_data": self.context.student_data,
            "agent_role": self.role.value
        }
        
        # Evaluar la respuesta del agente
        evaluation = self.evaluation_system.evaluate_interaction(
            content=agent_response.get("response", ""),
            context=evaluation_context,
            interaction_type=interaction_type
        )
        
        # Registrar la interacción en el contexto
        self.context.interactions.append({
            "timestamp": datetime.now().isoformat(),
            "input": input_content,
            "response": agent_response,
            "evaluation": evaluation
        })
        
        return evaluation
    
    def get_simulation_stats(self) -> Dict:
        """
        Obtiene estadísticas de la simulación actual
        """
        if not self.context:
            return {}
            
        interactions = self.context.interactions
        evaluations = [i.get("evaluation", {}) for i in interactions]
        
        return {
            "simulation_id": self.context.simulation_id,
            "duration": str(datetime.now() - self.context.start_time),
            "total_interactions": len(interactions),
            "average_score": sum(e.get("overall_score", 0) for e in evaluations) / len(evaluations) if evaluations else 0,
            "performance_by_criteria": self._aggregate_criteria_scores(evaluations)
        }
    
    def _aggregate_criteria_scores(self, evaluations: List[Dict]) -> Dict:
        """
        Agrega puntuaciones por criterio
        """
        criteria_scores = {}
        
        for evaluation in evaluations:
            criteria = evaluation.get("criteria_scores", {})
            for criterion, data in criteria.items():
                if criterion not in criteria_scores:
                    criteria_scores[criterion] = []
                criteria_scores[criterion].append(data.get("score", 0))
        
        return {
            criterion: sum(scores) / len(scores)
            for criterion, scores in criteria_scores.items()
            if scores
        }
