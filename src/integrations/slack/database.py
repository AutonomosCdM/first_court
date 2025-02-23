import sqlite3
import json
import os
from typing import Dict, Any, List
from datetime import datetime
import uuid

class SlackDatabase:
    def __init__(self, db_path='db/slack_integration.sqlite'):
        """
        Initialize the Slack database with SQLite
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        # Enable returning column names
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self._create_tables()
    
    def _create_tables(self):
        """
        Create necessary tables for Slack integration
        """
        # Cases table
        self.cursor.execute('''
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
        self.cursor.execute('''
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
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS hearings (
            id TEXT PRIMARY KEY,
            case_id TEXT,
            hearing_date DATE,
            scheduled_at DATETIME,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        )
        ''')
        
        # Commit changes
        self.conn.commit()
    
    def create_case(self, description: str) -> Dict[str, Any]:
        """
        Create a new case
        
        Args:
            description (str): Case description
        
        Returns:
            Dict containing case metadata
        """
        # Generate unique identifiers
        case_id = str(uuid.uuid4())
        year = datetime.now().year
        
        # Find the next case number
        self.cursor.execute('''
        SELECT MAX(CAST(SUBSTR(case_number, -3) AS INTEGER)) 
        FROM cases 
        WHERE case_number LIKE ?
        ''', (f'{year}-%',))
        
        last_number = self.cursor.fetchone()[0]
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
        self.cursor.execute('''
        INSERT INTO cases 
        (id, case_number, description, status, created_at, channel_id)
        VALUES (:id, :case_number, :description, :status, :created_at, :channel_id)
        ''', case_metadata)
        
        # Commit changes
        self.conn.commit()
        
        return case_metadata
    
    def add_document(self, case_id: str, filename: str, filetype: str, size: int) -> Dict[str, Any]:
        """
        Add a document to a case
        
        Args:
            case_id (str): ID of the case
            filename (str): Name of the file
            filetype (str): Type of the file
            size (int): Size of the file in bytes
        
        Returns:
            Dict containing document metadata
        """
        doc_metadata = {
            "id": str(uuid.uuid4()),
            "case_id": case_id,
            "filename": filename,
            "filetype": filetype,
            "size": size,
            "uploaded_at": datetime.now().isoformat()
        }
        
        # Insert document into database
        self.cursor.execute('''
        INSERT INTO documents 
        (id, case_id, filename, filetype, size, uploaded_at)
        VALUES (:id, :case_id, :filename, :filetype, :size, :uploaded_at)
        ''', doc_metadata)
        
        # Commit changes
        self.conn.commit()
        
        return doc_metadata
    
    def schedule_hearing(self, case_id: str, hearing_date: str) -> Dict[str, Any]:
        """
        Schedule a hearing for a case
        
        Args:
            case_id (str): ID of the case
            hearing_date (str): Date of the hearing (YYYY-MM-DD)
        
        Returns:
            Dict containing hearing metadata
        """
        hearing_metadata = {
            "id": str(uuid.uuid4()),
            "case_id": case_id,
            "hearing_date": hearing_date,
            "scheduled_at": datetime.now().isoformat()
        }
        
        # Insert hearing into database
        self.cursor.execute('''
        INSERT INTO hearings 
        (id, case_id, hearing_date, scheduled_at)
        VALUES (:id, :case_id, :hearing_date, :scheduled_at)
        ''', hearing_metadata)
        
        # Commit changes
        self.conn.commit()
        
        return hearing_metadata
    
    def get_case(self, case_id: str) -> Dict[str, Any]:
        """
        Retrieve case details
        
        Args:
            case_id (str): ID of the case
        
        Returns:
            Dict containing case details
        """
        # Fetch case
        self.cursor.execute('SELECT * FROM cases WHERE id = ?', (case_id,))
        case = self.cursor.fetchone()
        
        if not case:
            return None
        
        # Fetch associated documents
        self.cursor.execute('SELECT * FROM documents WHERE case_id = ?', (case_id,))
        documents = self.cursor.fetchall()
        
        # Fetch associated hearings
        self.cursor.execute('SELECT * FROM hearings WHERE case_id = ?', (case_id,))
        hearings = self.cursor.fetchall()
        
        # Convert sqlite3.Row to dict
        def row_to_dict(row):
            return dict(zip(row.keys(), row))
        
        return {
            "case": row_to_dict(case),
            "documents": [row_to_dict(doc) for doc in documents],
            "hearings": [row_to_dict(hearing) for hearing in hearings]
        }
    
    def close(self):
        """
        Close database connection
        """
        self.conn.close()
