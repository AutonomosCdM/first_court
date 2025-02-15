"""
Modelos de base de datos usando SQLAlchemy
"""
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()

class CaseStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Case(Base):
    __tablename__ = 'cases'
    
    id = Column(Integer, primary_key=True)
    case_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(CaseStatus), default=CaseStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    documents = relationship("Document", back_populates="case")
    hearings = relationship("Hearing", back_populates="case")
    participants = relationship("CaseParticipant", back_populates="case")

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('cases.id'))
    title = Column(String(200), nullable=False)
    document_type = Column(String(50))
    content = Column(Text)
    drive_id = Column(String(100))  # ID en Google Drive
    drive_url = Column(String(500))  # URL en Google Drive
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="documents")

class Hearing(Base):
    __tablename__ = 'hearings'
    
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('cases.id'))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    scheduled_for = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    calendar_event_id = Column(String(100))  # ID en Google Calendar
    meet_url = Column(String(500))  # URL de Google Meet
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="hearings")
    participants = relationship("HearingParticipant", back_populates="hearing")

class Participant(Base):
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    role = Column(String(50))  # juez, fiscal, defensor, etc.
    slack_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case_participations = relationship("CaseParticipant", back_populates="participant")
    hearing_participations = relationship("HearingParticipant", back_populates="participant")

class CaseParticipant(Base):
    __tablename__ = 'case_participants'
    
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey('cases.id'))
    participant_id = Column(Integer, ForeignKey('participants.id'))
    role = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="participants")
    participant = relationship("Participant", back_populates="case_participations")

class HearingParticipant(Base):
    __tablename__ = 'hearing_participants'
    
    id = Column(Integer, primary_key=True)
    hearing_id = Column(Integer, ForeignKey('hearings.id'))
    participant_id = Column(Integer, ForeignKey('participants.id'))
    attended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    hearing = relationship("Hearing", back_populates="participants")
    participant = relationship("Participant", back_populates="hearing_participations")

def init_db(database_url: str):
    """Inicializar la base de datos"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
