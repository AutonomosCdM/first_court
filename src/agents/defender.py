"""
Implementación del Agente Defensor para el sistema judicial
"""
from typing import Dict, List, Optional
from src.agents.core.base_agent import JudicialAgent
from src.agents.core.messaging import Message
from src.llm.providers.claude_custom import ClaudeClient
import os
from rich.console import Console
from rich.panel import Panel
import json

console = Console()

class DefenderAgent(JudicialAgent):
    """
    Agente que actúa como Defensor en el sistema judicial.
    Responsable de:
    - Analizar casos desde la perspectiva de la defensa
    - Construir teorías del caso
    - Evaluar evidencias y preparar contra-argumentos
    - Presentar defensas y alegatos
    - Proteger los derechos del imputado
    """
    
    def __init__(self, name: str = "Defensor"):
        super().__init__(name, {"api_key": os.getenv("ANTHROPIC_API_KEY")})
        self.llm = ClaudeClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def analyze_case(self, case_data: Dict) -> Dict:
        """Implementación del método abstracto de JudicialAgent"""
        return self.analyze_defense_case(case_data)
    
    def analyze_defense_case(self, case_data: Dict) -> Dict:
        """
        Analiza el caso desde la perspectiva de la defensa
        """
        prompt = f"""
        Como defensor del sistema judicial chileno, analiza el siguiente caso y proporciona una estrategia de defensa.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "analisis_preliminar": "descripción detallada",
            "teoria_caso": "planteamiento de la defensa",
            "puntos_debiles_acusacion": ["punto 1", "punto 2", ...],
            "derechos_vulnerados": ["derecho 1", "derecho 2", ...],
            "estrategia_defensa": ["estrategia 1", "estrategia 2", ...],
            "diligencias_solicitadas": ["diligencia 1", "diligencia 2", ...]
        }}
        
        DATOS DEL CASO:
        {json.dumps(case_data, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            try:
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    analysis = json.loads(json_str)
                else:
                    analysis = {
                        "analisis_preliminar": response,
                        "teoria_caso": "",
                        "puntos_debiles_acusacion": [],
                        "derechos_vulnerados": [],
                        "estrategia_defensa": [],
                        "diligencias_solicitadas": []
                    }
                
                self.case_history.append({
                    "type": "defense_analysis",
                    "data": analysis
                })
                return analysis
            except json.JSONDecodeError:
                analysis = {
                    "analisis_preliminar": response,
                    "teoria_caso": "",
                    "puntos_debiles_acusacion": [],
                    "derechos_vulnerados": [],
                    "estrategia_defensa": [],
                    "diligencias_solicitadas": []
                }
                self.case_history.append({
                    "type": "defense_analysis",
                    "data": analysis
                })
                return analysis
        except Exception as e:
            console.print(f"[red]Error al analizar el caso: {str(e)}[/red]")
            return {"error": str(e)}
    
    def handle_request(self, message: Message):
        """Maneja una solicitud de otro agente"""
        console.print(f"[blue]Defensor recibió solicitud de {message.sender}:[/blue]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def handle_notification(self, message: Message):
        """Maneja una notificación de otro agente"""
        console.print(f"[yellow]Defensor recibió notificación de {message.sender}:[/yellow]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def handle_decision(self, message: Message):
        """Maneja una decisión de otro agente"""
        console.print(f"[red]Defensor recibió decisión de {message.sender}:[/red]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def evaluate_evidence(self, evidence: List[Dict]) -> Dict:
        """
        Evalúa las evidencias desde la perspectiva de la defensa
        """
        prompt = f"""
        Como defensor del sistema judicial chileno, evalúa las siguientes evidencias.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "evaluacion_evidencias": [
                {{
                    "evidencia": "descripción",
                    "debilidades": ["debilidad 1", "debilidad 2", ...],
                    "contra_argumentos": ["argumento 1", "argumento 2", ...],
                    "objeciones_admisibilidad": ["objeción 1", "objeción 2", ...]
                }}
            ],
            "conclusiones": "análisis general",
            "recomendaciones": ["recomendación 1", "recomendación 2", ...]
        }}
        
        EVIDENCIAS:
        {json.dumps(evidence, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            try:
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    evaluation = json.loads(json_str)
                else:
                    evaluation = {
                        "evaluacion_evidencias": [],
                        "conclusiones": response,
                        "recomendaciones": []
                    }
                
                self.case_history.append({
                    "type": "evidence_evaluation",
                    "data": evaluation
                })
                return evaluation
            except json.JSONDecodeError:
                evaluation = {
                    "evaluacion_evidencias": [],
                    "conclusiones": response,
                    "recomendaciones": []
                }
                self.case_history.append({
                    "type": "evidence_evaluation",
                    "data": evaluation
                })
                return evaluation
        except Exception as e:
            console.print(f"[red]Error al evaluar evidencias: {str(e)}[/red]")
            return {"error": str(e)}
    
    def prepare_defense(self, case_data: Dict, prosecution_arguments: Dict) -> Dict:
        """
        Prepara la defensa en respuesta a los argumentos de la fiscalía
        """
        prompt = f"""
        Como defensor del sistema judicial chileno, prepara una defensa en respuesta a la acusación.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "argumentos_defensa": ["argumento 1", "argumento 2", ...],
            "refutacion_cargos": {{
                "cargo 1": "refutación detallada",
                "cargo 2": "refutación detallada",
                ...
            }},
            "atenuantes_propuestas": ["atenuante 1", "atenuante 2", ...],
            "peticiones": ["petición 1", "petición 2", ...],
            "pruebas_defensa": ["prueba 1", "prueba 2", ...]
        }}
        
        CASO:
        {json.dumps(case_data, indent=2, ensure_ascii=False)}
        
        ARGUMENTOS FISCALÍA:
        {json.dumps(prosecution_arguments, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            try:
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    defense = json.loads(json_str)
                else:
                    defense = {
                        "argumentos_defensa": [],
                        "refutacion_cargos": {},
                        "atenuantes_propuestas": [],
                        "peticiones": [],
                        "pruebas_defensa": []
                    }
                
                self.case_history.append({
                    "type": "defense_preparation",
                    "data": defense
                })
                return defense
            except json.JSONDecodeError:
                defense = {
                    "argumentos_defensa": [],
                    "refutacion_cargos": {},
                    "atenuantes_propuestas": [],
                    "peticiones": [],
                    "pruebas_defensa": []
                }
                self.case_history.append({
                    "type": "defense_preparation",
                    "data": defense
                })
                return defense
        except Exception as e:
            console.print(f"[red]Error al preparar la defensa: {str(e)}[/red]")
            return {"error": str(e)}
    
    def generate_document(self, document_type: str, context: Dict) -> str:
        """
        Genera documentos como escritos de defensa, recursos, etc.
        """
        prompt = f"""
        Como defensor del sistema judicial chileno, genera un documento de tipo {document_type} 
        basado en el siguiente contexto:
        
        CONTEXTO:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        El documento debe seguir el formato y estructura oficial de la defensoría penal pública chilena.
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
        Retorna el historial de acciones del defensor en el caso
        """
        return self.case_history
