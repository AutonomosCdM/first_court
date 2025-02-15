"""
Módulo de integración con Gmail para la gestión de comunicaciones judiciales.
"""
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64
import os
import pickle
from datetime import datetime
from src.integrations.template_engine import TemplateEngine

# Si modificas estos scopes, elimina el archivo token.pickle
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailClient:
    """Cliente para interactuar con Gmail API"""
    
    def __init__(self):
        """Inicializa el cliente de Gmail"""
        self.creds = None
        self.service = None
        self.template_engine = TemplateEngine()
    
    def _authenticate(self):
        """Maneja el proceso de autenticación con Gmail"""
        # El archivo token.pickle almacena los tokens de acceso y actualización del usuario
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # Si no hay credenciales válidas disponibles, permite al usuario iniciar sesión
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Usar el archivo credentials.json existente
                credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'credentials.json')
                if not os.path.exists(credentials_path):
                    raise ValueError(
                        'El archivo credentials.json no existe en la ubicación esperada. '
                        'Por favor, asegúrate de que el archivo esté presente en la raíz del proyecto.'
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0, redirect_uri_trailing_slash=True)
            
            # Guarda las credenciales para la próxima ejecución
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def send_notification(self,
                         to: List[str],
                         subject: str,
                         body: str,
                         attachments: List[str] = None,
                         template: str = None,
                         cc: List[str] = None,
                         bcc: List[str] = None) -> Dict:
        """
        Envía una notificación por correo electrónico.
        
        Args:
            to: Lista de destinatarios
            subject: Asunto del correo
            body: Contenido del correo (puede ser HTML)
            attachments: Lista de rutas a archivos adjuntos
            template: Nombre del template HTML a usar (opcional)
            cc: Lista de destinatarios en copia
            bcc: Lista de destinatarios en copia oculta
            
        Returns:
            Dict con la información del correo enviado
        """
        try:
            message = MIMEMultipart()
            message['to'] = ', '.join(to)
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
            
            # Si se especifica un template, usarlo
            if template:
                template_path = Path(__file__).parent / 'templates' / f'{template}.html'
                if template_path.exists():
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                        # Reemplazar placeholders en el template
                        body = template_content.replace('{{content}}', body)
            
            # Agregar el cuerpo del mensaje
            message.attach(MIMEText(body, 'html'))
            
            # Agregar archivos adjuntos
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                        message.attach(part)
            
            # Codificar el mensaje
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Enviar el mensaje
            sent_message = self.get_service().users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return sent_message
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_service(self):
        """Obtiene el servicio de Gmail, autenticando si es necesario"""
        if not self.service:
            self._authenticate()
        return self.service

    def send_hearing_notification(self,
                                to: List[str],
                                case_data: Dict,
                                hearing_data: Dict,
                                notification_type: str = 'scheduled') -> Dict:
        """
        Envía una notificación específica para audiencias.
        
        Args:
            to: Lista de destinatarios
            case_data: Datos del caso
            hearing_data: Datos de la audiencia
            notification_type: Tipo de notificación (scheduled, rescheduled, cancelled)
            
        Returns:
            Dict con la información del correo enviado
        """
        # Definir asunto y template según el tipo de notificación
        subjects = {
            'scheduled': f'Audiencia Programada - Causa {case_data.get("id")}',
            'rescheduled': f'Cambio de Fecha - Audiencia Causa {case_data.get("id")}',
            'cancelled': f'Cancelación de Audiencia - Causa {case_data.get("id")}'
        }
        
        templates = {
            'scheduled': 'hearing_scheduled',
            'rescheduled': 'hearing_rescheduled',
            'cancelled': 'hearing_cancelled'
        }
        
        # Preparar el cuerpo del mensaje con los datos relevantes
        body = f"""
        <h2>Información de la Audiencia</h2>
        <p><strong>Causa:</strong> {case_data.get('id')}</p>
        <p><strong>Tipo:</strong> {hearing_data.get('title')}</p>
        <p><strong>Fecha:</strong> {hearing_data.get('datetime')}</p>
        
        {'<p><strong>Enlace Meet:</strong> ' + hearing_data.get('meet_link', 'No disponible') + '</p>' 
         if hearing_data.get('virtual', True) else ''}
        
        <h3>Participantes:</h3>
        <ul>
        {''.join([f'<li>{p.get("nombre")} ({p.get("rol")})</li>' 
                  for p in case_data.get('participantes', [])])}
        </ul>
        
        {'<p><em>La audiencia ha sido cancelada.</em></p>' 
         if notification_type == 'cancelled' else ''}
        """
        
        return self.send_notification(
            to=to,
            subject=subjects.get(notification_type, subjects['scheduled']),
            body=body,
            template=templates.get(notification_type),
            attachments=self._get_relevant_documents(case_data)
        )
    
    def _get_relevant_documents(self, case_data: Dict) -> List[str]:
        """
        Obtiene la lista de documentos relevantes para adjuntar.
        Por ahora es un placeholder, se implementará cuando tengamos
        el sistema de gestión de documentos.
        """
        return []
