"""
Fábrica para crear agentes adaptados para simulación
"""
from typing import Dict, Optional, List

try:
    from src.agents.judge import Judge
    from src.agents.prosecutor import Prosecutor
    from src.agents.defender import Defender
    from src.agents.secretary import Secretary
except ImportError:
    from tests.simulation.mocks import (
        MockJudge as Judge,
        MockProsecutor as Prosecutor,
        MockDefender as Defender,
        MockSecretary as Secretary
    )
from src.simulation.core.agent_adapter import AgentAdapter, ParticipantRole
from src.simulation.core.evaluation_system import EvaluationSystem

class AgentFactory:
    """
    Fábrica para crear y configurar agentes adaptados para simulación
    """
    
    def __init__(self, evaluation_system: Optional[EvaluationSystem] = None):
        self.evaluation_system = evaluation_system or EvaluationSystem()
        
    def create_adapted_agents(self,
                            simulation_id: str,
                            case_data: Dict,
                            student_data: Optional[Dict] = None) -> Dict[str, AgentAdapter]:
        """
        Crea y configura todos los agentes necesarios para una simulación
        """
        agents = {}
        
        # Crear agentes base
        judge = Judge()
        prosecutor = Prosecutor()
        defender = Defender()
        secretary = Secretary()
        
        # Adaptar agentes para simulación
        agents["judge"] = self._adapt_agent(
            agent=judge,
            role=ParticipantRole.JUDGE,
            simulation_id=simulation_id,
            case_data=case_data,
            student_data=student_data
        )
        
        agents["prosecutor"] = self._adapt_agent(
            agent=prosecutor,
            role=ParticipantRole.PROSECUTOR,
            simulation_id=simulation_id,
            case_data=case_data,
            student_data=student_data
        )
        
        agents["defender"] = self._adapt_agent(
            agent=defender,
            role=ParticipantRole.DEFENDER,
            simulation_id=simulation_id,
            case_data=case_data,
            student_data=student_data
        )
        
        agents["secretary"] = self._adapt_agent(
            agent=secretary,
            role=ParticipantRole.SECRETARY,
            simulation_id=simulation_id,
            case_data=case_data,
            student_data=student_data
        )
        
        return agents
    
    def _adapt_agent(self,
                    agent: 'JudicialAgent',
                    role: ParticipantRole,
                    simulation_id: str,
                    case_data: Dict,
                    student_data: Optional[Dict] = None) -> AgentAdapter:
        """
        Adapta un agente individual para simulación
        """
        adapter = AgentAdapter(
            agent=agent,
            role=role,
            evaluation_system=self.evaluation_system
        )
        
        adapter.enter_simulation_mode(
            simulation_id=simulation_id,
            case_data=case_data,
            student_data=student_data
        )
        
        return adapter
    
    def get_evaluation_criteria(self, role: ParticipantRole) -> List[Dict]:
        """
        Obtiene los criterios de evaluación para un rol específico
        """
        return self.evaluation_system.get_criteria_for_role(role)
    
    def get_performance_metrics(self,
                              agents: Dict[str, AgentAdapter]) -> Dict[str, Dict]:
        """
        Obtiene métricas de desempeño para todos los agentes
        """
        return {
            name: agent.get_simulation_stats()
            for name, agent in agents.items()
        }
