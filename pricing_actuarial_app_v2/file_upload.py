"""
File upload operations for the pricing cell automation app.
"""
import logging
import os
from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)

class FileUploadManager:
    """Manages file uploads to Databricks volumes."""
    
    def __init__(self):
        """Initialize file upload manager."""
        try:
            # Try to initialize with explicit token
            token = os.getenv('DATABRICKS_TOKEN')
            if token:
                self.workspace_client = WorkspaceClient(host="https://e2-demo-field-eng.cloud.databricks.com", token=token)
            else:
                self.workspace_client = WorkspaceClient()  # picks from env vars
        except Exception as e:
            logger.error(f"Failed to initialize WorkspaceClient: {e}")
            # Create a mock client for basic functionality
            self.workspace_client = None
        self.volume_path = "/Volumes/shirlywang_insurance/fa_pricing/user_uploaded_brochures"
    
    def upload_file_to_volume(self, file_content, filename, volume_path=None):
        """Upload a file to the specified volume path."""
        if volume_path is None:
            volume_path = self.volume_path
            
        if self.workspace_client is None:
            logger.error("WorkspaceClient not initialized - cannot upload file")
            raise Exception("Databricks connection not available")
            
        try:
            full_path = f"{volume_path}/{filename}"
            self.workspace_client.files.upload(full_path, file_content, overwrite=True)
            logger.info(f"Uploaded {filename} to {full_path}")
            return full_path
        except Exception as e:
            logger.exception("Error uploading file to volume")
            raise
    
    def upload_multiple_files(self, file_contents, filenames, volume_path=None):
        """Upload multiple files to the volume."""
        uploaded_paths = []
        for content, filename in zip(file_contents, filenames):
            path = self.upload_file_to_volume(content, filename, volume_path)
            uploaded_paths.append(path)
        return uploaded_paths
    
    def delete_file_from_volume(self, filename, volume_path=None):
        """Delete a file from the specified volume path."""
        if volume_path is None:
            volume_path = self.volume_path
            
        if self.workspace_client is None:
            logger.error("WorkspaceClient not initialized - cannot delete file")
            raise Exception("Databricks connection not available")
            
        try:
            full_path = f"{volume_path}/{filename}"
            self.workspace_client.files.delete(full_path)
            logger.info(f"Deleted {filename} from {full_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {filename} from volume: {e}")
            return False

# Global file upload manager instance
file_upload_manager = FileUploadManager()
