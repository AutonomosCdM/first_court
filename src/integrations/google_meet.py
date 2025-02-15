"""Google Meet integration module."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.auth.auth_manager import AuthManager

class GoogleMeetClient:
    """Client for interacting with Google Meet API."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.calendar_service = None
        self._init_service()
    
    def _init_service(self):
        """Initialize the Calendar service for Meet integration."""
        credentials = self.auth_manager.get_credentials()
        self.calendar_service = build('calendar', 'v3', credentials=credentials)
    
    def create_meeting(self, title: str, start_time: datetime,
                      duration_minutes: int = 60,
                      attendees: Optional[List[str]] = None,
                      participants: Optional[List[Dict[str, str]]] = None,
                      case_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new Google Meet meeting.
        
        Args:
            title: Title of the meeting
            start_time: Start time
            duration_minutes: Duration in minutes
            attendees: List of email addresses
            participants: List of participant dictionaries with 'email' key
            case_data: Optional case data for context
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        event = {
            'summary': title,
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
                    'requestId': f"{title}-{start_time.isoformat()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        meeting = self.calendar_service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1,
            sendNotifications=True
        ).execute()
        
        return meeting
    
    def get_meeting_link(self, event_id: str) -> Optional[str]:
        """Get the Meet link for a calendar event."""
        event = self.calendar_service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        if 'conferenceData' in event:
            return event['conferenceData']['entryPoints'][0]['uri']
        return None
    
    def get_meeting_status(self, event_id: str) -> Dict[str, Any]:
        """Get the status of a meeting."""
        event = self.calendar_service.events().get(
            calendarId='primary',
            eventId=event_id,
            fields='id,status,summary,start,end,attendees,conferenceData'
        ).execute()
        
        now = datetime.now(timezone.utc)
        start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
        
        status = {
            'event_id': event.get('id'),
            'title': event.get('summary', ''),
            'status': 'scheduled',
            'start_time': start_time,
            'end_time': end_time,
            'attendees': event.get('attendees', []),
            'meet_link': event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', None)
        }
        
        if not status['event_id']:
            raise ValueError('No event_id found in response')
        
        if now < start_time:
            status['status'] = 'scheduled'
        elif now > end_time:
            status['status'] = 'ended'
        else:
            status['status'] = 'in_progress'
        
        return status
    
    def update_meeting(self, event_id: str, start_time: Optional[datetime] = None,
                      duration_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Update a meeting.
        
        Args:
            event_id: ID of the event to update
            start_time: New start time for the meeting
            duration_minutes: New duration in minutes
        """
        event = self.calendar_service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        if start_time:
            event['start'] = {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Santiago'
            }
            if duration_minutes:
                end_time = start_time + timedelta(minutes=duration_minutes)
            else:
                end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
            event['end'] = {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Santiago'
            }
        elif duration_minutes:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            end_time = start_time + timedelta(minutes=duration_minutes)
            event['end'] = {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Santiago'
            }
        
        updated_event = self.calendar_service.events().patch(
            calendarId='primary',
            eventId=event_id,
            body=event,
            sendUpdates='all'
        ).execute()
        
        return updated_event
