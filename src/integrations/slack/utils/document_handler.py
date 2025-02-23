from typing import Dict, Any, Optional, List, BinaryIO
import os
import aiohttp
from datetime import datetime
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

class DocumentHandler:
    def __init__(self, web_client: AsyncWebClient):
        self.web_client = web_client
        
    async def upload_document(
        self,
        channel: str,
        file: BinaryIO,
        filename: str,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a document to Slack
        
        Args:
            channel: Channel ID
            file: File object to upload
            filename: Name for the uploaded file
            title: Title for the upload
            initial_comment: Initial comment for the upload
            thread_ts: Thread timestamp if replying to thread
        """
        try:
            return await self.web_client.files_upload_v2(
                channel=channel,
                file=file,
                filename=filename,
                title=title,
                initial_comment=initial_comment,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            print(f"❌ Error uploading document: {e.response['error']}")
            raise
    
    async def download_file(
        self,
        file_url: str,
        output_dir: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Download a file from Slack
        
        Args:
            file_url: URL of the file to download
            output_dir: Directory to save the file
            filename: Optional filename override
            
        Returns:
            str: Path to downloaded file
        """
        try:
            headers = {"Authorization": f"Bearer {self.web_client.token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download file: {response.status}")
                    
                    # Use provided filename or generate one
                    if not filename:
                        content_disposition = response.headers.get("content-disposition", "")
                        if "filename=" in content_disposition:
                            filename = content_disposition.split("filename=")[1].strip('"')
                        else:
                            filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    # Ensure output directory exists
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Save file
                    file_path = os.path.join(output_dir, filename)
                    with open(file_path, "wb") as f:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                    
                    return file_path
                    
        except Exception as e:
            print(f"❌ Error downloading file: {str(e)}")
            raise
    
    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Get information about a file
        
        Args:
            file_id: File ID
        """
        try:
            return await self.web_client.files_info(file=file_id)
        except SlackApiError as e:
            print(f"❌ Error getting file info: {e.response['error']}")
            raise
    
    async def share_file(
        self,
        file_id: str,
        channels: List[str]
    ) -> Dict[str, Any]:
        """
        Share a file to additional channels
        
        Args:
            file_id: File ID to share
            channels: List of channel IDs to share to
        """
        try:
            return await self.web_client.files_share(
                file=file_id,
                channels=",".join(channels)
            )
        except SlackApiError as e:
            print(f"❌ Error sharing file: {e.response['error']}")
            raise
    
    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a file
        
        Args:
            file_id: File ID to delete
        """
        try:
            return await self.web_client.files_delete(file=file_id)
        except SlackApiError as e:
            print(f"❌ Error deleting file: {e.response['error']}")
            raise
    
    async def upload_case_document(
        self,
        channel: str,
        case_number: str,
        doc_type: str,
        file: BinaryIO,
        filename: str,
        description: Optional[str] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a case-related document with proper formatting
        
        Args:
            channel: Channel ID
            case_number: Case number/identifier
            doc_type: Type of document
            file: File to upload
            filename: Name for the file
            description: Optional description
            thread_ts: Thread timestamp if replying to thread
        """
        # Format title and comment
        title = f"📄 {doc_type} - Caso {case_number}"
        
        comment = f"*Documento:* {doc_type}\n*Caso:* {case_number}"
        if description:
            comment += f"\n*Descripción:* {description}"
        
        return await self.upload_document(
            channel=channel,
            file=file,
            filename=filename,
            title=title,
            initial_comment=comment,
            thread_ts=thread_ts
        )
