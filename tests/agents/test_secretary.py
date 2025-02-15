"""Tests for the Secretary Agent."""
import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.secretary import SecretaryAgent

@pytest.fixture
def secretary_agent():
    """Create a secretary agent with mocked clients."""
    with patch('src.agents.secretary.GoogleCalendarClient') as calendar_mock, \
         patch('src.agents.secretary.GoogleMeetClient') as meet_mock, \
         patch('src.agents.secretary.GmailClient') as gmail_mock:
        
        agent = SecretaryAgent()
        
        # Configure mocks
        agent.calendar_client = calendar_mock.return_value
        agent.meet_client = meet_mock.return_value
        agent.gmail_client = gmail_mock.return_value
        
        yield agent

@pytest.fixture
def sample_case_data():
    """Sample case data for testing."""
    return {
        'id': 'CASE-2025-001',
        'participantes': [
            {
                'nombre': 'Juan Pérez',
                'email': 'juan@example.com',
                'rol': 'demandante'
            },
            {
                'nombre': 'María García',
                'email': 'maria@example.com',
                'rol': 'demandada'
            },
            {
                'nombre': 'Pedro López',
                'email': 'pedro@example.com',
                'rol': 'juez'
            }
        ]
    }

def test_init(secretary_agent):
    """Test secretary agent initialization."""
    assert secretary_agent.calendar_client is not None
    assert secretary_agent.meet_client is not None
    assert secretary_agent.gmail_client is not None

def test_schedule_hearing_virtual(secretary_agent, sample_case_data):
    """Test scheduling a virtual hearing."""
    # Preparar
    title = "Primera Audiencia"
    date = datetime.now(UTC) + timedelta(days=1)
    duration = 60
    description = "Audiencia inicial del caso"
    
    # Configurar mocks
    secretary_agent.meet_client.create_meeting.return_value = {
        'conferenceData': {
            'entryPoints': [{'uri': 'https://meet.google.com/abc-defg-hij'}]
        }
    }
    
    secretary_agent.calendar_client.create_event.return_value = {
        'id': 'event123',
        'summary': f"Audiencia: {title} - Caso {sample_case_data['id']}",
        'start': {'dateTime': date.isoformat()},
        'end': {'dateTime': (date + timedelta(minutes=duration)).isoformat()}
    }
    
    # Ejecutar
    event = secretary_agent.schedule_hearing(
        case_data=sample_case_data,
        title=title,
        preferred_date=date,
        duration_minutes=duration,
        description=description,
        virtual=True
    )
    
    # Verificar
    # 1. Verificar creación de reunión virtual
    secretary_agent.meet_client.create_meeting.assert_called_once_with(
        title=f"Audiencia: {title} - Caso {sample_case_data['id']}",
        start_time=date,
        duration_minutes=duration,
        attendees=[p['email'] for p in sample_case_data['participantes']]
    )
    
    # 2. Verificar creación de evento en calendario
    secretary_agent.calendar_client.create_event.assert_called_once()
    call_args = secretary_agent.calendar_client.create_event.call_args[1]
    assert call_args['summary'] == f"Audiencia: {title} - Caso {sample_case_data['id']}"
    assert call_args['start_time'] == date
    assert call_args['end_time'] == date + timedelta(minutes=duration)
    assert 'https://meet.google.com/abc-defg-hij' in call_args['description']
    
    # 3. Verificar envío de emails
    assert secretary_agent.gmail_client.send_email.call_count == len(sample_case_data['participantes'])
    for participant in sample_case_data['participantes']:
        secretary_agent.gmail_client.send_email.assert_any_call(
            to=participant['email'],
            subject=f"Citación a Audiencia - Caso {sample_case_data['id']}",
            body=pytest.approx(
                f"Estimado/a {participant['nombre']},\n\n"
                f"Se le cita a la audiencia '{title}' del caso {sample_case_data['id']},"
                f" programada para el {date.strftime('%d/%m/%Y %H:%M')}."
                f"\n\nDuración estimada: {duration} minutos."
                f"\n\nEnlace de videoconferencia: https://meet.google.com/abc-defg-hij"
                f"\n\nSaludos cordiales,\nSistema Judicial",
                abs=1e-7
            )
        )

