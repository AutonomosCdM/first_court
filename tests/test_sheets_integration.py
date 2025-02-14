import unittest
from src.integrations.google_sheets import GoogleSheetsClient
from datetime import datetime, timedelta

class TestSheetsIntegration(unittest.TestCase):
    def setUp(self):
        self.sheets_client = GoogleSheetsClient()
        self.test_sheet_title = f"Test Dashboard {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def test_create_case_dashboard(self):
        """Prueba la creación de un dashboard de casos"""
        # Crear hoja de cálculo
        spreadsheet = self.sheets_client.create_spreadsheet(
            title=self.test_sheet_title
        )
        self.assertIsNotNone(spreadsheet.get('spreadsheetId'))
        
        # Crear hojas necesarias
        sheets = [
            "Casos Activos",
            "Audiencias Programadas",
            "Plazos",
            "Dashboard"
        ]
        
        for sheet in sheets:
            response = self.sheets_client.add_sheet(
                spreadsheet_id=spreadsheet['spreadsheetId'],
                title=sheet
            )
            self.assertIsNotNone(response)
            
        # Agregar datos de prueba
        test_cases = [
            ["ID Causa", "Tipo", "Estado", "Última Actualización"],
            ["C-1234-2025", "Civil", "En Trámite", "2025-02-14"],
            ["C-1235-2025", "Civil", "Terminada", "2025-02-13"],
            ["F-100-2025", "Familia", "En Trámite", "2025-02-14"]
        ]
        
        self.sheets_client.write_values(
            spreadsheet_id=spreadsheet['spreadsheetId'],
            range="Casos Activos!A1:D4",
            values=test_cases
        )
        
        # Verificar datos escritos
        values = self.sheets_client.read_values(
            spreadsheet_id=spreadsheet['spreadsheetId'],
            range="Casos Activos!A1:D4"
        )
        self.assertEqual(len(values), 4)
        self.assertEqual(values[0][0], "ID Causa")
        
    def test_deadline_tracking(self):
        """Prueba el seguimiento de plazos"""
        # Crear hoja de cálculo para plazos
        spreadsheet = self.sheets_client.create_spreadsheet(
            title=f"Test Plazos {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Configurar hoja de plazos
        plazos = [
            ["ID Causa", "Trámite", "Fecha Inicio", "Plazo (días)", "Fecha Vencimiento", "Estado"],
            ["C-1234-2025", "Contestación", "2025-02-14", "15", "2025-03-01", "En curso"],
            ["C-1235-2025", "Apelación", "2025-02-10", "5", "2025-02-15", "Vencido"]
        ]
        
        self.sheets_client.write_values(
            spreadsheet_id=spreadsheet['spreadsheetId'],
            range="Sheet1!A1:F3",
            values=plazos
        )
        
        # Verificar plazos
        today = datetime.now().date()
        values = self.sheets_client.read_values(
            spreadsheet_id=spreadsheet['spreadsheetId'],
            range="Sheet1!A2:F3"  # Excluir encabezados
        )
        
        for row in values:
            deadline = datetime.strptime(row[4], "%Y-%m-%d").date()
            if deadline < today:
                self.assertEqual(row[5], "Vencido")
                
    def test_create_case_report(self):
        """Prueba la generación de reportes de casos"""
        # Crear hoja de cálculo para reportes
        spreadsheet = self.sheets_client.create_spreadsheet(
            title=f"Test Reportes {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Agregar datos de casos
        casos = [
            ["ID Causa", "Tipo", "Ingreso", "Estado", "Última Actualización"],
            ["C-1234-2025", "Civil", "2025-01-15", "En Trámite", "2025-02-14"],
            ["C-1235-2025", "Civil", "2025-01-20", "Terminada", "2025-02-13"],
            ["F-100-2025", "Familia", "2025-02-01", "En Trámite", "2025-02-14"]
        ]
        
        self.sheets_client.write_values(
            spreadsheet_id=spreadsheet['spreadsheetId'],
            range="Sheet1!A1:E4",
            values=casos
        )
        
        # Generar fórmulas para el reporte
        formulas = [
            ["Resumen de Casos"],
            ["Total Casos", "=COUNTA(A2:A4)"],
            ["Casos En Trámite", "=COUNTIF(D2:D4, \"En Trámite\")"],
            ["Casos Terminados", "=COUNTIF(D2:D4, \"Terminada\")"],
            [],
            ["Casos por Tipo"],
            ["Civil", "=COUNTIF(B2:B4, \"Civil\")"],
            ["Familia", "=COUNTIF(B2:B4, \"Familia\")"]
        ]
        
        self.sheets_client.write_values(
            spreadsheet_id=spreadsheet['spreadsheetId'],
            range="Sheet2!A1:B8",
            values=formulas
        )
        
        # Verificar resultados del reporte
        report = self.sheets_client.read_values(
            spreadsheet_id=spreadsheet['spreadsheetId'],
            range="Sheet2!A1:B8"
        )
        self.assertEqual(len(report), 8)
        
    def tearDown(self):
        # Limpiar recursos creados durante las pruebas
        pass

if __name__ == '__main__':
    unittest.main()
