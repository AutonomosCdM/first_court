"""
Slack Logging Handler for structured logging of system events.
"""

import logging
from typing import Dict, Any, Optional

from .client import SlackClient
from .channel_manager import ChannelManager

class SlackLoggingHandler(logging.Handler):
    def __init__(self, 
                 slack_client: Optional[SlackClient] = None, 
                 channel_manager: Optional[ChannelManager] = None,
                 log_level: int = logging.INFO):
        """
        Initialize Slack Logging Handler.
        
        Args:
            slack_client (SlackClient, optional): Slack client instance
            channel_manager (ChannelManager, optional): Channel manager instance
            log_level (int, optional): Minimum log level to send to Slack
        """
        super().__init__()
        self.slack_client = slack_client or SlackClient()
        self.channel_manager = channel_manager or ChannelManager(self.slack_client)
        self.setLevel(log_level)
        
        # Formatter for log messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to Slack.
        
        Args:
            record (LogRecord): Log record to be emitted
        """
        try:
            # Format the log message
            msg = self.format(record)
            
            # Determine the appropriate channel based on log level
            if record.levelno >= logging.ERROR:
                channel_type = 'agent_logs'
            elif record.levelno >= logging.WARNING:
                channel_type = 'legal_reflections'
            else:
                channel_type = 'cases'
            
            # Get the channel ID
            channel_id = self.channel_manager.get_channel_id(channel_type)
            
            # Prepare message with color coding for severity
            if record.levelno >= logging.ERROR:
                formatted_msg = f":red_circle: *ERROR* ```{msg}```"
            elif record.levelno >= logging.WARNING:
                formatted_msg = f":warning: *WARNING* ```{msg}```"
            else:
                formatted_msg = f":information_source: *INFO* ```{msg}```"
            
            # Send message to Slack
            self.slack_client.send_message(channel_id, formatted_msg)
        
        except Exception:
            # Fallback to default error handling if Slack logging fails
            self.handleError(record)

    def create_performance_report(self, metrics: Dict[str, Any]) -> None:
        """
        Create a performance report in Slack.
        
        Args:
            metrics (dict): Performance metrics to report
        """
        channel_id = self.channel_manager.get_channel_id('case_summaries')
        
        # Format performance report
        report = "*Sistema AgentCourt - Informe de Rendimiento*\n"
        for key, value in metrics.items():
            report += f"• {key}: {value}\n"
        
        # Send performance report
        self.slack_client.send_message(channel_id, report)

    def log_agent_performance(self, agent_name: str, performance_data: Dict[str, Any]) -> None:
        """
        Log individual agent performance.
        
        Args:
            agent_name (str): Name of the agent
            performance_data (dict): Performance metrics for the agent
        """
        channel_id = self.channel_manager.get_channel_id('agent_logs')
        
        # Format agent performance log
        performance_log = f"*Rendimiento de Agente: {agent_name}*\n"
        for metric, value in performance_data.items():
            performance_log += f"• {metric}: {value}\n"
        
