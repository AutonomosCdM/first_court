import re
from typing import Dict, Any, Optional
from datetime import datetime
import os

from integrations.slack.base.event_handler import BaseSlackHandler
from integrations.slack.base.command_router import CommandRouter
from integrations.slack.utils.message_broker import MessageBroker
from integrations.slack.utils.notification import NotificationManager
from integrations.slack.utils.document_handler import DocumentHandler

class JudgeSlackApp(BaseSlackHandler):
    def __init__(self):
        super().__init__(env_prefix="JUDGE")
        self.router = CommandRouter()
        self.register_commands()
        
    async def initialize(self):
        """Initialize the Judge app"""
        await super().initialize()
        
        # Initialize utilities
        self.broker = MessageBroker(self.web_client)
        self.notifier = NotificationManager(self.web_client)
        self.doc_handler = DocumentHandler(self.web_client)
        
        # Optional: Uncomment and modify if you want to send a startup message
        # notification_channel = os.getenv('SLACK_NOTIFICATIONS_CHANNEL', 'C08DM64374H')
        # await self.notifier.send_notification(
        #     channel=notification_channel,
        #     title="Juez Online",
        #     message="⚖️ El Juez está en línea y listo para atender casos.",
        #     notification_type="success"
        # )
    
    def register_commands(self):
        """Register command handlers"""
        
        @self.router.command(r"ayuda")
        async def handle_help(text: str, event: Dict[str, Any]):
            help_text = """
*Comandos del Juez:*
• `resolver [caso] [tipo] [texto]` - Emitir resolución
• `audiencia [caso] [fecha] [tipo]` - Programar audiencia
• `fallo [caso] [decisión]` - Emitir fallo
• `admitir [caso]` - Admitir caso
• `rechazar [caso] [motivo]` - Rechazar caso
• `ayuda` - Mostrar este mensaje

*Ejemplos:*
• `resolver 2025-001 providencia "Traslado a la parte demandada"`
• `audiencia 2025-001 2024-03-01 "Audiencia de conciliación"`
• `fallo 2025-001 "Se acoge la demanda"`
• `admitir 2025-001`
• `rechazar 2025-001 "No cumple requisitos formales"`
            """
            
            await self.send_message(
                channel=event["channel"],
                text=help_text,
                thread_ts=event.get("thread_ts")
            )
    
        @self.router.command(r"resolver (\d{4}-\d{3}) (\w+) \"(.+)\"")
        async def handle_resolution(text: str, event: Dict[str, Any]):
            match = re.match(r"resolver (\d{4}-\d{3}) (\w+) \"(.+)\"", text)
            case_id = match.group(1)
            res_type = match.group(2)
            content = match.group(3)
            
            # Format resolution
            resolution_text = (
                f"*RESOLUCIÓN - {res_type.upper()}*\n\n"
                f"{content}\n\n"
                f"_{datetime.now().strftime('%d/%m/%Y %H:%M')}_"
            )
            
            # Send resolution
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type=f"Nueva Resolución: {res_type}",
                description=content
            )
            
            # Add reaction to original message
            if event.get("ts"):
                await self.add_reaction(
                    channel=event["channel"],
                    timestamp=event["ts"],
                    reaction="white_check_mark"
                )
    
        @self.router.command(r"fallo (\d{4}-\d{3}) \"(.+)\"")
        async def handle_ruling(text: str, event: Dict[str, Any]):
            match = re.match(r"fallo (\d{4}-\d{3}) \"(.+)\"", text)
            case_id = match.group(1)
            ruling = match.group(2)
            
            # Format ruling
            ruling_text = (
                f"*FALLO*\n\n"
                f"{ruling}\n\n"
                f"_{datetime.now().strftime('%d/%m/%Y %H:%M')}_"
            )
            
            # Send ruling
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type="Fallo Emitido",
                description=ruling
            )
            
            # Add reaction to original message
            if event.get("ts"):
                await self.add_reaction(
                    channel=event["channel"],
                    timestamp=event["ts"],
                    reaction="hammer"
                )
    
        @self.router.command(r"admitir (\d{4}-\d{3})")
        async def handle_admit(text: str, event: Dict[str, Any]):
            case_id = re.match(r"admitir (\d{4}-\d{3})", text).group(1)
            
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type="Caso Admitido",
                description="El caso ha sido admitido a tramitación."
            )
    
        @self.router.command(r"rechazar (\d{4}-\d{3}) \"(.+)\"")
        async def handle_reject(text: str, event: Dict[str, Any]):
            match = re.match(r"rechazar (\d{4}-\d{3}) \"(.+)\"", text)
            case_id = match.group(1)
            reason = match.group(2)
            
            await self.notifier.send_case_update(
                channel=f"caso-{case_id}",
                case_number=case_id,
                update_type="Caso Rechazado",
                description=f"El caso ha sido rechazado.\nMotivo: {reason}"
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
    
    async def handle_command(self, command: str, args: str, event: Dict[str, Any]):
        """Handle slash commands"""
        if command == "/resolver":
            await self.router.handle_command(f"resolver {args}", event)
        elif command == "/fallo":
            await self.router.handle_command(f"fallo {args}", event)
        elif command == "/ayuda":
            await self.router.handle_command("ayuda", event)
