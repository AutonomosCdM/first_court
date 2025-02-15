"""
Integración con Google Forms para recopilación de datos
"""
from typing import List, Dict, Optional
from src.auth.oauth_client import OAuth2Client

class GoogleFormsClient:
    """Cliente para interactuar con Google Forms"""
    
    def __init__(self):
        """Inicializa el cliente de Google Forms"""
        self.oauth_client = OAuth2Client()
        self.forms_service = self.oauth_client.forms
        self.drive_service = self.oauth_client.drive
    
    def create_form(self, title: str, description: str = '') -> Dict:
        """
        Crea un nuevo formulario
        
        Args:
            title: Título del formulario
            description: Descripción del formulario
            
        Returns:
            Dict con la información del formulario creado
        """
        # Primero creamos el formulario solo con el título
        form_body = {
            'info': {
                'title': title
            }
        }
        
        form = self.forms_service.forms().create(body=form_body).execute()
        
        # Si hay descripción, la agregamos con un batch update
        if description:
            update_body = {
                'requests': [{
                    'updateFormInfo': {
                        'info': {
                            'description': description
                        },
                        'updateMask': 'description'
                    }
                }]
            }
            
            self.forms_service.forms().batchUpdate(
                formId=form['formId'],
                body=update_body
            ).execute()
            
            # Actualizar el form con la nueva información
            form = self.forms_service.forms().get(formId=form['formId']).execute()
        
        return form
    
    def add_question(self, form_id: str, title: str, question_type: str, required: bool = False, options: List[str] = None) -> Dict:
        """
        Agrega una pregunta al formulario
        
        Args:
            form_id: ID del formulario
            title: Título de la pregunta
            question_type: Tipo de pregunta (TEXT, RADIO, FILE_UPLOAD, etc)
            required: Si es obligatorio responder
            options: Lista de opciones para preguntas de selección
            
        Returns:
            Dict con la información de la pregunta creada
        """
        question = {
            'title': title,
            'required': required
        }
        
        if question_type == 'TEXT':
            question['textQuestion'] = {}
        elif question_type == 'RADIO':
            question['choiceQuestion'] = {
                'type': 'RADIO',
                'options': [{'value': opt} for opt in (options or [])]
            }
        elif question_type == 'FILE_UPLOAD':
            question['fileUploadQuestion'] = {}
        
        request = {
            'requests': [{
                'createItem': {
                    'item': {
                        'questionItem': {
                            'question': question
                        }
                    },
                    'location': {
                        'index': 0
                    }
                }
            }]
        }
        
        result = self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=request
        ).execute()
        
        return result['replies'][0]['createItem']['questionItem']['question']

    
    def get_responses(self, form_id: str) -> List[Dict]:
        """
        Obtiene las respuestas de un formulario
        
        Args:
            form_id: ID del formulario
            
        Returns:
            Lista de respuestas
        """
        result = self.forms_service.forms().responses().list(formId=form_id).execute()
        return result.get('responses', [])
    
    def create_case_intake_form(self) -> Dict:
        """
        Crea un formulario de ingreso de casos
        
        Returns:
            Dict con la información del formulario creado
        """
        # Crear formulario base
        form = self.create_form(
            title='Ingreso de Nuevo Caso',
            description='Formulario para ingresar un nuevo caso al sistema'
        )
        
        form_id = form['formId']
        
        # Agregar campos
        self.add_question(form_id, 'Nombre del Solicitante', 'TEXT', required=True)
        self.add_question(form_id, 'RUT/DNI', 'TEXT', required=True)
        self.add_question(form_id, 'Correo Electrónico', 'TEXT', required=True)
        self.add_question(form_id, 'Teléfono de Contacto', 'TEXT', required=True)
        
        self.add_question(
            form_id,
            'Tipo de Caso',
            'RADIO',
            required=True,
            options=[
                'Civil',
                'Familia',
                'Laboral',
                'Penal',
                'Otro'
            ]
        )
        
        self.add_question(form_id, 'Descripción del Caso', 'TEXT', required=True)
        self.add_question(form_id, 'Documentos Adjuntos', 'FILE_UPLOAD')


        return form
    
    def create_satisfaction_survey(self) -> Dict:
        """
        Crea una encuesta de satisfacción
        
        Returns:
            Dict con la información del formulario creado
        """
        # Crear formulario base
        form = self.create_form(
            title='Encuesta de Satisfacción',
            description='Su opinión nos ayuda a mejorar nuestro servicio'
        )
        
        form_id = form['formId']
        
        # Agregar preguntas
        self.add_question(
            form_id,
            '¿Cómo calificaría la atención recibida?',
            'RADIO',
            required=True,
            options=[
                'Excelente',
                'Buena',
                'Regular',
                'Mala',
                'Muy mala'
            ]
        )
        
        self.add_question(
            form_id,
            '¿Cómo calificaría la claridad de la información proporcionada?',
            'RADIO',
            required=True,
            options=[
                'Muy clara',
                'Clara',
                'Regular',
                'Poco clara',
                'Nada clara'
            ]
        )
        
        self.add_question(
            form_id,
            '¿Recomendaría nuestros servicios?',
            'RADIO',
            required=True,
            options=[
                'Definitivamente sí',
                'Probablemente sí',
                'No estoy seguro',
                'Probablemente no',
                'Definitivamente no'
            ]
        )
        
        self.add_question(
            form_id,
            'Comentarios o sugerencias adicionales',
            'TEXT'
        )

        
        self.add_text_item(
            form_id,
            '¿Qué podríamos mejorar?',
            required=False
        )
        
        return form
