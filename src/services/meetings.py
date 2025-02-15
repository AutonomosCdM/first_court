"""
Servicio para la gestión de videollamadas con Google Meet.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.config import settings
from src.monitoring.logger import Logger
from src.monitoring.metrics import meeting_metrics

logger = Logger(__name__)

class MeetingService:
    """Servicio para gestionar videollamadas con Google Meet."""

    def __init__(self):
        """Inicializar servicio de Meet."""
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/meetings.space.created'
        ]
        
    async def create_meeting(self, user_credentials: Dict) -> Dict:
        """Crear una nueva reunión de Meet.
        
        Args:
            user_credentials: Credenciales del usuario de Google
            
        Returns:
            Dict con información de la reunión
        """
        try:
            with meeting_metrics.measure_latency("create_meeting"):
                # Crear credenciales
                credentials = Credentials(
                    token=user_credentials['token'],
                    refresh_token=user_credentials['refresh_token'],
                    token_uri=settings.GOOGLE_TOKEN_URI,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    scopes=self.scopes
                )

                # Crear servicio de Calendar
                service = build('calendar', 'v3', credentials=credentials)
                
                # Crear evento con Meet
                event = {
                    'summary': 'First Court - Videollamada',
                    'start': {
                        'dateTime': datetime.utcnow().isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                        'timeZone': 'UTC',
                    },
                    'conferenceData': {
                        'createRequest': {
                            'requestId': f"firstcourt-{datetime.utcnow().timestamp()}",
                            'conferenceSolutionKey': {
                                'type': 'hangoutsMeet'
                            }
                        }
                    }
                }
                
                # Insertar evento
                event = service.events().insert(
                    calendarId='primary',
                    body=event,
                    conferenceDataVersion=1
                ).execute()
                
                # Extraer información de Meet
                meeting_url = event['conferenceData']['entryPoints'][0]['uri']
                meeting_id = event['conferenceData']['conferenceId']
                
                return {
                    'meetingUrl': meeting_url,
                    'meetingId': meeting_id,
                    'expiresAt': event['end']['dateTime']
                }
                
        except Exception as e:
            logger.error(f"Error creating Meet meeting: {str(e)}")
            raise

    async def get_meeting_state(self, meeting_id: str, user_credentials: Dict) -> Dict:
        """Obtener estado de una reunión.
        
        Args:
            meeting_id: ID de la reunión
            user_credentials: Credenciales del usuario
            
        Returns:
            Estado actual de la reunión
        """
        try:
            with meeting_metrics.measure_latency("get_meeting_state"):
                # Crear credenciales
                credentials = Credentials(
                    token=user_credentials['token'],
                    refresh_token=user_credentials['refresh_token'],
                    token_uri=settings.GOOGLE_TOKEN_URI,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    scopes=self.scopes
                )

                # Crear servicio de Calendar
                service = build('calendar', 'v3', credentials=credentials)
                
                # Buscar evento por conferenceId
                now = datetime.utcnow()
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=now.isoformat() + 'Z',
                    timeMax=(now + timedelta(days=1)).isoformat() + 'Z',
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                # Encontrar evento con el meeting_id
                for event in events_result.get('items', []):
                    if event.get('conferenceData', {}).get('conferenceId') == meeting_id:
                        conference_data = event['conferenceData']
                        return {
                            'isActive': True,
                            'url': conference_data['entryPoints'][0]['uri'],
                            'participants': len(conference_data.get('participants', [])),
                            'startedAt': event['start']['dateTime']
                        }
                
                return {
                    'isActive': False,
                    'url': '',
                    'participants': 0,
                    'startedAt': None
                }
                
        except Exception as e:
            logger.error(f"Error getting meeting state: {str(e)}")
            raise
