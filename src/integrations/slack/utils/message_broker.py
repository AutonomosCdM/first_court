from typing import Dict, Any, Optional, List
import json
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

class MessageBroker:
    def __init__(self, web_client: AsyncWebClient):
        self.web_client = web_client
        
    async def broadcast_to_channel(
        self,
        channel: str,
        message: str,
        thread_ts: Optional[str] = None,
        mentions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Broadcast a message to a channel, optionally mentioning specific users
        
        Args:
            channel: Channel ID
            message: Message text
            thread_ts: Thread timestamp if replying to thread
            mentions: List of user IDs to mention
        """
        try:
            # Add mentions if specified
            if mentions:
                mentions_text = " ".join([f"<@{user_id}>" for user_id in mentions])
                message = f"{mentions_text}\n{message}"
            
            return await self.web_client.chat_postMessage(
                channel=channel,
                text=message,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            print(f"❌ Error broadcasting message: {e.response['error']}")
            raise
    
    async def create_case_channel(
        self, 
        case_number: str,
        members: Optional[List[str]] = None
    ) -> str:
        """
        Create a new channel for a case
        
        Args:
            case_number: Case number/identifier
            members: List of user IDs to invite
            
        Returns:
            str: Created channel ID
        """
        try:
            # Create channel name (caso-2025-001 -> caso-2025-001)
            channel_name = f"caso-{case_number.replace('/', '-').lower()}"
            
            # Create channel
            response = await self.web_client.conversations_create(
                name=channel_name,
                is_private=False
            )
            channel_id = response["channel"]["id"]
            
            # Invite members if specified
            if members:
                await self.web_client.conversations_invite(
                    channel=channel_id,
                    users=members
                )
            
            return channel_id
            
        except SlackApiError as e:
            print(f"❌ Error creating case channel: {e.response['error']}")
            raise
    
    async def get_channel_history(
        self,
        channel: str,
        limit: int = 100,
        oldest: Optional[str] = None,
        latest: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get message history from a channel
        
        Args:
            channel: Channel ID
            limit: Number of messages to return
            oldest: Start of time range
            latest: End of time range
        """
        try:
            response = await self.web_client.conversations_history(
                channel=channel,
                limit=limit,
                oldest=oldest,
                latest=latest
            )
            return response["messages"]
        except SlackApiError as e:
            print(f"❌ Error getting channel history: {e.response['error']}")
            raise
    
    async def get_thread_replies(
        self,
        channel: str,
        thread_ts: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get replies in a thread
        
        Args:
            channel: Channel ID
            thread_ts: Parent message timestamp
            limit: Number of replies to return
        """
        try:
            response = await self.web_client.conversations_replies(
                channel=channel,
                ts=thread_ts,
                limit=limit
            )
            return response["messages"]
        except SlackApiError as e:
            print(f"❌ Error getting thread replies: {e.response['error']}")
            raise
    
    async def update_message(
        self,
        channel: str,
        ts: str,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing message
        
        Args:
            channel: Channel ID
            ts: Message timestamp
            text: New message text
            blocks: New block kit blocks
        """
        try:
            return await self.web_client.chat_update(
                channel=channel,
                ts=ts,
                text=text,
                blocks=blocks
            )
        except SlackApiError as e:
            print(f"❌ Error updating message: {e.response['error']}")
            raise
