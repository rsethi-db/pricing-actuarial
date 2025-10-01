#!/usr/bin/env python3
"""
Databricks deployment script for the Pricing Cell Generation app.
This script handles the deployment process within Databricks environment.
"""

import os
import sys
import logging
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ImportFormat

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deploy_to_databricks():
    """Deploy the app to Databricks workspace."""
    try:
        # Initialize Databricks client
        workspace_client = WorkspaceClient()
        
        # Get workspace info
        workspace_info = workspace_client.config
        logger.info(f"Connected to Databricks workspace: {workspace_info.host}")
        
        # Create app directory in workspace
        app_path = "/Workspace/Users/{}/pricing_actuarial_app".format(
            os.environ.get('USER', 'unknown')
        )
        
        # Upload app files
        files_to_upload = [
            'app.py',
            'callbacks.py', 
            'ui_components.py',
            'config.py',
            'database.py',
            'file_upload.py',
            'claude_integration.py',
            'requirements.txt',
            'app.yaml',
            'static/styles.css',
            'static/logo.png'
        ]
        
        for file_path in files_to_upload:
            if os.path.exists(file_path):
                workspace_path = f"{app_path}/{file_path}"
                logger.info(f"Uploading {file_path} to {workspace_path}")
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                workspace_client.workspace.upload(
                    workspace_path,
                    content,
                    format=ImportFormat.AUTO,
                    overwrite=True
                )
        
        logger.info("✅ App successfully deployed to Databricks workspace!")
        logger.info(f"📁 App location: {app_path}")
        logger.info("🚀 You can now run the app from within Databricks")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = deploy_to_databricks()
    sys.exit(0 if success else 1)
