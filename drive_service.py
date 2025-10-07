#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Service - Upload foto bukti ke Google Drive
"""

import os
import json
import time
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

class DriveService:
    def __init__(self):
        self.health_status = True
        self.service = None
        self.folder_id = None
        
        # Initialize Google Drive connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Google Drive connection"""
        try:
            # Setup credentials
            scope = ['https://www.googleapis.com/auth/drive']
            
            # Try to load credentials from file
            if os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            else:
                # Fallback: try environment variable
                creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
                if creds_json:
                    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scope)
                else:
                    raise Exception("No credentials found")
            
            # Initialize service
            self.service = build('drive', 'v3', credentials=creds)
            
            # Create or find bot folder
            self.folder_id = self._create_or_find_folder()
            
            self.health_status = True
            print("✅ Google Drive connected successfully")
            
        except Exception as e:
            self.health_status = False
            print(f"❌ Error connecting to Google Drive: {str(e)}")
    
    def _create_or_find_folder(self) -> Optional[str]:
        """Create or find the bot folder"""
        try:
            if not self.service:
                return None
            
            # Search for existing folder
            query = "name='Bos Upety Bot Bukti' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            
            if files:
                return files[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': 'Bos Upety Bot Bukti',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            print(f"✅ Created folder: {folder.get('id')}")
            return folder.get('id')
            
        except Exception as e:
            print(f"Error creating/finding folder: {str(e)}")
            return None
    
    def upload_image_from_url(self, image_url: str, filename: str = None) -> Optional[str]:
        """
        Upload image from URL to Google Drive
        
        Args:
            image_url: URL gambar
            filename: Nama file (optional)
            
        Returns:
            str: Google Drive file ID atau None jika gagal
        """
        try:
            if not self.service or not self.folder_id:
                return None
            
            # Download image
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                print(f"Failed to download image: {response.status_code}")
                return None
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"bukti_{timestamp}.jpg"
            
            # Save to temporary file
            temp_file = f"temp_{filename}"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # Upload to Drive
            file_id = self._upload_file(temp_file, filename)
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return file_id
            
        except Exception as e:
            print(f"Error uploading image from URL: {str(e)}")
            return None
    
    def upload_file(self, file_path: str, filename: str = None) -> Optional[str]:
        """
        Upload file to Google Drive
        
        Args:
            file_path: Path ke file
            filename: Nama file di Drive (optional)
            
        Returns:
            str: Google Drive file ID atau None jika gagal
        """
        try:
            if not self.service or not self.folder_id:
                return None
            
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None
            
            if not filename:
                filename = os.path.basename(file_path)
            
            return self._upload_file(file_path, filename)
            
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None
    
    def _upload_file(self, file_path: str, filename: str) -> Optional[str]:
        """Internal method to upload file"""
        try:
            # Retry mechanism
            for attempt in range(3):
                try:
                    # File metadata
                    file_metadata = {
                        'name': filename,
                        'parents': [self.folder_id]
                    }
                    
                    # Media upload
                    media = MediaFileUpload(file_path, resumable=True)
                    
                    # Upload file
                    file = self.service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    # Make file publicly viewable
                    self.service.permissions().create(
                        fileId=file.get('id'),
                        body={'role': 'reader', 'type': 'anyone'}
                    ).execute()
                    
                    self.health_status = True
                    print(f"✅ File uploaded: {filename} (ID: {file.get('id')})")
                    return file.get('id')
                    
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        raise e
                    time.sleep(1)  # Wait before retry
                    
        except Exception as e:
            self.health_status = False
            print(f"❌ Error uploading file: {str(e)}")
            return None
    
    def get_file_url(self, file_id: str) -> Optional[str]:
        """
        Get public URL for file
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            str: Public URL atau None jika gagal
        """
        try:
            if not self.service:
                return None
            
            # Get file info
            file = self.service.files().get(fileId=file_id, fields='webViewLink').execute()
            return file.get('webViewLink')
            
        except Exception as e:
            print(f"Error getting file URL: {str(e)}")
            return None
    
    def get_direct_download_url(self, file_id: str) -> Optional[str]:
        """
        Get direct download URL
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            str: Direct download URL
        """
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            bool: True jika berhasil
        """
        try:
            if not self.service:
                return False
            
            self.service.files().delete(fileId=file_id).execute()
            print(f"✅ File deleted: {file_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
    
    def list_files(self, limit: int = 10) -> list:
        """
        List files in the bot folder
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            list: List of file information
        """
        try:
            if not self.service or not self.folder_id:
                return []
            
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                pageSize=limit,
                fields="files(id, name, createdTime, size, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def get_folder_info(self) -> Dict[str, Any]:
        """
        Get folder information
        
        Returns:
            Dict: Folder information
        """
        try:
            if not self.service or not self.folder_id:
                return {}
            
            folder = self.service.files().get(fileId=self.folder_id, fields='id,name,createdTime,size').execute()
            
            # Get file count
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, fields="files(id)").execute()
            file_count = len(results.get('files', []))
            
            return {
                'id': folder.get('id'),
                'name': folder.get('name'),
                'created_time': folder.get('createdTime'),
                'file_count': file_count,
                'url': f"https://drive.google.com/drive/folders/{self.folder_id}"
            }
            
        except Exception as e:
            print(f"Error getting folder info: {str(e)}")
            return {}
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up old files (older than specified days)
        
        Args:
            days: Number of days to keep files
            
        Returns:
            int: Number of files deleted
        """
        try:
            if not self.service or not self.folder_id:
                return 0
            
            # Calculate cutoff date
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            cutoff_iso = datetime.fromtimestamp(cutoff_date).isoformat() + 'Z'
            
            # Find old files
            query = f"'{self.folder_id}' in parents and trashed=false and createdTime < '{cutoff_iso}'"
            results = self.service.files().list(q=query, fields="files(id, name, createdTime)").execute()
            old_files = results.get('files', [])
            
            # Delete old files
            deleted_count = 0
            for file in old_files:
                if self.delete_file(file['id']):
                    deleted_count += 1
            
            print(f"✅ Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old files: {str(e)}")
            return 0
    
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.health_status
    
    def reconnect(self) -> bool:
        """Reconnect to Google Drive"""
        try:
            self._initialize_connection()
            return self.health_status
        except Exception as e:
            print(f"Error reconnecting: {str(e)}")
            return False
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information
        
        Returns:
            Dict: Storage information
        """
        try:
            if not self.service:
                return {}
            
            # Get about info (includes storage quota)
            about = self.service.about().get(fields='storageQuota').execute()
            quota = about.get('storageQuota', {})
            
            return {
                'limit': int(quota.get('limit', 0)) if quota.get('limit') else None,
                'usage': int(quota.get('usage', 0)) if quota.get('usage') else 0,
                'usage_in_drive': int(quota.get('usageInDrive', 0)) if quota.get('usageInDrive') else 0,
                'usage_in_drive_trash': int(quota.get('usageInDriveTrash', 0)) if quota.get('usageInDriveTrash') else 0
            }
            
        except Exception as e:
            print(f"Error getting storage info: {str(e)}")
            return {}
