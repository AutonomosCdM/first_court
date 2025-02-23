import re
from typing import Dict, Any, Optional
from datetime import datetime
import os
import uuid

from integrations.slack.base.event_handler import BaseSlackHandler
from integrations.slack.base.command_router import CommandRouter
from integrations.slack.utils.message_broker import MessageBroker
from integrations.slack.utils.notification import NotificationManager
from integrations.slack.utils.document_handler import DocumentHandler

# Import the database class
from AgentCourt.EMDB.db import db as DatabaseManager

class SecretarySlackApp(BaseSlackHandler):
    def __init__(self):
        super().__init__(env_prefix="SECRETARY")
        
        # Initialize database for the secretary
        self.db = DatabaseManager(agent_name="secretary")
        
        # Initialize command router
        self.router = CommandRouter()
        
        # Register commands
        self.register_commands()
        
    async def initialize(self):
        """Initialize the Secretary app"""
        await super().initialize()
        
        # Initialize utilities
        self.broker = MessageBroker(self.web_client)
        self.notifier = NotificationManager(self.web_client)
        self.doc_handler = DocumentHandler(self.web_client)
        
    def register_commands(self):
        """Register command handlers"""
        
        @self.router.command(r"ayuda")
        async def handle_help(text: str, event: Dict[str, Any]):
            help_text = """
*Comandos Disponibles:*
• `caso nuevo [descripción]` - Crear nuevo caso
• `caso [número]` - Consultar estado de un caso
• `documento [tipo] [caso]` - Subir documento
• `audiencia [fecha] [caso]` - Agendar audiencia
• `plazo [fecha] [descripción] [caso]` - Registrar plazo
• `ayuda` - Mostrar este mensaje

*Ejemplos:*
• `caso nuevo Demanda por incumplimiento de contrato`
• `caso 2025-001`
• `documento demanda 2025-001`
• `audiencia 2024-03-01 2025-001`
• `plazo 2024-03-15 "Presentación de pruebas" 2025-001`
            """
            
            await self.send_message(
                channel=event["channel"],
                text=help_text,
                thread_ts=event.get("thread_ts")
            )
    
        @self.router.command(r"caso nuevo (.*)")
        async def handle_new_case(text: str, event: Dict[str, Any]):
            description = re.match(r"caso nuevo (.*)", text).group(1)
            
            # Generate case number (YYYY-NNN)
            year = datetime.now().year
            
            # Use database to get next case number
            # This is a simple implementation. In a real-world scenario, 
            # you might want a more robust method to generate unique case numbers
            case_number_query = f"Get next case number for {year}"
            last_case = self.db.query_case(case_number_query)
            
            # If no previous case, start with 001
            number = "001" if not last_case else str(int(last_case.split("-")[-1]) + 1).zfill(3)
            case_id = f"{year}-{number}"
            
            # Prepare case metadata
            case_metadata = {
                "id": str(uuid.uuid4()),
                "case_number": case_id,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "status": "En Proceso",
                "channel_id": None  # Will be updated after channel creation
            }
            
            # Create case channel
            channel_id = await self.broker.create_case_channel(case_id)
            case_metadata["channel_id"] = channel_id
            
            # Store case in database
            self.db.add_to_case(
                id=case_metadata["id"], 
                document=f"Caso {case_id}: {description}",
                metadata=case_metadata
            )
            
            # Send initial message
            await self.notifier.send_case_update(
                channel=channel_id,
                case_number=case_id,
                update_type="Caso Creado",
                description=description
            )
            
            # Notify original channel
            await self.notifier.send_notification(
                channel=event["channel"],
                title="Caso Creado",
                message=f"Se ha creado el caso {case_id}\nCanal: <#{channel_id}>",
                notification_type="success",
                thread_ts=event.get("thread_ts")
            )
    
        @self.router.command(r"caso (\d{4}-\d{3})")
        async def handle_case_status(text: str, event: Dict[str, Any]):
            case_id = re.match(r"caso (\d{4}-\d{3})", text).group(1)
            
            # Query case from database
            case_query = f"Find case {case_id}"
            case_info = self.db.query_case_metadatas(case_query)
            
            # Default to basic information if not found
            status = case_info.get("status", "En Proceso")
            last_update = case_info.get("created_at", datetime.now().isoformat())
            next_deadline = "Sin plazos registrados"
            
            status_text = (
                f"*Estado del Caso {case_id}*\n"
                f"• *Estado:* {status}\n"
                f"• *Última actualización:* {last_update}\n"
                f"• *Próximo plazo:* {next_deadline}\n"
            )
            
            await self.send_message(
                channel=event["channel"],
                text=status_text,
                thread_ts=event.get("thread_ts")
            )
    
        @self.router.command(r"audiencia (\d{4}-\d{2}-\d{2}) (\d{4}-\d{3})")
        async def handle_schedule_hearing(text: str, event: Dict[str, Any]):
            match = re.match(r"audiencia (\d{4}-\d{2}-\d{2}) (\d{4}-\d{3})", text)
            date = match.group(1)
            case_id = match.group(2)
            
            # Update case with hearing information
            hearing_metadata = {
                "id": str(uuid.uuid4()),
                "case_number": case_id,
                "hearing_date": date,
                "scheduled_at": datetime.now().isoformat()
            }
            
            # Store hearing information in database
            self.db.add_to_case(
                id=hearing_metadata["id"],
                document=f"Audiencia programada para {case_id} el {date}",
                metadata=hearing_metadata
            )
            
            await self.notifier.send_notification(
                channel=event["channel"],
                title="Audiencia Agendada",
                message=(
                    f"*Caso:* {case_id}\n"
                    f"*Fecha:* {date}\n"
                ),
                notification_type="success",
                thread_ts=event.get("thread_ts")
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
            
            # Prepare document metadata
            doc_metadata = {
                "id": str(uuid.uuid4()),
                "filename": file['name'],
                "filetype": file['filetype'],
                "size": file['size'],
                "case_number": case_id,
                "uploaded_at": datetime.now().isoformat()
            }
            
            # Store document information in database
            self.db.add_to_case(
                id=doc_metadata["id"],
                document=f"Documento {file['name']} para caso {case_id}",
                metadata=doc_metadata
            )
            
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
        if command == "/caso":
            await self.router.handle_command(f"caso {args}", event)
        elif command == "/audiencia":
            await self.router.handle_command(f"audiencia {args}", event)
        elif command == "/ayuda":
            await self.router.handle_command("ayuda", event)
