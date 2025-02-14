"""
Pruebas unitarias para la integración con Google Meet
"""
import unittest
from datetime import datetime, timedelta
from src.integrations.google_meet import GoogleMeetClient

class TestGoogleMeet(unittest.TestCase):
    def setUp(self):
        """Inicializar el cliente y datos de prueba"""
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
        start_time = datetime.now() + timedelta(hours=2)
        meeting = self.client.create_meeting(
            title=f"Test Meeting - {self.case_data['id']}",
            start_time=start_time,
            duration_minutes=30,
            participants=self.participants,
            case_data=self.case_data
        )
        
        self.assertIn('event_id', meeting)
        self.assertIn('meet_link', meeting)
        self.assertTrue(meeting['meet_link'].startswith('https://meet.google.com/'))
        
    def test_update_meeting(self):
        """Prueba la actualización de una reunión"""
        # Crear reunión inicial
        start_time = datetime.now() + timedelta(hours=3)
        meeting = self.client.create_meeting(
            title="Original Meeting",
            start_time=start_time,
            duration_minutes=30,
            participants=self.participants,
            case_data=self.case_data
        )
        
        # Actualizar reunión
        new_title = "Updated Meeting"
        updated = self.client.update_meeting(
            event_id=meeting['event_id'],
            title=new_title,
            duration_minutes=45
        )
        
        self.assertEqual(updated['event_id'], meeting['event_id'])
        
    def test_get_meeting_status(self):
        """Prueba la obtención del estado de una reunión"""
        # Crear reunión
        start_time = datetime.now() + timedelta(hours=4)
        meeting = self.client.create_meeting(
            title="Status Test Meeting",
            start_time=start_time,
            duration_minutes=30,
            participants=self.participants,
            case_data=self.case_data
        )
        
        # Verificar estado
        status = self.client.get_meeting_status(meeting['event_id'])
        
        self.assertIn('status', status)
        self.assertIn('meet_link', status)
        self.assertIn('attendees', status)

if __name__ == '__main__':
    unittest.main()
