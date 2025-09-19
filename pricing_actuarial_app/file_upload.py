"""
File upload operations for the pricing cell automation app.
"""
import logging
from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)

class FileUploadManager:
    """Manages file uploads to Databricks volumes."""
    
    def __init__(self):
        """Initialize file upload manager."""
        self.workspace_client = WorkspaceClient()  # picks from env vars
        self.volume_path = "/Volumes/shirlywang_insurance/fa_pricing/user_uploaded_brochures"
    
    def upload_file_to_volume(self, file_content, filename, volume_path=None):
        """Upload a file to the specified volume path."""
        if volume_path is None:
            volume_path = self.volume_path
            
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

# Global file upload manager instance
file_upload_manager = FileUploadManager()
