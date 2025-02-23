"""
Implementación del Agente Juez para el sistema judicial
"""
from typing import Dict, List, Optional
from src.agents.core.base_agent import JudicialAgent
from src.llm.providers.claude_custom import ClaudeClient
from src.agents.core.messaging import MessageType, MessagePriority, Message
import os
from rich.console import Console
from rich.panel import Panel
import json
from datetime import datetime

console = Console()

class JudgeAgent(JudicialAgent):
    """
    Agente que actúa como Juez en el sistema judicial.
    Responsable de:
    - Analizar casos y evidencias
    - Tomar decisiones basadas en la ley
    - Emitir resoluciones y sentencias
    - Gestionar el proceso judicial
    """
    
    def __init__(self, name: str = "Juez"):
        super().__init__(name, {"api_key": os.getenv("ANTHROPIC_API_KEY")})
        self.llm = ClaudeClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.case_history: List[Dict] = []
        
    def analyze_case(self, case_data: Dict) -> Dict:
        """
        Analiza un caso judicial y genera una evaluación inicial
        """
        tipo_analisis = case_data.get("tipo_analisis", "general")
        
        if tipo_analisis == "admisibilidad":
            prompt = f"""
            Como juez del sistema judicial chileno, analiza la admisibilidad de la siguiente querella.
            Debes considerar:
            1. La revisión formal del Secretario
            2. El análisis de mérito del Fiscal
            3. La revisión de garantías del Defensor
            
            Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
            
            {{
                "admisibilidad": {{
                    "decision": "ADMISIBLE/INADMISIBLE",
                    "fundamentos": ["fundamento 1", "fundamento 2", ...],
                    "requisitos_cumplidos": ["requisito 1", "requisito 2", ...],
                    "requisitos_faltantes": ["requisito 1", "requisito 2", ...],
                    "observaciones": ["observacion 1", "observacion 2", ...]
                }},
                "instrucciones_fiscal": {{
                    "diligencias_ordenadas": ["diligencia 1", "diligencia 2", ...],
                    "plazos": ["plazo 1", "plazo 2", ...],
                    "medidas_urgentes": ["medida 1", "medida 2", ...],
                    "instrucciones_especificas": ["instruccion 1", "instruccion 2", ...]
                }}
            }}
            
            DATOS DEL CASO:
            {json.dumps(case_data, indent=2, ensure_ascii=False)}
            
            IMPORTANTE: Tu respuesta debe ser un objeto JSON válido, sin ningún texto adicional antes o después.
            """
        else:
            prompt = f"""
            Como juez del sistema judicial chileno, analiza el siguiente caso y proporciona una evaluación inicial.
            Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
            
            {{
                "evaluacion_preliminar": "descripción detallada",
                "puntos_clave": ["punto 1", "punto 2", ...],
                "pasos_procesales": ["paso 1", "paso 2", ...],
                "complejidades": ["complejidad 1", "complejidad 2", ...]
            }}
            
            DATOS DEL CASO:
            {json.dumps(case_data, indent=2, ensure_ascii=False)}
            
            IMPORTANTE: Tu respuesta debe ser un objeto JSON válido, sin ningún texto adicional antes o después.
            """
        
        try:
            response = self.llm.generate(prompt)
            # Si la respuesta es un string, parsearlo como JSON
            if isinstance(response, str):
                analysis = json.loads(response)
            else:
                analysis = response

            # Guardar en el historial
            self.case_history.append({
                "type": "case_analysis",
                "data": analysis
            })
            return analysis
        except Exception as e:
            console.print(f"[red]Error al analizar el caso: {str(e)}[/red]")
            return {"error": str(e)}
    
    def handle_request(self, message: Message):
        """Maneja una solicitud de otro agente"""
        console.print(f"[blue]Juez recibió solicitud de {message.sender}:[/blue]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
        
        # Procesar la solicitud según su tipo
        if isinstance(message.content, dict) and message.content.get('tipo_solicitud') == 'antecedentes_previos':
            # Simular búsqueda de antecedentes
            response = {
                'antecedentes_encontrados': True,
                'causas_previas': [
                    {'rit': '789-2023', 'tribunal': '4° Juzgado de Garantía', 'estado': 'Terminada'},
                    {'rit': '456-2023', 'tribunal': '2° Juzgado de Garantía', 'estado': 'En curso'}
                ],
                'observaciones': 'Se encontraron antecedentes relevantes'
            }
            
            # Enviar respuesta
            self.send_message(
                receiver=message.sender,
                subject=f"RE: {message.subject}",
                content=response,
                message_type=MessageType.RESPONSE,
                priority=message.priority
            )
            return response
        return None
    
    def handle_notification(self, message: Message):
        """Maneja una notificación de otro agente"""
        console.print(f"[yellow]Juez recibió notificación de {message.sender}:[/yellow]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def handle_decision(self, message: Message):
        """Maneja una decisión de otro agente"""
        console.print(f"[red]Juez recibió decisión de {message.sender}:[/red]")
        console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
    
    def issue_resolution(self, case_id: str, context: Dict) -> Dict:
        """
        Emite una resolución judicial
        """
        prompt = f"""
        Como juez del sistema judicial chileno, emite una resolución para el siguiente contexto:
        
        ANTECEDENTES:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        Genera una resolución judicial que incluya:
        1. Vistos (antecedentes considerados)
        2. Considerando (fundamentos jurídicos)
        3. Resuelvo (decisión)
        
        Formato deseado: JSON
        """
        
        try:
            response = self.llm.generate(prompt)
            resolution = json.loads(response)
            self.case_history.append({
                "type": "resolution",
                "case_id": case_id,
                "data": resolution
            })
            return resolution
        except Exception as e:
            console.print(f"[red]Error al emitir resolución: {str(e)}[/red]")
            return {"error": str(e)}
    
    def review_evidence(self, evidence: List[Dict]) -> Dict:
        """
        Revisa y evalúa las evidencias presentadas
        """
        prompt = f"""
        Como juez del sistema judicial chileno, evalúa las siguientes evidencias.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "evaluacion_evidencias": [
                {{
                    "evidencia": "descripción",
                    "valoracion": "análisis detallado",
                    "admisibilidad": true/false,
                    "observaciones": "comentarios adicionales"
                }}
            ],
            "relevancia_general": "análisis de relevancia",
            "recomendaciones": ["recomendación 1", "recomendación 2", ...]
        }}
        
        EVIDENCIAS PRESENTADAS:
        {json.dumps(evidence, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            # Intentar extraer el JSON de la respuesta
            try:
                # Buscar el primer { y el último }
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    evaluation = json.loads(json_str)
                else:
                    # Si no hay JSON, crear uno con la respuesta como texto
                    evaluation = {
                        "evaluacion_evidencias": [{
                            "evidencia": "Análisis general",
                            "valoracion": response,
                            "admisibilidad": True,
                            "observaciones": "Generado automáticamente"
                        }],
                        "relevancia_general": "Pendiente de evaluación detallada",
                        "recomendaciones": []
                    }
                
                self.case_history.append({
                    "type": "evidence_review",
                    "data": evaluation
                })
                return evaluation
            except json.JSONDecodeError:
                # Si falla el parsing, devolver un JSON con el texto completo
                evaluation = {
                    "evaluacion_evidencias": [{
                        "evidencia": "Análisis general",
                        "valoracion": response,
                        "admisibilidad": True,
                        "observaciones": "Generado automáticamente"
                    }],
                    "relevancia_general": "Pendiente de evaluación detallada",
                    "recomendaciones": []
                }
                self.case_history.append({
                    "type": "evidence_review",
                    "data": evaluation
                })
                return evaluation
        except Exception as e:
            console.print(f"[red]Error al evaluar evidencias: {str(e)}[/red]")
            return {"error": str(e)}
    
    def get_case_history(self) -> List[Dict]:
        """
        Retorna el historial de acciones del juez en el caso
        """
        return self.case_history
        
    def handle_request(self, message: Dict):
        """Maneja solicitudes de otros agentes"""
        content = message['content']
        sender = message['sender']
        
        if content.get('tipo_solicitud') == 'antecedentes_previos':
            # Procesar solicitud de antecedentes
            response = {
                'tipo_respuesta': 'antecedentes_previos',
                'imputado': content['imputado'],
                'antecedentes_encontrados': [
                    {
                        'causa': 'RIT 789-2022',
                        'tribunal': '4° Juzgado de Garantía',
                        'delito': 'Hurto simple',
                        'resultado': 'Condena 61 días',
                        'fecha': '2022-05-15'
                    },
                    {
                        'causa': 'RIT 456-2023',
                        'tribunal': '2° Juzgado de Garantía',
                        'delito': 'Receptación',
                        'resultado': 'Suspensión condicional',
                        'fecha': '2023-08-22'
                    }
                ],
                'observaciones': 'El imputado registra condenas previas por delitos menores'
            }
            
            self.send_message(
                receiver=sender,
                subject='Respuesta a solicitud de antecedentes',
                content=response,
                message_type=MessageType.RESPONSE,
                priority=MessagePriority.HIGH
            )
    
    def handle_notification(self, message: Dict):
        """Maneja notificaciones de otros agentes"""
        content = message['content']
        sender = message['sender']
        
        if content.get('tipo_antecedente') == 'informe_pericial':
            # Analizar el informe pericial
            analysis = {
                'tipo_analisis': 'evaluacion_pericial',
                'informe': content,
                'conclusion': 'El informe pericial no establece vinculación directa del imputado',
                'impacto': 'Favorable para la defensa',
                'recomendaciones': [
                    'Solicitar pericias adicionales',
                    'Evaluar otras líneas de investigación'
                ]
            }
            
            # Registrar el análisis en el historial
            self.case_history.append({
                'type': 'pericial_analysis',
                'data': analysis,
                'timestamp': datetime.now().isoformat()
            })
    
    def handle_decision(self, message: Dict):
        """Maneja decisiones de otros agentes"""
        content = message['content']
        sender = message['sender']
        
        # Registrar la decisión en el historial
        self.case_history.append({
            'type': 'external_decision',
            'sender': sender,
            'data': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def generate_document(self, document_type: str, context: Dict) -> str:
        """
        Genera documentos judiciales como sentencias, resoluciones, etc.
        """
        prompt = f"""
        Como juez del sistema judicial chileno, genera un documento de tipo {document_type} 
        basado en el siguiente contexto:
        
        CONTEXTO:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        El documento debe seguir el formato y estructura oficial del poder judicial chileno.
        """
        
        try:
            response = self.llm.generate(prompt)
            document = {
                "type": "document_generation",
                "document_type": document_type,
                "content": response,
                "timestamp": datetime.now().isoformat()
            }
            
            self.case_history.append(document)
            
            # Notificar a las partes sobre el nuevo documento
            self.notify_update(
                receivers=['ProsecutorAgent', 'DefenderAgent', 'SecretaryAgent'],
                subject=f'Nuevo documento judicial: {document_type}',
                content=document,
                priority=MessagePriority.HIGH
            )
            
            return response
        except Exception as e:
            console.print(f"[red]Error al generar documento: {str(e)}[/red]")
            return f"Error: {str(e)}"
