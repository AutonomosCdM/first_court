import re
from typing import Dict, Any, Optional
from datetime import datetime
import os

from integrations.slack.base.event_handler import BaseSlackHandler
from integrations.slack.base.command_router import CommandRouter
from integrations.slack.utils.message_broker import MessageBroker
from integrations.slack.utils.notification import NotificationManager
from integrations.slack.utils.document_handler import DocumentHandler

class DefenderSlackApp(BaseSlackHandler):
    def __init__(self):
        super().__init__(env_prefix="DEFENDER")
        self.router = CommandRouter()
        self.register_commands()
        
    async def initialize(self):
        """Initialize the Defender app"""
        await super().initialize()
        
        # Initialize utilities
        self.broker = MessageBroker(self.web_client)
        self.notifier = NotificationManager(self.web_client)
        self.doc_handler = DocumentHandler(self.web_client)
        
        # Optional: Uncomment and modify if you want to send a startup message
        # notification_channel = os.getenv('SLACK_NOTIFICATIONS_CHANNEL', 'C08DM64374H')
        # await self.notifier.send_notification(
        #     channel=notification_channel,
        #     title="Defensor Online",
        #     message="👨‍💼 El Defensor está en línea y listo para asistir.",
        #     notification_type="success"
        # )
    
    def register_commands(self):
        """Register command handlers"""
        
        @self.router.command(r"ayuda")
        async def handle_help(text: str, event: Dict[str, Any]):
            help_text = """
*Comandos del Defensor:*
• `defender [caso] [descripción]` - Presentar defensa
• `prueba [caso] [tipo] [descripción]` - Presentar prueba
• `recurso [caso] [tipo] [fundamento]` - Presentar recurso
• `alegar [caso] [argumento]` - Presentar alegato
• `solicitar [caso] [tipo] [detalle]` - Solicitar diligencia
• `ayuda` - Mostrar este mensaje

*Ejemplos:*
• `defender 2025-001 "Cumplimiento efectivo del contrato"`
• `prueba 2025-001 documental "Comprobantes de pago"`
• `recurso 2025-001 apelación "Errónea valoración de la prueba"`
• `alegar 2025-001 "La parte demandante no ha probado el incumplimiento"`
• `solicitar 2025-001 testigo "Declaración del supervisor"`
            """
            
            await self.send_message(
                channel=event["channel"],
                text=help_text,
                thread_ts=event.get("thread_ts")
            )
    
        @self.router.command(r"defender (\d{4}-\d{3}) \"(.+)\"")
        async def handle_defense(text: str, event: Dict[str, Any]):
            match = re.match(r"defender (\d{4}-\d{3}) \"(.+)\"", text)
            case_id = match.group(1)
            defense = match.group(2)
            
            # Format defense
            defense_text = (
                f"*DEFENSA*\n\n"
                f"{defense}\n\n"
                f"_{datetime.now().strftime('%d/%m/%Y %H:%M')}_"
            )
            
            # Send defense
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type="Nueva Defensa",
                description=defense
            )
            
            # Add reaction to original message
            if event.get("ts"):
                await self.add_reaction(
                    channel=event["channel"],
                    timestamp=event["ts"],
                    reaction="shield"
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
                update_type=f"Nueva Prueba de Defensa: {evidence_type}",
                description=(
                    f"*Tipo:* {evidence_type}\n"
                    f"*Descripción:* {description}\n"
                    f"*Archivos:*\n{files_text}"
                )
            )
    
        @self.router.command(r"recurso (\d{4}-\d{3}) (\w+) \"(.+)\"")
        async def handle_appeal(text: str, event: Dict[str, Any]):
            match = re.match(r"recurso (\d{4}-\d{3}) (\w+) \"(.+)\"", text)
            case_id = match.group(1)
            appeal_type = match.group(2)
            grounds = match.group(3)
            
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type=f"Nuevo Recurso: {appeal_type}",
                description=(
                    f"*Tipo de Recurso:* {appeal_type}\n"
                    f"*Fundamentos:* {grounds}"
                )
            )
    
        @self.router.command(r"alegar (\d{4}-\d{3}) \"(.+)\"")
        async def handle_argument(text: str, event: Dict[str, Any]):
            match = re.match(r"alegar (\d{4}-\d{3}) \"(.+)\"", text)
            case_id = match.group(1)
            argument = match.group(2)
            
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type="Nuevo Alegato",
                description=argument
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
        if command == "/defender":
            await self.router.handle_command(f"defender {args}", event)
        elif command == "/prueba":
            await self.router.handle_command(f"prueba {args}", event)
        elif command == "/ayuda":
            await self.router.handle_command("ayuda", event)
