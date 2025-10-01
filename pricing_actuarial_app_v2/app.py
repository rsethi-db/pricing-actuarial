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
    logger.info("Starting Product Features Dashboard...")
    dash_app.run(debug=True, port=8050, host='0.0.0.0')
