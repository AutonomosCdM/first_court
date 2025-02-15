"""
Módulo de integración con Google Calendar para la gestión de audiencias y eventos judiciales.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

# Si modificas estos scopes, elimina el archivo token.pickle
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarClient:
    """Cliente para interactuar con Google Calendar API"""
    
    def __init__(self):
        """Inicializa el cliente de Google Calendar"""
        self.creds = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self.service = None
    
    def _authenticate(self):
        """Maneja el proceso de autenticación con Google Calendar"""
        # El archivo token.pickle almacena los tokens de acceso y actualización del usuario
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # Si no hay credenciales válidas disponibles, permite al usuario iniciar sesión
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Usar el archivo credentials.json existente
                credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'credentials.json')
                if not os.path.exists(credentials_path):
                    raise ValueError(
                        'El archivo credentials.json no existe en la ubicación esperada. '
                        'Por favor, asegúrate de que el archivo esté presente en la raíz del proyecto.'
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=8085)
            
            # Guarda las credenciales para la próxima ejecución
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def get_service(self):
        """Obtiene el servicio de Calendar, autenticando si es necesario"""
        if not self.service:
            self._authenticate()
        return self.service

    def create_hearing(self, 
                      title: str,
                      start_time: datetime,
                      duration_minutes: int = 60,
                      description: str = None,
                      attendees: List[str] = None,
                      location: str = None,
                      virtual_meeting: bool = True) -> Dict:
        """
        Crea un evento para una audiencia en el calendario.
        
        Args:
            title: Título de la audiencia
            start_time: Fecha y hora de inicio
            duration_minutes: Duración en minutos
            description: Descripción detallada
            attendees: Lista de correos electrónicos de los participantes
            location: Ubicación física (si aplica)
            virtual_meeting: Si es True, agrega una videollamada de Google Meet
        
        Returns:
            Dict con la información del evento creado
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        event = {
            'summary': title,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Santiago',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Santiago',
            },
            'attendees': [{'email': email} for email in (attendees or [])],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        if virtual_meeting:
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': f"hearing_{start_time.strftime('%Y%m%d_%H%M')}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        
        event = self.get_service().events().insert(
            calendarId=self.calendar_id,
            body=event,
            conferenceDataVersion=1 if virtual_meeting else 0,
            sendUpdates='all'
        ).execute()
        
        return event
    
    def check_availability(self, 
                         start_time: datetime,
                         end_time: datetime) -> bool:
        """
        Verifica la disponibilidad en el calendario para un horario específico.
        
        Args:
            start_time: Fecha y hora de inicio
            end_time: Fecha y hora de fin
        
        Returns:
            bool indicando si el horario está disponible
        """
        events_result = self.get_service().events().list(
            calendarId=self.calendar_id,
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return len(events_result.get('items', [])) == 0
    
    def find_next_available_slot(self,
                               duration_minutes: int = 60,
                               start_from: datetime = None,
                               working_hours: tuple = (9, 18)) -> datetime:
        """
        Encuentra el próximo horario disponible para una audiencia.
        
        Args:
            duration_minutes: Duración necesaria en minutos
            start_from: Fecha desde la cual buscar (default: ahora)
            working_hours: Tupla con hora inicio y fin de la jornada laboral
        
        Returns:
            datetime con el próximo horario disponible
        """
        if not start_from:
            start_from = datetime.now()
        
        # Ajustar a hora de inicio si está fuera de horario laboral
        current = start_from.replace(
            hour=working_hours[0],
            minute=0,
            second=0,
            microsecond=0
        )
        if start_from.hour >= working_hours[1]:
            current += timedelta(days=1)
        
        max_days = 60  # Límite de búsqueda
        days_checked = 0
        
        while days_checked < max_days:
            while current.hour < working_hours[1]:
                end_time = current + timedelta(minutes=duration_minutes)
                if self.check_availability(current, end_time):
                    return current
                
                current += timedelta(minutes=30)  # Intentar cada 30 minutos
            
            # Pasar al siguiente día laboral
            current = (current + timedelta(days=1)).replace(
                hour=working_hours[0],
                minute=0
            )
            days_checked += 1
        
        raise ValueError("No se encontraron horarios disponibles en los próximos 60 días")
    
    def update_hearing(self,
                      event_id: str,
                      updates: Dict) -> Dict:
        """
        Actualiza los detalles de una audiencia existente.
        
        Args:
            event_id: ID del evento a actualizar
            updates: Diccionario con los campos a actualizar
        
        Returns:
            Dict con la información actualizada del evento
        """
        event = self.get_service().events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()
        
        event.update(updates)
        
        updated_event = self.get_service().events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event,
            sendUpdates='all'
        ).execute()
        
        return updated_event
    
    def cancel_hearing(self, event_id: str) -> None:
        """
        Cancela una audiencia programada.
        
        Args:
            event_id: ID del evento a cancelar
        """
        self.get_service().events().delete(
            calendarId=self.calendar_id,
            eventId=event_id,
            sendUpdates='all'
        ).execute()
