"""
Integración con Slack para notificaciones y comunicación
"""
import os
import logging
from typing import Dict, List, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackIntegration:
    def __init__(self, token: Optional[str] = None):
        """Inicializar cliente de Slack"""
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        if not self.token:
            raise ValueError("SLACK_BOT_TOKEN no está configurado")
        
        self.client = WebClient(token=self.token)
        
    def send_notification(
        self,
        channel: str,
        message: str,
        thread_ts: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Enviar notificación a un canal
        
        Args:
            channel: ID o nombre del canal
            message: Mensaje a enviar
            thread_ts: ID del hilo para responder
            attachments: Adjuntos del mensaje
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                thread_ts=thread_ts,
                attachments=attachments
            )
            logger.info(f"Mensaje enviado a {channel}")
            return response
            
        except SlackApiError as e:
            logger.error(f"Error al enviar mensaje: {e.response['error']}")
            raise
            
    def create_case_channel(self, case_id: str, participants: List[str] = None) -> Dict:
        """
        Crear un canal privado para un caso
        
        Args:
            case_id: ID del caso
            participants: Lista de IDs de usuarios a invitar
        """
        channel_name = f"caso-{case_id.lower()}"
        try:
            # Crear canal privado
            response = self.client.conversations_create(
                name=channel_name,
                is_private=True
            )
            channel_id = response["channel"]["id"]
            
            # Invitar participantes
            if participants:
                self.client.conversations_invite(
                    channel=channel_id,
                    users=",".join(participants)
                )
                
            logger.info(f"Canal creado: {channel_name}")
            return response
            
        except SlackApiError as e:
            logger.error(f"Error al crear canal: {e.response['error']}")
            raise
            
    def update_case_status(
        self,
        case_id: str,
        status: str,
        details: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict:
        """
        Actualizar estado de un caso
        
        Args:
            case_id: ID del caso
            status: Nuevo estado
            details: Detalles adicionales
            channel: Canal donde enviar la actualización
        """
        if not channel:
            channel = f"caso-{case_id.lower()}"
            
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Actualización de Caso {case_id}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Estado:*\n{status}"
                    }
                ]
            }
        ]
        
        if details:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Detalles:*\n{details}"
                }
            })
            
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                blocks=blocks
            )
            logger.info(f"Estado actualizado para caso {case_id}")
            return response
            
        except SlackApiError as e:
            logger.error(f"Error al actualizar estado: {e.response['error']}")
            raise
