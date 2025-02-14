"""
Módulo de integración con Google Meet para la gestión de audiencias virtuales.
"""
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime, timedelta
import json
from pathlib import Path

# Si modificas estos scopes, elimina el archivo token.pickle
SCOPES = [
    'https://www.googleapis.com/auth/calendar',  # Para crear eventos con Meet
    'https://www.googleapis.com/auth/drive',     # Para guardar grabaciones
]

class GoogleMeetClient:
    """Cliente para interactuar con Google Meet a través de Calendar API"""
    
    def __init__(self):
        """Inicializa el cliente de Google Meet"""
        self.creds = None
        self.calendar_service = None
        self.drive_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Maneja el proceso de autenticación"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
    
    def create_meeting(self, 
                      title: str,
                      start_time: datetime,
                      duration_minutes: int = 60,
                      participants: List[Dict] = None,
                      case_data: Dict = None) -> Dict:
        """
        Crea una reunión de Google Meet
        
        Args:
            title: Título de la reunión
            start_time: Fecha y hora de inicio
            duration_minutes: Duración en minutos
            participants: Lista de participantes con sus roles
            case_data: Datos del caso asociado
            
        Returns:
            Dict con la información de la reunión creada
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Configurar la reunión
        event = {
            'summary': title,
            'description': self._generate_description(case_data),
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Santiago',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Santiago',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"hearing_{case_data['id']}_{start_time.strftime('%Y%m%d_%H%M')}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
            'attendees': self._format_participants(participants),
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ]
            }
        }
        
        # Crear el evento con la reunión
        event = self.calendar_service.events().insert(
            calendarId='primary',
            conferenceDataVersion=1,
            body=event,
            sendUpdates='all'
        ).execute()
        
        return {
            'event_id': event['id'],
            'meet_link': event['conferenceData']['entryPoints'][0]['uri'],
            'start_time': event['start']['dateTime'],
            'end_time': event['end']['dateTime']
        }
    
    def update_meeting(self,
                      event_id: str,
                      title: str = None,
                      start_time: datetime = None,
                      duration_minutes: int = None,
                      participants: List[Dict] = None) -> Dict:
        """
        Actualiza una reunión existente
        
        Args:
            event_id: ID del evento a actualizar
            title: Nuevo título (opcional)
            start_time: Nueva fecha/hora (opcional)
            duration_minutes: Nueva duración (opcional)
            participants: Nueva lista de participantes (opcional)
            
        Returns:
            Dict con la información actualizada
        """
        # Obtener evento actual
        event = self.calendar_service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # Actualizar campos si se proporcionan
        if title:
            event['summary'] = title
        
        if start_time:
            event['start']['dateTime'] = start_time.isoformat()
            if duration_minutes:
                end_time = start_time + timedelta(minutes=duration_minutes)
                event['end']['dateTime'] = end_time.isoformat()
        
        if participants:
            event['attendees'] = self._format_participants(participants)
        
        # Actualizar el evento
        updated_event = self.calendar_service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event,
            sendUpdates='all'
        ).execute()
        
        return {
            'event_id': updated_event['id'],
            'meet_link': updated_event['conferenceData']['entryPoints'][0]['uri'],
            'start_time': updated_event['start']['dateTime'],
            'end_time': updated_event['end']['dateTime']
        }
    
    def get_meeting_status(self, event_id: str) -> Dict:
        """
        Obtiene el estado actual de una reunión
        
        Args:
            event_id: ID del evento
            
        Returns:
            Dict con el estado de la reunión
        """
        event = self.calendar_service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        return {
            'status': event['status'],
            'meet_link': event['conferenceData']['entryPoints'][0]['uri'],
            'start_time': event['start']['dateTime'],
            'end_time': event['end']['dateTime'],
            'attendees': event.get('attendees', [])
        }
    
    def _generate_description(self, case_data: Dict) -> str:
        """Genera la descripción de la reunión"""
        return f"""
        Audiencia Virtual - Tribunal Autónomo
        
        Causa: {case_data.get('id')}
        Tipo: {case_data.get('tipo')}
        Materia: {case_data.get('materia')}
        
        Esta es una audiencia oficial del Tribunal Autónomo.
        La sesión será grabada para fines oficiales.
        
        Notas:
        - Ingrese 5 minutos antes del inicio
        - Mantenga su micrófono en silencio cuando no esté hablando
        - Use un fondo neutro y apropiado
        - Asegure una conexión estable a internet
        """
    
    def _format_participants(self, participants: List[Dict]) -> List[Dict]:
        """Formatea la lista de participantes para el evento"""
        return [
            {
                'email': p['email'],
                'responseStatus': 'needsAction',
                'optional': False
            }
            for p in participants if p.get('email')
        ]
