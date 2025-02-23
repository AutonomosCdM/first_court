"""
Implementación del Agente Fiscal para el sistema judicial
"""
from typing import Dict, List, Optional
from src.agents.core.base_agent import JudicialAgent
from src.agents.core.messaging import Message, AgentCommunication
from src.llm.providers.claude_custom import ClaudeClient
import os
from rich.console import Console
from rich.panel import Panel
import json

console = Console()

class ProsecutorAgent(JudicialAgent, AgentCommunication):
    """
    Agente que actúa como Fiscal en el sistema judicial.
    Responsable de:
    - Investigar hechos y recabar evidencias
    - Formular acusaciones
    - Solicitar diligencias
    - Participar en audiencias
    - Presentar pruebas y argumentos
    """
    
    def __init__(self, name: str = "Fiscal", broker=None):
        JudicialAgent.__init__(self, name, {"api_key": os.getenv("ANTHROPIC_API_KEY")})
        AgentCommunication.__init__(self, name, broker)
        self.llm = ClaudeClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    def analyze_case(self, case_data: Dict) -> Dict:
        """Implementación del método abstracto de JudicialAgent"""
        result = self.investigate_case(case_data)
        return json.loads(result) if isinstance(result, str) else result
    
    def investigate_case(self, case_data: Dict) -> Dict:
        """
        Analiza los hechos del caso y determina líneas de investigación
        """
        prompt = f"""
        Como fiscal del sistema judicial chileno, analiza los siguientes hechos y determina las líneas de investigación.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "analisis_hechos": "descripción detallada",
            "lineas_investigacion": ["línea 1", "línea 2", ...],
            "diligencias_propuestas": ["diligencia 1", "diligencia 2", ...],
            "evidencia_requerida": ["evidencia 1", "evidencia 2", ...],
            "riesgos_identificados": ["riesgo 1", "riesgo 2", ...]
        }}
        
        DATOS DEL CASO:
        {json.dumps(case_data, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            # Intentar extraer el JSON de la respuesta
            try:
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    analysis = json.loads(json_str)
                else:
                    analysis = {
                        "analisis_hechos": response,
                        "lineas_investigacion": [],
                        "diligencias_propuestas": [],
                        "evidencia_requerida": [],
                        "riesgos_identificados": []
                    }
                
                self.case_history.append({
                    "type": "investigation_analysis",
                    "data": analysis
                })
                return analysis
            except json.JSONDecodeError:
                analysis = {
                    "analisis_hechos": response,
                    "lineas_investigacion": [],
                    "diligencias_propuestas": [],
                    "evidencia_requerida": [],
                    "riesgos_identificados": []
                }
                self.case_history.append({
                    "type": "investigation_analysis",
                    "data": analysis
                })
                return analysis
        except Exception as e:
            console.print(f"[red]Error al analizar el caso: {str(e)}[/red]")
            return {"error": str(e)}
    
    def handle_request(self, message: Message):
        """Maneja una solicitud de otro agente"""
        console.print(f"[blue]Fiscal recibió solicitud de {message.sender}:[/blue]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def handle_notification(self, message: Message):
        """Maneja una notificación de otro agente"""
        console.print(f"[yellow]Fiscal recibió notificación de {message.sender}:[/yellow]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def handle_decision(self, message: Message):
        """Maneja una decisión de otro agente"""
        console.print(f"[red]Fiscal recibió decisión de {message.sender}:[/red]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def formulate_accusation(self, investigation_data: Dict) -> Dict:
        """
        Formula una acusación basada en la investigación
        """
        prompt = f"""
        Como fiscal del sistema judicial chileno, formula una acusación basada en la siguiente investigación.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "hechos_acusados": ["hecho 1", "hecho 2", ...],
            "calificacion_juridica": "descripción del tipo penal",
            "participacion_imputado": "grado de participación",
            "circunstancias_modificatorias": ["circunstancia 1", "circunstancia 2", ...],
            "pruebas_ofrecidas": ["prueba 1", "prueba 2", ...],
            "pena_solicitada": "descripción de la pena"
        }}
        
        DATOS DE LA INVESTIGACIÓN:
        {json.dumps(investigation_data, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            try:
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    accusation = json.loads(json_str)
                else:
                    accusation = {
                        "hechos_acusados": [],
                        "calificacion_juridica": response,
                        "participacion_imputado": "Por determinar",
                        "circunstancias_modificatorias": [],
                        "pruebas_ofrecidas": [],
                        "pena_solicitada": "Por determinar"
                    }
                
                self.case_history.append({
                    "type": "accusation",
                    "data": accusation
                })
                return accusation
            except json.JSONDecodeError:
                accusation = {
                    "hechos_acusados": [],
                    "calificacion_juridica": response,
                    "participacion_imputado": "Por determinar",
                    "circunstancias_modificatorias": [],
                    "pruebas_ofrecidas": [],
                    "pena_solicitada": "Por determinar"
                }
                self.case_history.append({
                    "type": "accusation",
                    "data": accusation
                })
                return accusation
        except Exception as e:
            console.print(f"[red]Error al formular acusación: {str(e)}[/red]")
            return {"error": str(e)}
    
    def generate_document(self, document_type: str, context: Dict) -> str:
        """
        Genera documentos como acusaciones, solicitudes, etc.
        """
        prompt = f"""
        Como fiscal del sistema judicial chileno, genera un documento de tipo {document_type} 
        basado en el siguiente contexto:
        
        CONTEXTO:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        El documento debe seguir el formato y estructura oficial del ministerio público chileno.
        """
        
        try:
            response = self.llm.generate(prompt)
            self.case_history.append({
                "type": "document_generation",
                "document_type": document_type,
                "content": response
            })
            return response
        except Exception as e:
            console.print(f"[red]Error al generar documento: {str(e)}[/red]")
            return f"Error: {str(e)}"
    
    def get_case_history(self) -> List[Dict]:
        """
        Retorna el historial de acciones del fiscal en el caso
        """
        return self.case_history
