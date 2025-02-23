import os
from datetime import datetime
import uuid
from typing import Dict, Any, Optional

from src.integrations.database.sqlite_db import SQLiteDatabase

class SlackDatabase(SQLiteDatabase):
    """Slack-specific database implementation"""
    
    def __init__(self, db_path: str = 'db/slack_integration.sqlite'):
        """Initialize Slack database
        
        Args:
            db_path (str): Path to SQLite database file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        super().__init__(db_path)
        
        with self.connection():
            self._create_tables()
    
    def _create_tables(self) -> None:
        """Create necessary tables for Slack integration"""
        # Cases table
        self.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            case_number TEXT,
            description TEXT,
            status TEXT,
            created_at DATETIME,
            channel_id TEXT
        )
        ''')
        
        # Documents table
        self.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            case_id TEXT,
            filename TEXT,
            filetype TEXT,
            size INTEGER,
            uploaded_at DATETIME,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        )
        ''')
        
        # Hearings table
        self.execute('''
        CREATE TABLE IF NOT EXISTS hearings (
            id TEXT PRIMARY KEY,
            case_id TEXT,
            hearing_date DATE,
            scheduled_at DATETIME,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        )
        ''')
    
    def create_case(self, description: str) -> Dict[str, Any]:
        """Create a new case
        
        Args:
            description (str): Case description
        
        Returns:
            Dict containing case metadata
        """
        with self.connection(), self.transaction():
            # Generate unique identifiers
            case_id = str(uuid.uuid4())
            year = datetime.now().year
            
            # Find the next case number
            result = self.fetch_one('''
                SELECT MAX(CAST(SUBSTR(case_number, -3) AS INTEGER)) 
                FROM cases 
                WHERE case_number LIKE :year_pattern
            ''', {"year_pattern": f'{year}-%'})
            
            last_number = result[0] if result else 0
            case_number = f"{year}-{str(last_number + 1).zfill(3) if last_number else '001'}"
            
            # Prepare case metadata
            case_metadata = {
                "id": case_id,
                "case_number": case_number,
                "description": description,
                "status": "En Proceso",
                "created_at": datetime.now().isoformat(),
                "channel_id": None
            }
            
            # Insert case into database
            self.execute('''
                INSERT INTO cases 
                (id, case_number, description, status, created_at, channel_id)
                VALUES (:id, :case_number, :description, :status, :created_at, :channel_id)
            ''', case_metadata)
            
            return case_metadata
    
    def add_document(self, case_id: str, filename: str, filetype: str, size: int) -> Dict[str, Any]:
        """Add a document to a case
        
        Args:
            case_id (str): ID of the case
            filename (str): Name of the file
            filetype (str): Type of the file
            size (int): Size of the file in bytes
        
        Returns:
            Dict containing document metadata
        """
        with self.connection(), self.transaction():
            doc_metadata = {
                "id": str(uuid.uuid4()),
                "case_id": case_id,
                "filename": filename,
                "filetype": filetype,
                "size": size,
                "uploaded_at": datetime.now().isoformat()
            }
            
            self.execute('''
                INSERT INTO documents 
                (id, case_id, filename, filetype, size, uploaded_at)
                VALUES (:id, :case_id, :filename, :filetype, :size, :uploaded_at)
            ''', doc_metadata)
            
            return doc_metadata
    
    def schedule_hearing(self, case_id: str, hearing_date: str) -> Dict[str, Any]:
        """Schedule a hearing for a case
        
        Args:
            case_id (str): ID of the case
            hearing_date (str): Date of the hearing (YYYY-MM-DD)
        
        Returns:
            Dict containing hearing metadata
        """
        with self.connection(), self.transaction():
            hearing_metadata = {
                "id": str(uuid.uuid4()),
                "case_id": case_id,
                "hearing_date": hearing_date,
                "scheduled_at": datetime.now().isoformat()
            }
            
            self.execute('''
                INSERT INTO hearings 
                (id, case_id, hearing_date, scheduled_at)
                VALUES (:id, :case_id, :hearing_date, :scheduled_at)
            ''', hearing_metadata)
            
            return hearing_metadata
    
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve case details
        
        Args:
            case_id (str): ID of the case
        
        Returns:
            Optional[Dict] containing case details or None if not found
        """
        with self.connection():
            # Fetch case
            case = self.fetch_one('SELECT * FROM cases WHERE id = :id', {"id": case_id})
            
            if not case:
                return None
            
            # Fetch associated documents
            documents = self.fetch_all(
                'SELECT * FROM documents WHERE case_id = :id', 
                {"id": case_id}
            )
            
            # Fetch associated hearings
            hearings = self.fetch_all(
                'SELECT * FROM hearings WHERE case_id = :id',
                {"id": case_id}
            )
            
            return {
                "case": case,
                "documents": documents,
                "hearings": hearings
            }
