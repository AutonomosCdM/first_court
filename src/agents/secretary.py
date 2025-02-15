"""Secretary agent for managing calendar and scheduling."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from src.integrations.google_calendar import GoogleCalendarClient
from src.integrations.google_meet import GoogleMeetClient
from src.integrations.gmail import GmailClient

class SecretaryAgent:
    """Agent responsible for managing calendar and scheduling."""
    
    def __init__(self):
        self.calendar_client = GoogleCalendarClient()
        self.meet_client = GoogleMeetClient()
        self.gmail_client = GmailClient()
    
    def schedule_hearing(self, case_data: Dict[str, Any], title: str,
                        preferred_date: datetime, duration_minutes: int = 60,
                        description: Optional[str] = None,
                        virtual: bool = True) -> Dict[str, Any]:
        """Schedule a court hearing with case data."""
        # Extraer emails de participantes
        attendees = [p['email'] for p in case_data['participantes']]
        
        # Crear reunión virtual si es necesario
        if virtual:
            meeting = self.meet_client.create_meeting(
                title=f"Audiencia: {title} - Caso {case_data['id']}",
                start_time=preferred_date,
                duration_minutes=duration_minutes,
                attendees=attendees
            )
            meet_link = meeting.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri')
            if description:
                description = f"{description}\n\nEnlace de videoconferencia: {meet_link}"
        
        # Crear evento en calendario
        event = self.calendar_client.create_event(
            summary=f"Audiencia: {title} - Caso {case_data['id']}",
            start_time=preferred_date,
            end_time=preferred_date + timedelta(minutes=duration_minutes),
            description=description,
            attendees=attendees
        )
        
        # Enviar notificaciones por email
        for participant in case_data['participantes']:
            self.gmail_client.send_email(
                to=participant['email'],
                subject=f"Citación a Audiencia - Caso {case_data['id']}",
                body=f"Estimado/a {participant['nombre']},\n\n"
                     f"Se le cita a la audiencia '{title}' del caso {case_data['id']},"
                     f" programada para el {preferred_date.strftime('%d/%m/%Y %H:%M')}."
                     f"\n\nDuración estimada: {duration_minutes} minutos."
                     + (f"\n\nEnlace de videoconferencia: {meet_link}" if virtual else "")
                     + f"\n\nSaludos cordiales,\nSistema Judicial"
            )
        
        return event
    
    def get_upcoming_hearings(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming court hearings."""
        time_min = datetime.now(UTC)
        time_max = time_min + timedelta(days=days)
        
        return self.calendar_client.get_events(
            time_min=time_min,
            time_max=time_max
        )
