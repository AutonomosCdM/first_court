"""
Pruebas unitarias para la integración con Google Meet
"""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from src.integrations.google_meet import GoogleMeetClient

class TestGoogleMeet(unittest.TestCase):
    def setUp(self):
        """Inicializar el cliente y datos de prueba"""
        # Mock Calendar service
        self.mock_calendar = MagicMock()
        
        # Configure mock responses
        self.mock_event = {
            'id': 'test_event_id',
            'status': 'confirmed',
            'hangoutLink': 'https://meet.google.com/test',
            'conferenceData': {
                'entryPoints': [{
                    'uri': 'https://meet.google.com/test',
                    'label': 'meet.google.com/test'
                }]
            },
            'start': {
                'dateTime': '2025-02-15T10:00:00-03:00',
                'timeZone': 'America/Santiago'
            },
            'end': {
                'dateTime': '2025-02-15T11:00:00-03:00',
                'timeZone': 'America/Santiago'
            },
            'attendees': [
                {'email': 'judge@test.com', 'responseStatus': 'accepted'},
                {'email': 'defender@test.com', 'responseStatus': 'needsAction'}
            ]
        }
        
        # Create mock events method
        self.mock_events = MagicMock()
        self.mock_events.insert.return_value.execute.return_value = self.mock_event
        self.mock_events.get.return_value.execute.return_value = self.mock_event
        self.mock_events.patch.return_value.execute.return_value = self.mock_event
        self.mock_calendar.events = self.mock_events
        
        # Create client with mocked service
        with patch('googleapiclient.discovery.build') as mock_build:
            def mock_build_service(service, version, credentials):
                if service == 'calendar':
                    return self.mock_calendar
            mock_build.side_effect = mock_build_service
            self.client = GoogleMeetClient()
        
        self.case_data = {
            'id': 'TEST-2025-002',
            'tipo': 'Audiencia de Prueba',
            'materia': 'Civil'
        }
        self.participants = [
            {'email': 'judge@test.com', 'role': 'Juez'},
            {'email': 'defender@test.com', 'role': 'Defensor'}
        ]
        
    def test_create_meeting(self):
        """Prueba la creación de una reunión"""
        start_time = datetime.now(timezone.utc) + timedelta(hours=2)
        meeting = self.client.create_meeting(
            title=f"Test Meeting - {self.case_data['id']}",
            start_time=start_time,
            duration_minutes=30,
            participants=self.participants,
            case_data=self.case_data
        )
        
        # Verify API call
        assert self.mock_calendar.events.call_count > 0
        assert self.mock_calendar.events.return_value.insert.call_count > 0
        
        # Verify response
        self.assertEqual(meeting['id'], self.mock_event['id'])
        self.assertEqual(meeting['hangoutLink'], self.mock_event['hangoutLink'])
        self.assertEqual(meeting['status'], self.mock_event['status'])
        
    def test_update_meeting(self):
        """Prueba la actualización de una reunión"""
        # Create initial meeting
        start_time = datetime.now(timezone.utc) + timedelta(hours=3)
        meeting = self.client.create_meeting(
            title="Original Meeting",
            start_time=start_time,
            duration_minutes=30,
            participants=self.participants,
            case_data=self.case_data
        )
        
        # Update meeting
        new_time = start_time + timedelta(hours=1)
        updated = self.client.update_meeting(
            event_id=meeting['id'],
            start_time=new_time,
            duration_minutes=45
        )
        
        # Verify API call
        assert self.mock_calendar.events.call_count > 0
        assert self.mock_calendar.events.return_value.patch.call_count > 0
        
        # Verify response
        self.assertEqual(updated['id'], meeting['id'])
        self.assertEqual(updated['status'], self.mock_event['status'])
        
    def test_get_meeting_status(self):
        """Prueba la obtención del estado de una reunión"""
        # Create meeting
        start_time = datetime.now(timezone.utc) + timedelta(hours=4)
        meeting = self.client.create_meeting(
            title="Status Test Meeting",
            start_time=start_time,
            duration_minutes=30,
            participants=self.participants,
            case_data=self.case_data
        )
        
        # Get status
        status = self.client.get_meeting_status(meeting['id'])
        
        # Verify API call
        assert self.mock_calendar.events.call_count > 0
        assert self.mock_calendar.events.return_value.get.call_count > 0
        
        # Verify response
        self.assertEqual(status['id'], self.mock_event['id'])
        self.assertEqual(status['status'], self.mock_event['status'])
        self.assertEqual(status['meet_link'], self.mock_event['hangoutLink'])
        self.assertEqual(len(status['attendees']), len(self.mock_event['attendees']))

if __name__ == '__main__':
    unittest.main()
