from typing import List, Dict, Any
from src.agents.core.base_agent import JudicialAgent
from rich.console import Console
from rich.panel import Panel

console = Console()

class CourtSimulation:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, JudicialAgent] = {}
        self.case_history: List[Dict] = []
        
    def add_agent(self, role: str, agent: JudicialAgent):
        """Agrega un agente al sistema de simulación"""
        self.agents[role] = agent
        console.print(f"[green]Agente {role} agregado exitosamente[/green]")
        
    def run_simulation(self, case_data: Dict):
        """Ejecuta una simulación completa de un caso"""
        console.print(Panel.fit("Iniciando simulación de caso judicial", 
                              title="Sistema Judicial", 
                              border_style="blue"))
        
        # Análisis inicial del caso
        for role, agent in self.agents.items():
            analysis = agent.analyze_case(case_data)
            self.case_history.append({
                "role": role,
                "action": "análisis",
                "content": analysis
            })
            
        console.print("[yellow]Simulación completada[/yellow]")
        return self.case_history
