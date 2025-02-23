"""
Implementación del Agente de Corte para coordinar el proceso judicial
"""
from typing import Dict, List
from src.agents.core.base_agent import JudicialAgent
from src.agents.judge import JudgeAgent
from src.agents.prosecutor import ProsecutorAgent
from src.agents.defender import DefenderAgent
from src.agents.secretary import SecretaryAgent
from src.agents.core.messaging import Message, MessageType, MessagePriority
from rich.console import Console

console = Console()

class CourtAgent(JudicialAgent):
    """
    Agente que coordina el proceso judicial, actuando como intermediario entre los
    diferentes agentes involucrados (Juez, Fiscal, Defensor, Secretario).
    """
    
    def __init__(self, drive_service, name: str = "Agente de Corte"):
        super().__init__(name)
        self.judge = JudgeAgent()
        self.prosecutor = ProsecutorAgent()
        self.defender = DefenderAgent()
        self.secretary = SecretaryAgent()
        
    def handle_case(self, case_data: Dict) -> Dict:
        """
        Maneja el proceso judicial de un caso, coordinando las acciones de los
        diferentes agentes.
        """
        console.print(f"[blue]Agente de Corte recibió nuevo caso:[/blue]")
        console.print(case_data)
        
        # Solicitar análisis de admisibilidad al Juez
        admissibility_analysis = self.judge.analyze_case(case_data)
        
        if admissibility_analysis['admisibilidad']['decision'] == 'ADMISIBLE':
            console.print("[green]Caso admitido[/green]")
            
            # Solicitar análisis de mérito al Fiscal
            merit_analysis = self.prosecutor.analyze_case(case_data)
            
            # Solicitar revisión de garantías al Defensor
            guarantee_review = self.defender.review_guarantees(case_data)
            
            # Integrar los análisis y tomar una decisión
            decision = self.judge.issue_resolution(case_data['id'], {
                'admisibilidad': admissibility_analysis['admisibilidad'],
                'analisis_merito': merit_analysis,
                'revision_garantias': guarantee_review
            })
            
            # Notificar a las partes sobre la resolución
            self.notify_parties(case_data['id'], decision)
            
            return decision
        else:
            console.print("[red]Caso inadmitido[/red]")
            return admissibility_analysis
        
    def notify_parties(self, case_id: str, resolution: Dict):
        """
        Notifica a las partes (Fiscal, Defensor, Secretario) sobre una resolución judicial
        """
        self.prosecutor.handle_notification({
            'type': 'resolution',
            'case_id': case_id,
            'content': resolution
        })
        
        self.defender.handle_notification({
            'type': 'resolution',
            'case_id': case_id,
            'content': resolution
        })
        
        self.secretary.handle_notification({
            'type': 'resolution',
            'case_id': case_id,
            'content': resolution
        })
        
    def handle_request(self, message: Message):
        """
        Maneja solicitudes de otros agentes, redirigiendo al agente correspondiente
        """
        console.print(f"[blue]Agente de Corte recibió solicitud de {message.sender}:[/blue]")
        console.print(message.content)
        
        if message.content.get('tipo_solicitud') == 'antecedentes_previos':
            self.judge.handle_request(message)
        else:
            console.print("[red]Solicitud no reconocida[/red]")
