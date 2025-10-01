"""
Main application file for the Product Features Dashboard.
A modularized Dash application for AI-powered insurance product analysis.
"""
import sys
import os
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash import Dash, dcc
import dash_bootstrap_components as dbc

# Import our modular components
from ui_components import (
    create_header, create_main_content, create_footer, create_loading_modal, create_chatbot
)
from callbacks import register_callbacks

# ==============================
# Logging
# ==============================
logger = logging.getLogger(__name__)

# ==============================
# Dash App
# ==============================
dash_app = Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    assets_folder='static'
)
server = dash_app.server

# Create the main layout
dash_app.layout = dbc.Container([
    create_header(),
    create_main_content(),
    create_loading_modal(),
    create_chatbot(),
    create_footer()
], fluid=True, className="p-0")

# Register all callbacks
register_callbacks(dash_app)

# ==============================
# Run app
# ==============================
if __name__ == "__main__":
    # Check if running in Databricks environment
    is_databricks = os.environ.get('DATABRICKS_RUNTIME_VERSION') is not None
    
    if is_databricks:
        # Production settings for Databricks
        debug_mode = False
        port = int(os.environ.get('PORT', 8050))
        host = '0.0.0.0'
        logger.info("Starting Product Features Dashboard in Databricks environment...")
        logger.info(f"App will be available at the URL provided by Databricks on port {port}")
    else:
        # Development settings
        debug_mode = True
        port = 8050
        host = '0.0.0.0'
        logger.info("Starting Product Features Dashboard in development mode...")
        logger.info(f"App available at: http://{host}:{port}")
    
    dash_app.run(debug=debug_mode, port=port, host=host)
