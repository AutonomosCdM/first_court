"""
Implementación del Agente Secretario para el sistema judicial
"""
from typing import Dict, List, Optional
from src.agents.core.base_agent import JudicialAgent
from src.agents.core.messaging import Message, MessageType
from src.llm.providers.claude_custom import ClaudeClient
from src.integrations.drive_docling_integration import DriveDoclingIntegration
import os
from rich.console import Console
from rich.panel import Panel
import json
from datetime import datetime, timedelta

console = Console()

class SecretaryAgent(JudicialAgent):
    """
    Agente que actúa como Secretario en el sistema judicial.
    Responsable de:
    - Gestionar la tramitación de causas
    - Generar resoluciones y documentos
    - Mantener el registro de actuaciones
    - Coordinar audiencias
    - Notificar a las partes
    - Integración con Google Drive y procesamiento de documentos
    """
    
    def __init__(self, name: str = "Secretario"):
        super().__init__(name, {"api_key": os.getenv("ANTHROPIC_API_KEY")})
        self.llm = ClaudeClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.drive_integration = DriveDoclingIntegration()
    
    def process_drive_documents(self, folder_id: Optional[str] = None) -> List[Dict]:
        """
        Procesa documentos desde Google Drive
        
        Args:
            folder_id (Optional[str]): ID de la carpeta en Google Drive
        
        Returns:
            Lista de documentos procesados
        """
        try:
            processed_docs = self.drive_integration.process_drive_documents(folder_id)
            
            # Registrar procesamiento de documentos en el historial
            self.case_history.append({
                "type": "drive_document_processing",
                "total_documents": len(processed_docs),
                "documents": [
                    {
                        "file_name": doc.get('drive_metadata', {}).get('name', 'Unknown'),
                        "status": "processed" if 'error' not in doc else "error"
                    } for doc in processed_docs
                ],
                "timestamp": datetime.now().isoformat()
            })
            
            return processed_docs
        except Exception as e:
            console.print(f"[red]Error al procesar documentos de Drive: {str(e)}[/red]")
            return []
    
    def generate_drive_document_summary(self, folder_id: Optional[str] = None) -> Dict:
        """
        Genera un resumen de los documentos procesados desde Drive
        
        Args:
            folder_id (Optional[str]): ID de la carpeta en Google Drive
        
        Returns:
            Resumen de documentos procesados
        """
        processed_docs = self.process_drive_documents(folder_id)
        
        return {
            "total_documents": len(processed_docs),
            "document_summaries": [
                {
                    "file_name": doc.get('drive_metadata', {}).get('name', 'Unknown'),
                    "file_type": doc.get('drive_metadata', {}).get('mimeType', 'Unknown'),
                    "prosecutor_analysis": doc.get('prosecutor_analysis', {}),
                    "defender_analysis": doc.get('defender_analysis', {}),
                    "error": doc.get('error')
                } for doc in processed_docs
            ]
        }
    
    def list_drive_documents(self, folder_id: Optional[str] = None) -> List[Dict]:
        """
        Lista documentos en una carpeta de Google Drive
        
        Args:
            folder_id (Optional[str]): ID de la carpeta en Google Drive
        
        Returns:
            Lista de documentos en la carpeta
        """
        try:
            return self.drive_integration.list_legal_documents(folder_id)
        except Exception as e:
            console.print(f"[red]Error al listar documentos de Drive: {str(e)}[/red]")
            return []
    
    def analyze_case(self, case_data: Dict) -> Dict:
        """Implementación del método abstracto de JudicialAgent"""
        return self.review_case_status(case_data)
    
    def review_case_status(self, case_data: Dict) -> Dict:
        """
        Revisa el estado actual de la causa y genera un informe
        """
        prompt = f"""
        Como secretario del tribunal, analiza el siguiente caso y proporciona un informe de estado.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "estado_actual": "descripción del estado procesal",
            "ultimas_actuaciones": ["actuación 1", "actuación 2", ...],
            "proximas_actuaciones": ["actuación 1", "actuación 2", ...],
            "plazos_vigentes": [
                {{"actuacion": "nombre", "fecha_limite": "fecha", "estado": "vigente/vencido"}}
            ],
            "documentos_pendientes": ["documento 1", "documento 2", ...],
            "notificaciones_pendientes": ["notificación 1", "notificación 2", ...]
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
                    status = json.loads(json_str)
                else:
                    status = {
                        "estado_actual": response,
                        "ultimas_actuaciones": [],
                        "proximas_actuaciones": [],
                        "plazos_vigentes": [],
                        "documentos_pendientes": [],
                        "notificaciones_pendientes": []
                    }
            except json.JSONDecodeError:
                status = {
                    "estado_actual": response,
                    "ultimas_actuaciones": [],
                    "proximas_actuaciones": [],
                    "plazos_vigentes": [],
                    "documentos_pendientes": [],
                    "notificaciones_pendientes": []
                }
            
            self.case_history.append({
                "type": "case_status_review",
                "data": status,
                "timestamp": datetime.now().isoformat()
            })
            return status
        except Exception as e:
            console.print(f"[red]Error al revisar estado de la causa: {str(e)}[/red]")
            return {"error": str(e)}
    
    def handle_request(self, message: Message):
        """Maneja una solicitud de otro agente"""
        try:
            console.print(f"[blue]Secretario recibió solicitud de {message.sender}:[/blue]")
            console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
            
            # Procesar la solicitud según su tipo
            if isinstance(message.content, dict) and message.content.get('tipo_solicitud') == 'acceso_expediente':
                # Simular búsqueda de expediente
                response = {
                    'acceso_concedido': True,
                    'expediente': {
                        'rit': message.content.get('rit', 'No especificado'),
                        'fojas': 125,
                        'estado': 'Activo',
                        'ubicacion': 'Archivo Digital',
                        'observaciones': 'Expediente disponible para consulta'
                    }
                }
                
                # Enviar respuesta
                self.send_message(
                    receiver=message.sender,
                    subject=f"RE: {message.subject}",
                    content=response,
                    message_type=MessageType.RESPONSE,
                    priority=message.priority
                )
        except Exception as e:
            console.print(f"[red]Error al procesar solicitud: {str(e)}[/red]")
    
    def handle_notification(self, message: Message):
        """Maneja una notificación de otro agente"""
        try:
            console.print(f"[yellow]Secretario recibió notificación de {message.sender}:[/yellow]")
            console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
        except Exception as e:
            console.print(f"[red]Error al procesar notificación: {str(e)}[/red]")
    
    def handle_decision(self, message: Message):
        """Maneja una decisión de otro agente"""
        try:
            console.print(f"[red]Secretario recibió decisión de {message.sender}:[/red]")
            console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
        except Exception as e:
            console.print(f"[red]Error al procesar decisión: {str(e)}[/red]")
    
    def generate_resolution(self, resolution_type: str, context: Dict) -> Dict:
        """
        Genera una resolución judicial según el tipo y contexto
        """
        prompt = f"""
        Como secretario del tribunal, genera una resolución de tipo {resolution_type}.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "tipo_resolucion": "tipo específico",
            "encabezado": "texto del encabezado",
            "vistos": ["considerando 1", "considerando 2", ...],
            "considerando": ["considerando 1", "considerando 2", ...],
            "resuelvo": ["punto 1", "punto 2", ...],
            "notificaciones": ["parte 1", "parte 2", ...],
            "fecha": "fecha actual",
            "firma": "cargo del firmante"
        }}
        
        CONTEXTO:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            try:
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    resolution = json.loads(json_str)
                else:
                    resolution = {
                        "tipo_resolucion": resolution_type,
                        "encabezado": "",
                        "vistos": [],
                        "considerando": [],
                        "resuelvo": [response],
                        "notificaciones": [],
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                        "firma": self.name
                    }
            except json.JSONDecodeError:
                resolution = {
                    "tipo_resolucion": resolution_type,
                    "encabezado": "",
                    "vistos": [],
                    "considerando": [],
                    "resuelvo": [response],
                    "notificaciones": [],
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "firma": self.name
                }
            
            self.case_history.append({
                "type": "resolution_generation",
                "resolution_type": resolution_type,
                "data": resolution,
                "timestamp": datetime.now().isoformat()
            })
            return resolution
        except Exception as e:
            console.print(f"[red]Error al generar resolución: {str(e)}[/red]")
            return {"error": str(e)}
    
    def schedule_hearing(self, hearing_type: str, case_data: Dict, participants: List[Dict]) -> Dict:
        """
        Programa una audiencia según tipo y participantes
        """
        prompt = f"""
        Como secretario del tribunal, programa una audiencia de tipo {hearing_type}.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "tipo_audiencia": "tipo específico",
            "fecha_hora": "fecha y hora propuesta",
            "sala": "número o identificación de la sala",
            "participantes": ["participante 1", "participante 2", ...],
            "documentos_requeridos": ["documento 1", "documento 2", ...],
            "notificaciones": ["notificación 1", "notificación 2", ...],
            "observaciones": "observaciones importantes"
        }}
        
        DATOS DEL CASO:
        {json.dumps(case_data, indent=2, ensure_ascii=False)}
        
        PARTICIPANTES:
        {json.dumps(participants, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            try:
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    schedule = json.loads(json_str)
                else:
                    schedule = {
                        "tipo_audiencia": hearing_type,
                        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "sala": "Por asignar",
                        "participantes": [p["nombre"] for p in participants],
                        "documentos_requeridos": [],
                        "notificaciones": [],
                        "observaciones": response
                    }
            except json.JSONDecodeError:
                schedule = {
                    "tipo_audiencia": hearing_type,
                    "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "sala": "Por asignar",
                    "participantes": [p["nombre"] for p in participants],
                    "documentos_requeridos": [],
                    "notificaciones": [],
                    "observaciones": response
                }
            
            self.case_history.append({
                "type": "hearing_scheduling",
                "hearing_type": hearing_type,
                "data": schedule,
                "timestamp": datetime.now().isoformat()
            })
            return schedule
        except Exception as e:
            console.print(f"[red]Error al programar audiencia: {str(e)}[/red]")
            return {"error": str(e)}
    
    def generate_notification(self, notification_type: str, recipient: Dict, content: Dict) -> Dict:
        """
        Genera una notificación según tipo y destinatario
        """
        prompt = f"""
        Como secretario del tribunal, genera una notificación de tipo {notification_type}.
        Debes responder SOLO con un objeto JSON válido que contenga los siguientes campos:
        
        {{
            "tipo_notificacion": "tipo específico",
            "destinatario": {{
                "nombre": "nombre completo",
                "cargo": "cargo o rol",
                "direccion": "dirección"
            }},
            "contenido": "texto de la notificación",
            "fecha_emision": "fecha actual",
            "fecha_notificacion": "fecha propuesta",
            "forma_notificacion": "método de notificación",
            "documentos_adjuntos": ["documento 1", "documento 2", ...]
        }}
        
        DESTINATARIO:
        {json.dumps(recipient, indent=2, ensure_ascii=False)}
        
        CONTENIDO:
        {json.dumps(content, indent=2, ensure_ascii=False)}
        """
        
        try:
            response = self.llm.generate(prompt)
            try:
                start = response.find('{')
                end = response.rfind('}')
                if start >= 0 and end >= 0:
                    json_str = response[start:end+1]
                    notification = json.loads(json_str)
                else:
                    notification = {
                        "tipo_notificacion": notification_type,
                        "destinatario": recipient,
                        "contenido": response,
                        "fecha_emision": datetime.now().strftime("%Y-%m-%d"),
                        "fecha_notificacion": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                        "forma_notificacion": "Por determinar",
                        "documentos_adjuntos": []
                    }
            except json.JSONDecodeError:
                notification = {
                    "tipo_notificacion": notification_type,
                    "destinatario": recipient,
                    "contenido": response,
                    "fecha_emision": datetime.now().strftime("%Y-%m-%d"),
                    "fecha_notificacion": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "forma_notificacion": "Por determinar",
                    "documentos_adjuntos": []
                }
            
            self.case_history.append({
                "type": "notification_generation",
                "notification_type": notification_type,
                "data": notification,
                "timestamp": datetime.now().isoformat()
            })
            return notification
        except Exception as e:
            console.print(f"[red]Error al generar notificación: {str(e)}[/red]")
            return {"error": str(e)}
    
    def generate_document(self, document_type: str, context: Dict) -> str:
        """
        Genera documentos oficiales del tribunal
        """
        prompt = f"""
        Como secretario del tribunal, genera un documento de tipo {document_type} 
        basado en el siguiente contexto:
        
        CONTEXTO:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        El documento debe seguir el formato y estructura oficial del poder judicial chileno.
        """
        
        try:
            response = self.llm.generate(prompt)
            self.case_history.append({
                "type": "document_generation",
                "document_type": document_type,
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            return response
        except Exception as e:
            console.print(f"[red]Error al generar documento: {str(e)}[/red]")
            return f"Error: {str(e)}"
    
    def get_case_history(self) -> List[Dict]:
        """
        Retorna el historial de actuaciones del secretario en el caso
        """
        return self.case_history