def test_schedule_hearing_presential(secretary_agent, sample_case_data):
    """Test scheduling a presential hearing."""
    # Preparar
    title = "Audiencia Presencial"
    date = datetime.now(UTC) + timedelta(days=2)
    duration = 90
    description = "Audiencia presencial en sala 101"
    
    secretary_agent.calendar_client.create_event.return_value = {
        'id': 'event456',
        'summary': f"Audiencia: {title} - Caso {sample_case_data['id']}",
        'start': {'dateTime': date.isoformat()},
        'end': {'dateTime': (date + timedelta(minutes=duration)).isoformat()}
    }
    
    # Ejecutar
    event = secretary_agent.schedule_hearing(
        case_data=sample_case_data,
        title=title,
        preferred_date=date,
        duration_minutes=duration,
        description=description,
        virtual=False
    )
    
    # Verificar
    # 1. Verificar que no se creó reunión virtual
    secretary_agent.meet_client.create_meeting.assert_not_called()
    
    # 2. Verificar creación de evento en calendario
    secretary_agent.calendar_client.create_event.assert_called_once()
    call_args = secretary_agent.calendar_client.create_event.call_args[1]
    assert call_args['summary'] == f"Audiencia: {title} - Caso {sample_case_data['id']}"
    assert call_args['description'] == description
    
    # 3. Verificar envío de emails sin link virtual
    for participant in sample_case_data['participantes']:
        secretary_agent.gmail_client.send_email.assert_any_call(
            to=participant['email'],
            subject=f"Citación a Audiencia - Caso {sample_case_data['id']}",
            body=pytest.approx(
                f"Estimado/a {participant['nombre']},\n\n"
                f"Se le cita a la audiencia '{title}' del caso {sample_case_data['id']},"
                f" programada para el {date.strftime('%d/%m/%Y %H:%M')}."
                f"\n\nDuración estimada: {duration} minutos."
                f"\n\nSaludos cordiales,\nSistema Judicial",
                abs=1e-7
            )
        )

def test_get_upcoming_hearings(secretary_agent):
    """Test getting upcoming hearings."""
    # Preparar
    days = 7
    expected_events = [
        {
            'id': 'event1',
            'summary': 'Audiencia 1',
            'start': {'dateTime': '2025-02-16T10:00:00Z'},
            'end': {'dateTime': '2025-02-16T11:00:00Z'}
        },
        {
            'id': 'event2',
            'summary': 'Audiencia 2',
            'start': {'dateTime': '2025-02-18T15:00:00Z'},
            'end': {'dateTime': '2025-02-18T16:30:00Z'}
        }
    ]
    
    secretary_agent.calendar_client.get_events.return_value = expected_events
    
    # Ejecutar
    events = secretary_agent.get_upcoming_hearings(days=days)
    
    # Verificar
    secretary_agent.calendar_client.get_events.assert_called_once()
    call_args = secretary_agent.calendar_client.get_events.call_args[1]
    assert isinstance(call_args['time_min'], datetime)
    assert isinstance(call_args['time_max'], datetime)
    assert call_args['time_max'] - call_args['time_min'] == timedelta(days=days)
    assert events == expected_events

def test_schedule_hearing_error_handling(secretary_agent, sample_case_data):
    """Test error handling when scheduling a hearing."""
    # Preparar
    title = "Audiencia con Error"
    date = datetime.now(UTC) + timedelta(days=1)
    
    # Simular error en Meet
    secretary_agent.meet_client.create_meeting.side_effect = Exception("Error creando reunión")
    
    # Ejecutar y verificar
    with pytest.raises(Exception) as exc_info:
        secretary_agent.schedule_hearing(
            case_data=sample_case_data,
            title=title,
            preferred_date=date,
            virtual=True
        )
    
    assert "Error creando reunión" in str(exc_info.value)
    # Verificar que no se creó el evento ni se enviaron emails
    secretary_agent.calendar_client.create_event.assert_not_called()
    secretary_agent.gmail_client.send_email.assert_not_called()
