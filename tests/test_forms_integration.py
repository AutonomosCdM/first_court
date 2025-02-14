import unittest
from src.integrations.google_forms import GoogleFormsClient
from src.integrations.google_sheets import GoogleSheetsClient
from datetime import datetime

class TestFormsIntegration(unittest.TestCase):
    def setUp(self):
        self.forms_client = GoogleFormsClient()
        self.sheets_client = GoogleSheetsClient()
        self.test_form_title = f"Test Ingreso Causa {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def test_create_case_form(self):
        """Prueba la creación de un formulario de ingreso de causas"""
        # Crear formulario
        form = self.forms_client.create_form(
            title=self.test_form_title,
            description="Formulario de prueba para ingreso de causas"
        )
        self.assertIsNotNone(form.get('formId'))
        
        # Agregar preguntas
        questions = [
            {
                "title": "Tipo de Causa",
                "type": "RADIO",
                "options": ["Civil", "Familia", "Laboral", "Penal"]
            },
            {
                "title": "RUT/RUN Demandante",
                "type": "TEXT",
                "required": True
            },
            {
                "title": "Nombre Completo Demandante",
                "type": "TEXT",
                "required": True
            },
            {
                "title": "Documentos Fundantes",
                "type": "FILE_UPLOAD",
                "required": True
            }
        ]
        
        for q in questions:
            question = self.forms_client.add_question(
                form_id=form['formId'],
                title=q['title'],
                question_type=q['type'],
                required=q.get('required', False),
                options=q.get('options', None)
            )
            self.assertIsNotNone(question)
            
        # Crear hoja de cálculo vinculada
        spreadsheet = self.sheets_client.create_spreadsheet(
            title=f"Respuestas - {self.test_form_title}"
        )
        self.assertIsNotNone(spreadsheet.get('spreadsheetId'))
        
        # Vincular formulario con hoja de cálculo
        self.forms_client.link_to_spreadsheet(
            form_id=form['formId'],
            spreadsheet_id=spreadsheet['spreadsheetId']
        )
        
        # Verificar vinculación
        responses_dest = self.forms_client.get_response_destination(form['formId'])
        self.assertEqual(responses_dest['spreadsheetId'], spreadsheet['spreadsheetId'])
        
    def test_process_form_responses(self):
        """Prueba el procesamiento de respuestas del formulario"""
        # Crear formulario de prueba con respuestas
        form = self.forms_client.create_form(
            title=f"Test Respuestas {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description="Formulario de prueba para procesar respuestas"
        )
        
        # Agregar una pregunta simple
        self.forms_client.add_question(
            form_id=form['formId'],
            title="Nombre",
            question_type="TEXT"
        )
        
        # Simular una respuesta
        response_data = {"Nombre": "Juan Pérez"}
        self.forms_client.submit_form_response(
            form_id=form['formId'],
            response_data=response_data
        )
        
        # Verificar que la respuesta se registró
        responses = self.forms_client.get_form_responses(form['formId'])
        self.assertGreater(len(responses), 0)
        self.assertEqual(responses[0]['answers']['Nombre'], "Juan Pérez")
        
    def tearDown(self):
        # Limpiar recursos creados durante las pruebas
        pass

if __name__ == '__main__':
    unittest.main()
