"""
Integración con Google Sheets para reportes y análisis
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from src.auth.oauth_client import OAuth2Client

class GoogleSheetsClient:
    """Cliente para interactuar con Google Sheets"""
    
    def __init__(self):
        """Inicializa el cliente de Google Sheets"""
        self.oauth_client = OAuth2Client()
        self.sheets_service = self.oauth_client.sheets
        self.drive_service = self.oauth_client.drive
    
    def create_spreadsheet(self, title: str) -> Dict:
        """
        Crea una nueva hoja de cálculo
        
        Args:
            title: Título de la hoja de cálculo
            
        Returns:
            Dict con la información de la hoja creada
        """
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        
        spreadsheet = self.sheets_service.spreadsheets().create(
            body=spreadsheet
        ).execute()
        
        return spreadsheet
    
    def add_sheet(self, spreadsheet_id: str, title: str) -> Dict:
        """
        Agrega una nueva hoja a una hoja de cálculo existente
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            title: Título de la nueva hoja
            
        Returns:
            Dict con la información de la hoja creada
        """
        body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': title
                    }
                }
            }]
        }
        
        result = self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        
        return result['replies'][0]['addSheet']
    
    def write_values(self, *, spreadsheet_id: str, range: str, values: List[List[Any]]) -> Dict:
        """
        Escribe valores en una hoja de cálculo
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            range: Rango donde escribir (ej: 'Hoja1!A1:D5')
            values: Lista de listas con los valores a escribir
            
        Returns:
            Dict con el resultado de la operación
        """
        body = {
            'values': values
        }
        
        result = self.sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return result
    
    def read_values(self, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """
        Lee valores de una hoja de cálculo
        
        Args:
            spreadsheet_id: ID de la hoja de cálculo
            range_name: Rango a leer
            
        Returns:
            Lista de listas con los valores leídos
        """
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        return result.get('values', [])
    
    def create_cases_dashboard(self) -> Dict:
        """
        Crea un dashboard para seguimiento de casos
        
        Returns:
            Dict con la información de la hoja creada
        """
        # Crear hoja de cálculo
        spreadsheet = self.create_spreadsheet('Dashboard de Casos')
        spreadsheet_id = spreadsheet['spreadsheetId']
        
        # Definir encabezados
        headers = [
            ['ID Caso', 'Tipo', 'Estado', 'Fecha Ingreso', 'Última Actualización', 
             'Próxima Audiencia', 'Responsable', 'Prioridad']
        ]
        
        # Escribir encabezados
        self.write_values(spreadsheet_id, 'Hoja1!A1:H1', headers)
        
        # Aplicar formato
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.2,
                            'green': 0.2,
                            'blue': 0.2
                        },
                        'textFormat': {
                            'foregroundColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            },
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]
        
        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        return spreadsheet
    
    def create_deadlines_tracker(self) -> Dict:
        """
        Crea una hoja de seguimiento de plazos
        
        Returns:
            Dict con la información de la hoja creada
        """
        # Crear hoja de cálculo
        spreadsheet = self.create_spreadsheet('Control de Plazos')
        spreadsheet_id = spreadsheet['spreadsheetId']
        
        # Definir encabezados
        headers = [
            ['ID Caso', 'Trámite', 'Fecha Inicio', 'Plazo (días)', 'Fecha Límite',
             'Estado', 'Responsable', 'Observaciones']
        ]
        
        # Escribir encabezados
        self.write_values(spreadsheet_id, 'Hoja1!A1:H1', headers)
        
        # Aplicar formato condicional para fechas próximas
        requests = [{
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{'sheetId': 0, 'startColumnIndex': 4, 'endColumnIndex': 5}],
                    'booleanRule': {
                        'condition': {
                            'type': 'DATE_BEFORE',
                            'values': [{'relativeDate': 'TODAY'}]
                        },
                        'format': {
                            'backgroundColor': {'red': 1.0, 'green': 0.4, 'blue': 0.4}
                        }
                    }
                }
            }
        }]
        
        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        return spreadsheet
