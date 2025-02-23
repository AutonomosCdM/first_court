"""
Slack Client for managing communication and interactions.
"""

import os
import logging
from typing import Dict, Any, Optional, List

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackClient:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Slack client with authentication token.
        
        Args:
            token (str, optional): Slack Bot User OAuth Token. 
                                   Defaults to environment variable SLACK_BOT_TOKEN.
        """
        self.token = token or os.getenv('SLACK_BOT_TOKEN')
        if not self.token:
            raise ValueError("Slack Bot Token is required. Set SLACK_BOT_TOKEN environment variable.")
        
        self.client = WebClient(token=self.token)
        self.logger = logging.getLogger(__name__)

    def send_message(self, channel: str, message: str, thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to a specific Slack channel.
        
        Args:
            channel (str): Channel ID or name
            message (str): Message content
            thread_ts (str, optional): Timestamp of thread to reply in
        
        Returns:
            Dict containing Slack API response
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                thread_ts=thread_ts
            )
            return response
        except SlackApiError as e:
            self.logger.error(f"Error sending message: {e}")
            raise

    def create_thread_for_case(self, channel: str, case_summary: Dict[str, Any]) -> str:
        """
        Create a new thread for a specific case with initial summary.
        
        Args:
            channel (str): Channel to create thread in
            case_summary (dict): Summary of the case
        
        Returns:
            str: Thread timestamp
        """
        try:
            initial_message = f"*Nuevo Caso Judicial*\n" \
                              f"Tipo de Caso: {case_summary.get('case_type', 'No especificado')}\n" \
                              f"Descripción: {case_summary.get('content', 'Sin descripción')}"
            
            response = self.client.chat_postMessage(
                channel=channel,
                text=initial_message,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": initial_message
                        }
                    }
                ]
            )
            return response['ts']  # Thread timestamp
        except SlackApiError as e:
            self.logger.error(f"Error creating case thread: {e}")
            raise

    def add_thread_reply(self, channel: str, thread_ts: str, agent_name: str, message: str) -> Dict[str, Any]:
        """
        Add a reply to an existing thread from a specific agent.
        
        Args:
            channel (str): Channel of the thread
            thread_ts (str): Timestamp of the thread
            agent_name (str): Name of the agent sending the message
            message (str): Content of the message
        
        Returns:
            Dict containing Slack API response
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=f"*{agent_name}*: {message}"
            )
            return response
        except SlackApiError as e:
            self.logger.error(f"Error adding thread reply: {e}")
            raise

    def list_channels(self) -> List[Dict[str, Any]]:
        """
        List all channels the bot has access to.
        
        Returns:
            List of channel dictionaries
        """
        try:
            response = self.client.conversations_list()
            return response['channels']
        except SlackApiError as e:
            self.logger.error(f"Error listing channels: {e}")
            raise

    def create_channel(self, name: str) -> Dict[str, Any]:
        """
        Create a new Slack channel.
        
        Args:
            name (str): Name of the channel to create
        
        Returns:
            Dict containing channel information
        """
        try:
            response = self.client.conversations_create(
                name=name,
                is_private=False  # Public channel
            )
            return response['channel']
        except SlackApiError as e:
            self.logger.error(f"Error creating channel: {e}")
            raise
