import re
from typing import Dict, Any, Optional
from datetime import datetime
import os

from integrations.slack.base.event_handler import BaseSlackHandler
from integrations.slack.base.command_router import CommandRouter
from integrations.slack.utils.message_broker import MessageBroker
from integrations.slack.utils.notification import NotificationManager
from integrations.slack.utils.document_handler import DocumentHandler

class ProsecutorSlackApp(BaseSlackHandler):
    def __init__(self):
        super().__init__(env_prefix="PROSECUTOR")
        self.router = CommandRouter()
        self.register_commands()
        
    async def initialize(self):
        """Initialize the Prosecutor app"""
        await super().initialize()
        
        # Initialize utilities
        self.broker = MessageBroker(self.web_client)
        self.notifier = NotificationManager(self.web_client)
        self.doc_handler = DocumentHandler(self.web_client)
        
        # Optional: Uncomment and modify if you want to send a startup message
        # notification_channel = os.getenv('SLACK_NOTIFICATIONS_CHANNEL', 'C08DM64374H')
        # await self.notifier.send_notification(
        #     channel=notification_channel,
        #     title="Fiscal Online",
        #     message="🔍 El Fiscal está en línea y listo para investigar.",
        #     notification_type="success"
        # )
    
    def register_commands(self):
        """Register command handlers"""
        
        @self.router.command(r"ayuda")
        async def handle_help(text: str, event: Dict[str, Any]):
            help_text = """
*Comandos del Fiscal:*
• `acusar [caso] [descripción]` - Presentar acusación
• `prueba [caso] [tipo] [descripción]` - Presentar prueba
• `diligencia [caso] [tipo] [descripción]` - Solicitar diligencia
• `investigar [caso] [aspecto]` - Iniciar investigación
• `concluir [caso] [resultado]` - Concluir investigación
• `ayuda` - Mostrar este mensaje

*Ejemplos:*
• `acusar 2025-001 "Incumplimiento de contrato"`
• `prueba 2025-001 documental "Contrato firmado"`
• `diligencia 2025-001 testifical "Declaración de testigos"`
• `investigar 2025-001 "Análisis de documentación"`
• `concluir 2025-001 "Evidencia suficiente para acusar"`
            """
            
            await self.send_message(
                channel=event["channel"],
                text=help_text,
                thread_ts=event.get("thread_ts")
            )
    
        @self.router.command(r"acusar (\d{4}-\d{3}) \"(.+)\"")
        async def handle_accusation(text: str, event: Dict[str, Any]):
            match = re.match(r"acusar (\d{4}-\d{3}) \"(.+)\"", text)
            case_id = match.group(1)
            accusation = match.group(2)
            
            # Format accusation
            accusation_text = (
                f"*ACUSACIÓN*\n\n"
                f"{accusation}\n\n"
                f"_{datetime.now().strftime('%d/%m/%Y %H:%M')}_"
            )
            
            # Send accusation
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type="Nueva Acusación",
                description=accusation
            )
            
            # Add reaction to original message
            if event.get("ts"):
                await self.add_reaction(
                    channel=event["channel"],
                    timestamp=event["ts"],
                    reaction="scales"
                )
    
        @self.router.command(r"prueba (\d{4}-\d{3}) (\w+) \"(.+)\"")
        async def handle_evidence(text: str, event: Dict[str, Any]):
            match = re.match(r"prueba (\d{4}-\d{3}) (\w+) \"(.+)\"", text)
            case_id = match.group(1)
            evidence_type = match.group(2)
            description = match.group(3)
            
            # Handle attached files if any
            files = event.get("files", [])
            file_refs = []
            
            for file in files:
                file_refs.append(f"• {file['name']}")
            
            files_text = "\n".join(file_refs) if file_refs else "Sin archivos adjuntos"
            
            # Send evidence notification
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type=f"Nueva Prueba: {evidence_type}",
                description=(
                    f"*Tipo:* {evidence_type}\n"
                    f"*Descripción:* {description}\n"
                    f"*Archivos:*\n{files_text}"
                )
            )
    
        @self.router.command(r"investigar (\d{4}-\d{3}) \"(.+)\"")
        async def handle_investigation(text: str, event: Dict[str, Any]):
            match = re.match(r"investigar (\d{4}-\d{3}) \"(.+)\"", text)
            case_id = match.group(1)
            aspect = match.group(2)
            
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type="Investigación Iniciada",
                description=f"Aspecto investigado: {aspect}"
            )
    
        @self.router.command(r"concluir (\d{4}-\d{3}) \"(.+)\"")
        async def handle_conclusion(text: str, event: Dict[str, Any]):
            match = re.match(r"concluir (\d{4}-\d{3}) \"(.+)\"", text)
            case_id = match.group(1)
            result = match.group(2)
            
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type="Investigación Concluida",
                description=result
            )
    
    async def handle_message(self, event: Dict[str, Any]):
        """Handle incoming messages"""
        # Skip messages from the bot itself
        if event.get("user") == self.bot_id:
            return
            
        text = event.get("text", "").strip()
        
        # Try to handle as command
        if await self.router.handle_command(text, event):
            return
            
        # Handle file uploads
        if event.get("files"):
            await self.handle_file_upload(event)
            return
            
        # Default response
        await self.send_message(
            channel=event["channel"],
            text="Lo siento, no entiendo ese comando. Escribe `ayuda` para ver los comandos disponibles.",
            thread_ts=event.get("thread_ts")
        )
    
    async def handle_mention(self, event: Dict[str, Any]):
        """Handle when the bot is mentioned"""
        text = event.get("text", "").replace(f"<@{self.bot_id}>", "").strip()
        
        # Try to handle as command
        if await self.router.handle_command(text, event):
            return
            
        # Default response
        await self.send_message(
            channel=event["channel"],
            text="¿En qué puedo ayudarte? Escribe `ayuda` para ver los comandos disponibles.",
            thread_ts=event.get("thread_ts")
        )
    
    async def handle_file_upload(self, event: Dict[str, Any]):
        """Handle file uploads"""
        files = event.get("files", [])
        
        for file in files:
            # Try to extract case number from channel name or thread
            case_id = None
            channel_info = await self.web_client.conversations_info(
                channel=event["channel"]
            )
            channel_name = channel_info["channel"]["name"]
            if channel_name.startswith("caso-"):
                case_id = channel_name.replace("caso-", "")
            
            await self.notifier.send_notification(
                channel=event["channel"],
                title="Documento Recibido",
                message=(
                    f"*Archivo:* {file['name']}\n"
                    f"*Tipo:* {file['filetype']}\n"
                    f"*Tamaño:* {file['size']} bytes\n"
                    + (f"*Caso:* {case_id}\n" if case_id else "")
                ),
                notification_type="info",
                thread_ts=event.get("thread_ts")
            )
    
    async def handle_command(self, command: str, args: str, event: Dict[str, Any]):
        """Handle slash commands"""
        if command == "/acusar":
            await self.router.handle_command(f"acusar {args}", event)
        elif command == "/prueba":
            await self.router.handle_command(f"prueba {args}", event)
        elif command == "/ayuda":
            await self.router.handle_command("ayuda", event)
