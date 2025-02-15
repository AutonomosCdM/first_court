"""Google Calendar integration module."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.auth.auth_manager import AuthManager

class GoogleCalendarClient:
    """Client for interacting with Google Calendar API."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.calendar_id = 'primary'  # Can be overridden in config
        self.service = None
        self._init_service()
    
    def _init_service(self):
        """Initialize the Calendar service."""
        credentials = self.auth_manager.get_credentials()
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def create_event(self, summary: str, start_time: datetime, 
                    end_time: datetime, description: str = None,
                    attendees: List[str] = None) -> Dict[str, Any]:
        """Create a new calendar event."""
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Santiago'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Santiago'
            },
        }
        
        if description:
            event['description'] = description
            
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
            
        return self.service.events().insert(
            calendarId=self.calendar_id,
            body=event,
            sendUpdates='all'
        ).execute()
    
    def get_events(self, time_min: Optional[datetime] = None,
                  time_max: Optional[datetime] = None,
                  max_results: int = 10) -> List[Dict[str, Any]]:
        """Get calendar events within the specified time range."""
        if not time_min:
            time_min = datetime.utcnow()
        if not time_max:
            time_max = time_min + timedelta(days=7)
            
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=time_min.isoformat() + 'Z',
            timeMax=time_max.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
