"""
File upload operations for the pricing cell automation app.
"""
import logging
import os

logger = logging.getLogger(__name__)

class FileUploadManager:
    """Manages file uploads to Databricks volumes."""
    
    def __init__(self):
        """Initialize file upload manager."""
        self.workspace_client = None
        self.use_dbutils = False
        
        # Check if we're in a Databricks environment
        is_databricks = (
            os.environ.get('DATABRICKS_RUNTIME_VERSION') is not None or
            os.environ.get('DATABRICKS_WORKSPACE_URL') is not None or
            os.environ.get('DATABRICKS_APP_ID') is not None
        )
        
        if is_databricks:
            logger.info("Detected Databricks environment")
            # Try using dbutils first (available in Databricks Apps)
            try:
                from databricks import dbutils
                self.dbutils = dbutils
                self.use_dbutils = True
                logger.info("Successfully initialized with dbutils")
            except Exception as e:
                logger.warning(f"dbutils not available: {e}")
                # Fall back to WorkspaceClient
                try:
                    from databricks.sdk import WorkspaceClient
                    self.workspace_client = WorkspaceClient()
                    logger.info("Successfully initialized WorkspaceClient")
                except Exception as e2:
                    logger.error(f"Failed to initialize WorkspaceClient: {e2}")
        else:
            # Not in Databricks - try WorkspaceClient with explicit config
            logger.info("Not in Databricks environment, trying explicit configuration")
            try:
                from databricks.sdk import WorkspaceClient
                host = os.getenv('DATABRICKS_HOST', 'https://e2-demo-field-eng.cloud.databricks.com')
                
                # Try OAuth first (best for local development)
                # This will use Databricks CLI config or prompt for OAuth login
                try:
                    self.workspace_client = WorkspaceClient(host=host)
                    logger.info("Successfully initialized WorkspaceClient with OAuth/CLI auth")
                except Exception as oauth_error:
                    logger.warning(f"OAuth/CLI auth failed: {oauth_error}")
                    
                    # Fall back to token auth if OAuth fails
                    token = os.getenv('DATABRICKS_TOKEN')
                    if token:
                        self.workspace_client = WorkspaceClient(host=host, token=token)
                        logger.info("Successfully initialized WorkspaceClient with token")
                    else:
                        logger.error("No authentication method available. Please either:")
                        logger.error("  1. Run 'databricks auth login --host https://e2-demo-field-eng.cloud.databricks.com'")
                        logger.error("  2. Set DATABRICKS_TOKEN environment variable")
                        self.workspace_client = None
            except Exception as e:
                logger.error(f"Failed to initialize WorkspaceClient: {e}")
        
        self.volume_path = "/Volumes/richa_sethi/nwag/uploaded_docs"
    
    def upload_file_to_volume(self, file_content, filename, volume_path=None):
        """Upload a file to the specified volume path."""
        if volume_path is None:
            volume_path = self.volume_path
        
        full_path = f"{volume_path}/{filename}"
        
        # Try dbutils first if available (for binary files)
        if self.use_dbutils and hasattr(self, 'dbutils'):
            try:
                logger.info(f"Uploading {filename} using dbutils")
                # For binary files, write to a temporary local path then copy to volume
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as tmp:
                    tmp.write(file_content if isinstance(file_content, bytes) else file_content.encode())
                    tmp_path = tmp.name
                
                # Copy to volume
                self.dbutils.fs.cp(f"file:{tmp_path}", full_path)
                
                # Clean up temp file
                import os as os_module
                os_module.remove(tmp_path)
                
                logger.info(f"Successfully uploaded {filename} to {full_path} using dbutils")
                return full_path
            except Exception as e:
                logger.error(f"Failed to upload with dbutils: {e}")
                # Fall through to try WorkspaceClient
        
        # Try WorkspaceClient with Files API
        if self.workspace_client is not None:
            try:
                logger.info(f"Uploading {filename} using WorkspaceClient.files.upload()")
                logger.info(f"Target path: {full_path}")
                logger.info(f"File size: {len(file_content) if file_content else 0} bytes")
                
                # Upload using Files API - file_path should be the full volume path
                self.workspace_client.files.upload(
                    file_path=full_path,
                    contents=file_content,
                    overwrite=True
                )
                
                logger.info(f"Successfully uploaded {filename} to {full_path} using WorkspaceClient")
                return full_path
            except Exception as e:
                logger.exception(f"Error uploading file with WorkspaceClient: {e}")
                # Log more details about the error
                logger.error(f"Full path attempted: {full_path}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Error message: {str(e)}")
                raise
        
        # Neither method available
        error_msg = (
            "Databricks connection not available. "
            "Please ensure: 1) The app is deployed to Databricks Apps, "
            "2) databricks-sdk>=0.35.0 is installed, "
            "3) The app service principal has proper permissions."
        )
        logger.error(f"No upload method available - cannot upload file. {error_msg}")
        raise Exception(error_msg)
    
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
