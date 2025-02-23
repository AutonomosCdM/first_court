from typing import Dict, Any, Optional, List
from datetime import datetime
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

class NotificationManager:
    def __init__(self, web_client: AsyncWebClient):
        self.web_client = web_client
        
    async def send_notification(
        self,
        channel: str,
        title: str,
        message: str,
        notification_type: str = "info",
        mentions: Optional[List[str]] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a formatted notification
        
        Args:
            channel: Channel ID
            title: Notification title
            message: Notification message
            notification_type: Type of notification (info, warning, error, success)
            mentions: List of user IDs to mention
            thread_ts: Thread timestamp if replying to thread
        """
        # Define notification styles
        styles = {
            "info": {
                "emoji": "ℹ️",
                "color": "#2196F3"
            },
            "warning": {
                "emoji": "⚠️",
                "color": "#FFC107"
            },
            "error": {
                "emoji": "❌",
                "color": "#F44336"
            },
            "success": {
                "emoji": "✅",
                "color": "#4CAF50"
            }
        }
        
        style = styles.get(notification_type, styles["info"])
        
        # Build mentions text if specified
        mentions_text = ""
        if mentions:
            mentions_text = " ".join([f"<@{user_id}>" for user_id in mentions])
        
        # Create blocks for rich formatting
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{style['emoji']} *{title}*\n{message}"
                }
            }
        ]
        
        if mentions_text:
            blocks.append({
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"Para: {mentions_text}"
                }]
            })
        
        try:
            return await self.web_client.chat_postMessage(
                channel=channel,
                text=f"{style['emoji']} {title}\n{message}",
                blocks=blocks,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            print(f"❌ Error sending notification: {e.response['error']}")
            raise
    
    async def send_deadline_reminder(
        self,
        channel: str,
        case_number: str,
        deadline_type: str,
        deadline: datetime,
        assignees: List[str],
        details: Optional[str] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a deadline reminder notification
        
        Args:
            channel: Channel ID
            case_number: Case number/identifier
            deadline_type: Type of deadline (e.g. "Presentación de Pruebas")
            deadline: Deadline datetime
            assignees: List of user IDs responsible
            details: Additional details
            thread_ts: Thread timestamp if replying to thread
        """
        deadline_str = deadline.strftime("%d/%m/%Y %H:%M")
        
        title = f"⏰ Recordatorio de Plazo: {deadline_type}"
        message = (
            f"*Caso:* {case_number}\n"
            f"*Plazo:* {deadline_str}\n"
            f"*Tipo:* {deadline_type}\n"
        )
        
        if details:
            message += f"*Detalles:* {details}\n"
        
        return await self.send_notification(
            channel=channel,
            title=title,
            message=message,
            notification_type="warning",
            mentions=assignees,
            thread_ts=thread_ts
        )
    
    async def send_case_update(
        self,
        channel: str,
        case_number: str,
        update_type: str,
        description: str,
        notify_users: Optional[List[str]] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a case update notification
        
        Args:
            channel: Channel ID
            case_number: Case number/identifier
            update_type: Type of update (e.g. "Nueva Resolución")
            description: Update description
            notify_users: List of user IDs to notify
            thread_ts: Thread timestamp if replying to thread
        """
        title = f"📋 Actualización de Caso: {update_type}"
        message = (
            f"*Caso:* {case_number}\n"
            f"*Actualización:* {update_type}\n"
            f"*Descripción:* {description}\n"
        )
        
        return await self.send_notification(
            channel=channel,
            title=title,
            message=message,
            notification_type="info",
            mentions=notify_users,
            thread_ts=thread_ts
        )
    
    async def send_error_notification(
        self,
        channel: str,
        error_type: str,
        description: str,
        notify_admin: bool = True,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an error notification
        
        Args:
            channel: Channel ID
            error_type: Type of error
            description: Error description
            notify_admin: Whether to notify admin users
            thread_ts: Thread timestamp if replying to thread
        """
        title = f"🚨 Error: {error_type}"
        message = f"*Descripción:* {description}"
        
        # TODO: Get admin users from configuration
        admin_users = ["U12345", "U67890"] if notify_admin else None
        
        return await self.send_notification(
            channel=channel,
            title=title,
            message=message,
            notification_type="error",
            mentions=admin_users,
            thread_ts=thread_ts
        )
