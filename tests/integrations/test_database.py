"""
Tests para la integración con la base de datos
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.integrations.database.models import (
    Base, Case, Document, Hearing, Participant,
    CaseParticipant, HearingParticipant, CaseStatus
)

# Configuración para testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    """Fixture para crear una sesión de base de datos de prueba"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def sample_case(db_session):
    """Fixture para crear un caso de prueba"""
    case = Case(
        case_number="2025-001-TEST",
        title="Caso de Prueba",
        description="Este es un caso de prueba",
        status=CaseStatus.PENDING
    )
    db_session.add(case)
    db_session.commit()
    return case

@pytest.fixture
def sample_participants(db_session):
    """Fixture para crear participantes de prueba"""
    participants = [
        Participant(
            name="Juez Test",
            email="juez@test.com",
            role="juez",
            slack_id="U123TEST"
        ),
        Participant(
            name="Fiscal Test",
            email="fiscal@test.com",
            role="fiscal",
            slack_id="U124TEST"
        ),
        Participant(
            name="Defensor Test",
            email="defensor@test.com",
            role="defensor",
            slack_id="U125TEST"
        )
    ]
    for p in participants:
        db_session.add(p)
    db_session.commit()
    return participants

def test_create_case(db_session):
    """Test para crear un caso"""
    case = Case(
        case_number="2025-002-TEST",
        title="Nuevo Caso",
        description="Descripción del caso",
        status=CaseStatus.PENDING
    )
    db_session.add(case)
    db_session.commit()
    
    assert case.id is not None
    assert case.case_number == "2025-002-TEST"
    assert case.status == CaseStatus.PENDING

def test_add_document_to_case(db_session, sample_case):
    """Test para agregar un documento a un caso"""
    doc = Document(
        case_id=sample_case.id,
        title="Documento de Prueba",
        document_type="sentencia",
        content="Contenido del documento",
        drive_id="1234TEST",
        drive_url="https://drive.google.com/test"
    )
    db_session.add(doc)
    db_session.commit()
    
    assert doc.id is not None
    assert doc.case_id == sample_case.id
    assert len(sample_case.documents) == 1

def test_schedule_hearing(db_session, sample_case, sample_participants):
    """Test para programar una audiencia"""
    hearing = Hearing(
        case_id=sample_case.id,
        title="Audiencia de Prueba",
        description="Primera audiencia del caso",
        scheduled_for=datetime.utcnow(),
        duration_minutes=60,
        calendar_event_id="evt123TEST",
        meet_url="https://meet.google.com/test"
    )
    db_session.add(hearing)
    db_session.commit()
    
    # Agregar participantes a la audiencia
    for p in sample_participants:
        participant = HearingParticipant(
            hearing_id=hearing.id,
            participant_id=p.id
        )
        db_session.add(participant)
    
    db_session.commit()
    
    assert hearing.id is not None
    assert len(hearing.participants) == len(sample_participants)

def test_case_status_update(db_session, sample_case):
    """Test para actualizar el estado de un caso"""
    assert sample_case.status == CaseStatus.PENDING
    
    sample_case.status = CaseStatus.IN_PROGRESS
    db_session.commit()
    
    updated_case = db_session.query(Case).get(sample_case.id)
    assert updated_case.status == CaseStatus.IN_PROGRESS

def test_participant_relationships(db_session, sample_case, sample_participants):
    """Test para verificar las relaciones entre participantes y casos"""
    for p in sample_participants:
        case_participant = CaseParticipant(
            case_id=sample_case.id,
            participant_id=p.id,
            role=p.role
        )
        db_session.add(case_participant)
    
    db_session.commit()
    
    assert len(sample_case.participants) == len(sample_participants)
    
    # Verificar que podemos acceder a los casos desde los participantes
    participant = sample_participants[0]
    assert len(participant.case_participations) == 1
    assert participant.case_participations[0].case_id == sample_case.id
