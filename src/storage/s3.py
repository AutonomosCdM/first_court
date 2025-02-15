"""Amazon S3 storage client and utilities."""
from typing import Dict, Any, Optional, BinaryIO
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import mimetypes
import os
from src.config import settings

class S3Client:
    """Client for interacting with Amazon S3."""
    
    def __init__(self):
        """Initialize S3 client."""
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.S3_BUCKET
        
    def upload_file(self, file: BinaryIO, key: str,
                   metadata: Optional[Dict[str, str]] = None,
                   content_type: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to S3.
        
        Args:
            file: File-like object to upload
            key: S3 object key
            metadata: Optional metadata to attach to the object
            content_type: Optional content type, will be guessed if not provided
            
        Returns:
            Upload response metadata
        """
        if not content_type:
            content_type, _ = mimetypes.guess_type(key)
            
        extra_args = {
            'ContentType': content_type or 'application/octet-stream'
        }
        
        if metadata:
            extra_args['Metadata'] = metadata
            
        return self.client.upload_fileobj(
            file,
            self.bucket,
            key,
            ExtraArgs=extra_args
        )
    
    def download_file(self, key: str) -> BinaryIO:
        """Download a file from S3."""
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key
        )
        return response['Body']
    
    def delete_file(self, key: str):
        """Delete a file from S3."""
        return self.client.delete_object(
            Bucket=self.bucket,
            Key=key
        )
    
    def get_presigned_url(self, key: str, expires_in: int = 3600,
                         operation: str = 'get_object') -> str:
        """Generate a presigned URL for an S3 object.
        
        Args:
            key: S3 object key
            expires_in: URL expiration time in seconds
            operation: S3 operation ('get_object' or 'put_object')
            
        Returns:
            Presigned URL
        """
        try:
            return self.client.generate_presigned_url(
                operation,
                Params={
                    'Bucket': self.bucket,
                    'Key': key
                },
                ExpiresIn=expires_in
            )
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def list_files(self, prefix: str = '', max_keys: int = 1000) -> Dict[str, Any]:
        """List files in the bucket with optional prefix."""
        return self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix,
            MaxKeys=max_keys
        )
    
    def get_file_metadata(self, key: str) -> Dict[str, Any]:
        """Get metadata for a file."""
        try:
            return self.client.head_object(
                Bucket=self.bucket,
                Key=key
            )
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise

class StorageManager:
    """Manager for handling file storage operations."""
    
    def __init__(self):
        """Initialize storage manager."""
        self.s3 = S3Client()
        
    def get_storage_path(self, document_id: str, filename: str) -> str:
        """Generate storage path for a file."""
        date = datetime.now().strftime('%Y/%m/%d')
        return f"documents/{document_id}/{date}/{filename}"
    
    def cleanup_old_files(self, prefix: str, days: int = 30):
        """Clean up files older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        paginator = self.s3.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.s3.bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                if obj['LastModified'] < cutoff:
                    self.s3.delete_file(obj['Key'])
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            response = self.s3.client.list_objects_v2(
                Bucket=self.s3.bucket
            )
            
            total_size = 0
            file_count = 0
            
            while True:
                for obj in response.get('Contents', []):
                    total_size += obj['Size']
                    file_count += 1
                    
                if not response.get('IsTruncated'):
                    break
                    
                response = self.s3.client.list_objects_v2(
                    Bucket=self.s3.bucket,
                    ContinuationToken=response['NextContinuationToken']
                )
            
            return {
                'total_size': total_size,
                'file_count': file_count,
                'bucket': self.s3.bucket
            }
            
        except ClientError as e:
            print(f"Error getting storage stats: {e}")
            return None
