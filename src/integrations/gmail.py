"""Gmail integration module."""
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from src.auth.auth_manager import AuthManager

class GmailClient:
    """Client for interacting with Gmail API."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.service = None
        self._init_service()
    
    def _init_service(self):
        """Initialize the Gmail service."""
        credentials = self.auth_manager.get_credentials()
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def send_email(self, to: str, subject: str, body: str,
                  html: Optional[str] = None) -> Dict[str, Any]:
        """Send an email using Gmail API."""
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['subject'] = subject
        
        # Add plain text version
        message.attach(MIMEText(body, 'plain'))
        
        # Add HTML version if provided
        if html:
            message.attach(MIMEText(html, 'html'))
            
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode('utf-8')
        
        sent_message = self.service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return sent_message
    
    def list_messages(self, query: str = '',
                     max_results: int = 10) -> List[Dict[str, Any]]:
        """List messages in Gmail that match the query."""
        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        full_messages = []
        
        for msg in messages:
            message = self.service.users().messages().get(
                userId='me',
                id=msg['id']
            ).execute()
            full_messages.append(message)
            
        return full_messages
    
    def get_message(self, message_id: str) -> Dict[str, Any]:
        """Get a specific message by ID."""
        return self.service.users().messages().get(
            userId='me',
            id=message_id
        ).execute()
