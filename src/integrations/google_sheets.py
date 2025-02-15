"""Google Sheets integration module."""
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from src.auth.auth_manager import AuthManager

class GoogleSheetsClient:
    """Client for interacting with Google Sheets API."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.service = None
        self._init_service()
    
    def _init_service(self):
        """Initialize the Sheets service."""
        credentials = self.auth_manager.get_credentials()
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def create_spreadsheet(self, title: str, sheets: List[str] = None) -> Dict[str, Any]:
        """Create a new Google Spreadsheet."""
        spreadsheet = {
            'properties': {'title': title},
            'sheets': []
        }
        
        if sheets:
            for sheet_title in sheets:
                spreadsheet['sheets'].append({
                    'properties': {'title': sheet_title}
                })
        
        return self.service.spreadsheets().create(
            body=spreadsheet
        ).execute()
    
    def get_values(self, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """Get values from a specific range in a spreadsheet."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        return result.get('values', [])
    
    def update_values(self, spreadsheet_id: str, range_name: str,
                     values: List[List[Any]]) -> Dict[str, Any]:
        """Update values in a specific range."""
        body = {
            'values': values
        }
        
        return self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def append_values(self, spreadsheet_id: str, range_name: str,
                     values: List[List[Any]]) -> Dict[str, Any]:
        """Append values to a specific range."""
        body = {
            'values': values
        }
        
        return self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
    
    def create_case_register(self, title: str) -> Dict[str, Any]:
        """Create a new case register spreadsheet with predefined structure."""
        sheets = ['Casos', 'Audiencias', 'Documentos', 'Estadísticas']
        spreadsheet = self.create_spreadsheet(title, sheets)
        
        # Configurar encabezados para cada hoja
        headers = {
            'Casos': [
                ['ID', 'Tipo', 'Materia', 'Estado', 'Fecha Inicio', 
                 'Juez', 'Demandante', 'Demandado', 'Última Actualización']
            ],
            'Audiencias': [
                ['ID Caso', 'Tipo Audiencia', 'Fecha', 'Hora', 'Virtual',
                 'Estado', 'Link Meet', 'Observaciones']
            ],
            'Documentos': [
                ['ID Caso', 'Tipo Documento', 'Fecha', 'Autor',
                 'Link Drive', 'Confidencial']
            ],
            'Estadísticas': [
                ['Métrica', 'Valor', 'Período']
            ]
        }
        
        for sheet_name, header in headers.items():
            self.update_values(
                spreadsheet_id=spreadsheet['spreadsheetId'],
                range_name=f'{sheet_name}!A1',
                values=header
            )
        
        return spreadsheet
