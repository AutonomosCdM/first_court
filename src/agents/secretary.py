"""Implementación del Agente Secretario para el sistema judicial"""
from typing import Dict, List, Optional
from src.agents.core.base_agent import JudicialAgent
from src.agents.core.messaging import Message, MessageType
from src.llm.providers.deepseek_custom import DeepseekClient
from src.integrations.google_calendar import GoogleCalendarClient
from src.integrations.gmail import GmailClient
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
    """
    
    def __init__(self, name: str = "Secretario"):
        super().__init__(name, {"api_key": os.getenv("DEEPSEEK_API_KEY")})
        self.llm = DeepseekClient(api_key=os.getenv("DEEPSEEK_API_KEY"))
        self.calendar = GoogleCalendarClient()
        self.gmail = GmailClient()
    
    def analyze_case(self, case_data: Dict) -> Dict:
        """Implementación del método abstracto de JudicialAgent"""
        return self.review_case_status(case_data)
    
    def schedule_hearing(self, case_data: Dict, title: str, preferred_date: datetime = None,
                    duration_minutes: int = 60, description: str = None, virtual: bool = True) -> Dict:
        """
        Agenda una nueva audiencia para un caso.
        
        Args:
            case_data: Datos del caso
            title: Título de la audiencia
            preferred_date: Fecha preferida (opcional)
            duration_minutes: Duración en minutos
            description: Descripción detallada
            virtual: Si es True, será una audiencia virtual
            
        Returns:
            Dict con la información del evento creado
        """
        # Obtener participantes del caso
        attendees = self._get_case_participants_emails(case_data)
        
        # Si no se especifica fecha, buscar el próximo horario disponible
        if not preferred_date:
            try:
                preferred_date = self.calendar.find_next_available_slot(
                    duration_minutes=duration_minutes
                )
            except ValueError as e:
                console.print(f"[red]Error al buscar horario disponible: {str(e)}[/red]")
                return {"error": str(e)}
        
        # Preparar descripción completa
        full_description = f"""
        Causa: {case_data.get('id', 'N/A')}
        Tipo de Audiencia: {title}
        
        {description or ''}
        
        Participantes:
        {chr(10).join([f'- {p.get("nombre", "")} ({p.get("rol", "")})' for p in case_data.get("participantes", [])])}
        """
        
        try:
            # Crear el evento en el calendario
            event = self.calendar.create_hearing(
                title=f"[{case_data.get('id', 'N/A')}] {title}",
                start_time=preferred_date,
                duration_minutes=duration_minutes,
                description=full_description,
                attendees=attendees,
                virtual_meeting=virtual
            )
            
            # Enviar notificaciones por email
            self.gmail.send_hearing_notification(
                to=attendees,
                case_data=case_data,
                hearing_data={
                    'title': title,
                    'datetime': preferred_date.isoformat(),
                    'duration': duration_minutes,
                    'virtual': virtual,
                    'meet_link': event.get('hangoutLink')
                },
                notification_type='scheduled'
            )
            
            # Registrar en el historial del caso
            self.case_history.append({
                "type": "hearing_scheduled",
                "data": {
                    "event_id": event.get('id'),
                    "title": title,
                    "datetime": preferred_date.isoformat(),
                    "duration": duration_minutes,
                    "virtual": virtual
                },
                "timestamp": datetime.now().isoformat()
            })
            
            return event
            
        except Exception as e:
            console.print(f"[red]Error al agendar audiencia: {str(e)}[/red]")
            return {"error": str(e)}
    
    def _get_case_participants_emails(self, case_data: Dict) -> List[str]:
        """
        Extrae los correos electrónicos de los participantes del caso.
        """
        emails = []
        for participant in case_data.get("participantes", []):
            email = participant.get("email")
            if email:
                emails.append(email)
        return emails
    
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
    
    def reschedule_hearing(self, case_data: Dict, event_id: str, new_date: datetime) -> Dict:
        """
        Reagenda una audiencia existente.
        
        Args:
            case_data: Datos del caso
            event_id: ID del evento en Google Calendar
            new_date: Nueva fecha y hora para la audiencia
            
        Returns:
            Dict con la información del evento actualizado
        """
        try:
            # Obtener participantes del caso
            attendees = self._get_case_participants_emails(case_data)
            
            # Actualizar el evento en el calendario
            event = self.calendar.update_hearing(
                event_id=event_id,
                updates={
                    'start': {
                        'dateTime': new_date.isoformat(),
                        'timeZone': 'America/Santiago',
                    },
                    'end': {
                        'dateTime': (new_date + timedelta(minutes=60)).isoformat(),
                        'timeZone': 'America/Santiago',
                    }
                }
            )
            
            # Enviar notificaciones por email
            self.gmail.send_hearing_notification(
                to=attendees,
                case_data=case_data,
                hearing_data={
                    'title': event.get('summary', '').split(']')[-1].strip(),
                    'datetime': new_date.isoformat(),
                    'duration': 60,  # Por ahora hardcodeado
                    'virtual': 'hangoutLink' in event,
                    'meet_link': event.get('hangoutLink')
                },
                notification_type='rescheduled'
            )
            
            # Registrar en el historial del caso
            self.case_history.append({
                "type": "hearing_rescheduled",
                "data": {
                    "event_id": event_id,
                    "new_datetime": new_date.isoformat(),
                },
                "timestamp": datetime.now().isoformat()
            })
            
            return event
            
        except Exception as e:
            console.print(f"[red]Error al reagendar audiencia: {str(e)}[/red]")
            return {"error": str(e)}
    
    def cancel_hearing(self, case_data: Dict, event_id: str) -> Dict:
        """
        Cancela una audiencia existente.
        
        Args:
            case_data: Datos del caso
            event_id: ID del evento en Google Calendar
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Obtener participantes del caso
            attendees = self._get_case_participants_emails(case_data)
            
            # Obtener datos del evento antes de cancelarlo
            event = self.calendar.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Enviar notificaciones por email
            self.gmail.send_hearing_notification(
                to=attendees,
                case_data=case_data,
                hearing_data={
                    'title': event.get('summary', '').split(']')[-1].strip(),
                    'datetime': event.get('start', {}).get('dateTime'),
                    'duration': 60,  # Por ahora hardcodeado
                    'virtual': 'hangoutLink' in event,
                    'meet_link': event.get('hangoutLink')
                },
                notification_type='cancelled'
            )
            
            # Cancelar el evento
            self.calendar.cancel_hearing(event_id)
            
            # Registrar en el historial del caso
            self.case_history.append({
                "type": "hearing_cancelled",
                "data": {
                    "event_id": event_id,
                    "cancelled_at": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "cancelled", "event_id": event_id}
            
        except Exception as e:
            console.print(f"[red]Error al cancelar audiencia: {str(e)}[/red]")
            return {"error": str(e)}

    def generate_document(self, document_type: str, case_data: Dict) -> str:
        """Implementación del método abstracto de JudicialAgent"""
        return "Documento generado"

    def handle_request(self, message: Message):
        """Maneja una solicitud de otro agente"""
        try:
            console.print(f"[blue]Secretario recibió solicitud de {message.sender}:[/blue]")
            console.print(Panel(json.dumps(message.content, indent=2, ensure_ascii=False)))
            
            # Procesar la solicitud según su tipo
            if message.type == MessageType.CASE_STATUS:
                return self.review_case_status(message.content)
            else:
                return {"error": f"Tipo de mensaje no soportado: {message.type}"}
                
        except Exception as e:
            console.print(f"[red]Error al procesar solicitud: {str(e)}[/red]")
            return {"error": str(e)}
