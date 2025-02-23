import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

class SlackEventHandler:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Slack tokens
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        
        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
        
        self.bot_id = None
        self.session = None
        self.web_client = None
    
    async def initialize(self):
        """Initialize the event handler"""
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
    
    async def send_message(self, channel: str, text: str, thread_ts: str = None):
        """Send a message to a channel"""
        try:
            await self.web_client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts
            )
            print(f"✅ Message sent to {channel}")
        except SlackApiError as e:
            print(f"❌ Error sending message: {e.response['error']}")
    
    async def monitor_channel(self, channel_id: str):
        """Monitor a channel for messages"""
        try:
            while True:
                # Get channel history
                response = await self.web_client.conversations_history(
                    channel=channel_id,
                    limit=1
                )
                
                if response["ok"] and response["messages"]:
                    message = response["messages"][0]
                    
                    # Skip messages from the bot itself
                    if message.get("user") == self.bot_id:
                        await asyncio.sleep(1)
                        continue
                    
                    text = message.get("text", "").strip()
                    print(f"📩 New message: {text}")
                    
                    # Generate and send response
                    response = f"👋 ¡Gracias por tu mensaje! Estoy procesando: '{text}'"
                    await self.send_message(
                        channel=channel_id,
                        text=response,
                        thread_ts=message.get("ts")
                    )
                
                await asyncio.sleep(1)
                
        except SlackApiError as e:
            print(f"❌ Error monitoring channel: {e.response['error']}")
    
    async def start(self):
        """Start the event handler"""
        try:
            print("🚀 Starting Slack event handler...")
            await self.initialize()
            
            # Send a test message to verify connection
            test_channel = "C08DM64374H"  # Your channel ID
            await self.send_message(
                channel=test_channel,
                text="🤖 ¡Hola! El agente de comunicación está en línea y listo para ayudar. 📜⚖️"
            )
            
            print("✅ Connected and ready!")
            print(f"👀 Monitoring channel {test_channel}")
            
            # Monitor the channel
            await self.monitor_channel(test_channel)
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if self.session:
                await self.session.close()

async def main():
    handler = SlackEventHandler()
    try:
        await handler.start()
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
