import os
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

class BaseSlackHandler(ABC):
    def __init__(self, env_prefix: str):
        """
        Initialize base Slack handler
        
        Args:
            env_prefix: Prefix for environment variables (e.g. 'SECRETARY', 'JUDGE')
        """
        load_dotenv()
        
        # Load credentials with prefix
        self.bot_token = os.getenv(f'{env_prefix}_BOT_TOKEN')
        self.app_id = os.getenv(f'{env_prefix}_SLACK_APP_ID')
        self.signing_secret = os.getenv(f'{env_prefix}_SIGNING_SECRET')
        
        if not all([self.bot_token, self.app_id, self.signing_secret]):
            raise ValueError(f"Missing required environment variables for {env_prefix}")
        
        self.bot_id = None
        self.session = None
        self.web_client = None
        
    async def initialize(self):
        """Initialize the Slack client and session"""
        # Create aiohttp session
        self.session = aiohttp.ClientSession()
        
        # Initialize web client
        self.web_client = AsyncWebClient(
            token=self.bot_token,
            session=self.session
        )
        
        # Get bot ID
        auth_response = await self.web_client.auth_test()
        self.bot_id = auth_response["user_id"]
        print(f"✅ Bot ID: {self.bot_id}")
    
    async def send_message(
        self, 
        channel: str, 
        text: str, 
        thread_ts: Optional[str] = None,
        blocks: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel
        
        Args:
            channel: Channel ID to send message to
            text: Message text
            thread_ts: Thread timestamp to reply to
            blocks: Block kit blocks for rich formatting
        """
        try:
            return await self.web_client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts,
                blocks=blocks
            )
        except SlackApiError as e:
            # Check if the error is due to channel not found
            if e.response['error'] == 'channel_not_found':
                print(f"❌ Channel {channel} not found. Skipping message.")
                return {}
            else:
                print(f"❌ Error sending message: {e.response['error']}")
                raise
    
    async def add_reaction(self, channel: str, timestamp: str, reaction: str):
        """Add a reaction to a message"""
        try:
            await self.web_client.reactions_add(
                channel=channel,
                timestamp=timestamp,
                name=reaction
            )
        except SlackApiError as e:
            print(f"❌ Error adding reaction: {e.response['error']}")
    
    async def upload_file(
        self,
        channels: str,
        file: str,
        title: Optional[str] = None,
        thread_ts: Optional[str] = None
    ):
        """Upload a file to Slack"""
        try:
            return await self.web_client.files_upload_v2(
                channels=channels,
                file=file,
                title=title,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            print(f"❌ Error uploading file: {e.response['error']}")
            raise
    
    @abstractmethod
    async def handle_message(self, event: Dict[str, Any]):
        """Handle incoming messages - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def handle_mention(self, event: Dict[str, Any]):
        """Handle mentions - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def handle_command(self, command: str, args: str, event: Dict[str, Any]):
        """Handle slash commands - must be implemented by subclasses"""
        pass
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def start(self):
        """Start the event handler"""
        try:
            print(f"🚀 Starting Slack event handler...")
            await self.initialize()
            
            # Keep alive
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await self.cleanup()
