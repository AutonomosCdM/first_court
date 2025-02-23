"""
Channel Manager for handling Slack channel operations specific to AgentCourt.
"""

import os
from typing import Dict, Any, Optional, List

from .client import SlackClient
from .message_formatter import MessageFormatter

class ChannelManager:
    CHANNELS = {
        'cases': 'casos-judiciales',
        'agent_logs': 'logs-agentes',
        'legal_reflections': 'reflexiones-legales',
        'case_summaries': 'resumenes-casos'
    }

    def __init__(self, slack_client: Optional[SlackClient] = None):
        """
        Initialize ChannelManager with optional Slack client.
        
        Args:
            slack_client (SlackClient, optional): Slack client instance
        """
        self.slack_client = slack_client or SlackClient()
        self.channel_ids = {}

    def ensure_channels_exist(self) -> None:
        """
        Ensure all required channels exist, creating them if necessary.
        """
        existing_channels = {channel['name']: channel['id'] 
                             for channel in self.slack_client.list_channels()}
        
        for key, channel_name in self.CHANNELS.items():
            if channel_name not in existing_channels:
                new_channel = self.slack_client.create_channel(channel_name)
                self.channel_ids[key] = new_channel['id']
                print(f"Created new channel: #{channel_name}")
            else:
                self.channel_ids[key] = existing_channels[channel_name]

    def get_channel_id(self, channel_type: str) -> str:
        """
        Get the channel ID for a specific channel type.
        
        Args:
            channel_type (str): Type of channel (from CHANNELS keys)
        
        Returns:
            str: Channel ID
        
        Raises:
            KeyError: If channel type is not found
        """
        if channel_type not in self.channel_ids:
            self.ensure_channels_exist()
        
        return self.channel_ids[channel_type]

    def post_case_summary(self, case_summary: Dict[str, Any]) -> str:
        """
        Post a case summary to the cases channel.
        
        Args:
            case_summary (dict): Case summary details
        
        Returns:
            str: Thread timestamp of the posted message
        """
        channel_id = self.get_channel_id('cases')
        blocks = MessageFormatter.create_slack_blocks_for_case(case_summary)
        
        response = self.slack_client.client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text=MessageFormatter.format_case_summary(case_summary)
        )
        
        return response['ts']

    def log_agent_interaction(self, agent_name: str, role: str, message: str) -> None:
        """
        Log an agent interaction to the agent logs channel.
        
        Args:
            agent_name (str): Name of the agent
            role (str): Role of the agent
            message (str): Interaction message
        """
        channel_id = self.get_channel_id('agent_logs')
        formatted_message = MessageFormatter.format_agent_message(agent_name, role, message)
        
        self.slack_client.send_message(channel_id, formatted_message)

    def record_legal_reflection(self, legal_reflection: Dict[str, Any]) -> None:
        """
        Record legal reflection to the legal reflections channel.
        
        Args:
            legal_reflection (dict): Legal reflection details
        """
        channel_id = self.get_channel_id('legal_reflections')
        formatted_reflection = MessageFormatter.format_legal_reflection(legal_reflection)
        
        self.slack_client.send_message(channel_id, formatted_reflection)
