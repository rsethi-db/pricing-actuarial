"""
UI components for the pricing cell automation app.
"""
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def create_header():
    """Create the application header."""
    return html.Div([
        # Main header
        html.Div([
            html.H1("Pricing Cell Generation", className="main-title"),
            html.Div([
                html.P("Welcome to the Pricing Cell Generation Platform. This application provides a streamlined process for generating pricing cells for life insurance policies using AI-powered document analysis.", 
                       className="welcome-text")
            ], className="welcome-banner")
        ], className="header-section"),
        
        # Step navigation
        html.Div([
            html.Div([
                html.Div("1", className="step-number"),
                html.Span("Reference Product Specs", className="step-label")
            ], className="step-item pending", id="step-nav-1"),
            
            html.Div([
                html.Div("2", className="step-number"),
                html.Span("Product Feature Specification", className="step-label")
            ], className="step-item pending", id="step-nav-2"),
            
            html.Div([
                html.Div("3", className="step-number"),
                html.Span("New Business Inforce Generation", className="step-label")
            ], className="step-item pending", id="step-nav-3"),
            
            html.Div([
                html.Div("4", className="step-number"),
                html.Span("Pricing Cell Generation", className="step-label")
            ], className="step-item pending", id="step-nav-4")
        ], className="step-navigation")
    ], className="app-header")

def create_step1_section():
    """Create Step 1: Reference Product Specs (Upload) section."""
    return html.Div([
        html.Div([
            html.Div([
                html.H3("Step 1: Reference Product Specs", className="section-title")
            ], className="section-header"),
            
            # Upload Section
            html.Div([
                html.H4("Upload Product Brochures", className="upload-title"),
                html.P("Upload PDF brochures to extract reference product specifications", className="upload-description"),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div([
                        html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                        html.P("Drag and Drop or Click to Select PDF Files", className="mb-2"),
                        html.P("Supports PDF files", className="text-muted small")
                    ], className="text-center"),
                    style={
                        "width": "100%", 
                        "height": "150px", 
                        "lineHeight": "150px",
                        "borderWidth": "2px", 
                        "borderStyle": "dashed", 
                        "borderRadius": "10px",
                        "textAlign": "center", 
                        "margin": "20px 0",
                        "cursor": "pointer",
                        "transition": "all 0.3s ease",
                        "backgroundColor": "#f8f9fa",
                        "borderColor": "#6c757d"
                    },
                    className="upload-area",
                    multiple=True
                ),
                html.Div(id="upload-feedback", className="mt-3")
            ], className="upload-section"),
            
            # Uploaded PDFs Management
            html.Div([
                html.H4("Uploaded PDF Files", className="pdf-management-title"),
                html.Div(id="uploaded-pdfs-list", className="pdf-list"),
                html.Div(id="pdf-management-status", className="pdf-status")
            ], className="pdf-management-section", id="pdf-management", style={"display": "none"})
        ], className="main-content")
    ], className="step1-section", id="step1")

def create_step2_section():
    """Create Step 2: Product Feature Specification section."""
    return html.Div([
        html.Div([
            html.Div([
                html.H3("Step 2: Product Feature Specification", className="section-title")
            ], className="section-header"),
            
            # Reference Product Specs Section
            html.Div([
                html.H4("From reference product specs", className="subsection-title"),
                html.Div([
                    html.Div([
                        html.Span("Minimum Guaranteed Rate: ", className="feature-label"),
                        html.Span("Varies between 2% to 3.5%", className="feature-value")
                    ], className="feature-item"),
                    html.Div([
                        html.Span("Surrender Charge Period: ", className="feature-label"),
                        html.Span("Varies between 3 to 7 years, 5 years is the most common", className="feature-value")
                    ], className="feature-item"),
                    html.Div([
                        html.Span("Surrender Charge: ", className="feature-label"),
                        html.Span("Usually decreasing year over year, ranges between 10% to 0%", className="feature-value")
                    ], className="feature-item")
                ], className="reference-features")
            ], className="reference-section"),
            
            # Adjust Product Features Section
            html.Div([
                html.Div([
                    html.I(className="fas fa-cog me-2"),
                    html.H4("Adjust Product Features", className="subsection-title")
                ], className="adjust-header"),
                
                html.Div([
                    # Minimum Guaranteed Rate
                    html.Div([
                        html.Label("Minimum Guaranteed Rate (%)", className="form-label"),
                        html.Div([
                            dcc.Input(
                                type="number",
                                value="3.5",
                                min="0",
                                max="10",
                                step="0.1",
                                className="form-input",
                                id="min-guaranteed-rate"
                            ),
                            html.Div([
                                html.Button("▲", className="input-btn up"),
                                html.Button("▼", className="input-btn down")
                            ], className="input-buttons")
                        ], className="input-group"),
                        html.Small("Enter minimum guaranteed rate (0-10%)", className="form-hint")
                    ], className="form-field"),
                    
                    # Surrender Charge Period
                    html.Div([
                        html.Label("Surrender Charge Period (years)", className="form-label"),
                        html.Div([
                            dcc.Input(
                                type="number",
                                value="7",
                                min="1",
                                max="20",
                                step="1",
                                className="form-input",
                                id="surrender-period"
                            ),
                            html.Div([
                                html.Button("▲", className="input-btn up"),
                                html.Button("▼", className="input-btn down")
                            ], className="input-buttons")
                        ], className="input-group"),
                        html.Small("Enter surrender charge period in years", className="form-hint")
                    ], className="form-field"),
                    
                    # Surrender Charge
                    html.Div([
                        html.Label("Surrender Charge (%)", className="form-label"),
                        html.Div([
                            dcc.Input(
                                type="number",
                                value="8",
                                min="0",
                                max="20",
                                step="0.5",
                                className="form-input",
                                id="surrender-charge"
                            ),
                            html.Div([
                                html.Button("▲", className="input-btn up"),
                                html.Button("▼", className="input-btn down")
                            ], className="input-buttons")
                        ], className="input-group"),
                        html.Small("Enter surrender charge percentage", className="form-hint")
                    ], className="form-field"),
                    
                    # Add Scenario Button
                    html.Button(
                        [html.I(className="fas fa-plus me-2"), "Add New Scenario"],
                        className="add-scenario-btn"
                    )
                ], className="adjust-features")
            ], className="adjust-section"),
            
            # Scenario Display
            html.Div([
                html.Div([
                    html.H4("Scenario 1", className="scenario-title"),
                    html.Button("×", className="remove-btn")
                ], className="scenario-header"),
                html.Div([
                    html.Div([
                        html.Span("Minimum Guaranteed Rate: ", className="scenario-label"),
                        html.Span("3.5%", className="scenario-value")
                    ], className="scenario-feature"),
                    html.Div([
                        html.Span("Surrender Charge Period: ", className="scenario-label"),
                        html.Span("7 years", className="scenario-value")
                    ], className="scenario-feature"),
                    html.Div([
                        html.Span("Surrender Charge: ", className="scenario-label"),
                        html.Span("8%", className="scenario-value")
                    ], className="scenario-feature")
                ], className="scenario-content")
            ], className="scenario-section")
        ], className="main-content")
    ], className="step2-section", id="step2", style={"display": "none"})

def create_control_section():
    """Create the control section with step navigation and AI processing."""
    return html.Div([
        # Step 1 Controls (Upload)
        html.Div([
            html.Button(
                [html.I(className="fas fa-arrow-right me-2"), "Continue to Step 2"],
                id="continue-to-step2",
                className="continue-btn",
                disabled=True
            ),
            html.Div(id="step1-status", className="status-message")
        ], className="step1-controls", id="step1-controls"),
        
        # Step 2 Controls (AI Processing)
        html.Div([
            html.Button(
                [html.I(className="fas fa-arrow-left me-2"), "Back to Step 1"],
                id="back-to-step1",
                className="back-btn"
            ),
            html.Button(
                [html.I(className="fas fa-play me-2"), "Parse & Run AI Batch"],
                id="parse-ai-btn",
                className="process-btn"
            ),
            html.Button(
                [html.I(className="fas fa-download me-2"), "Export Results"],
                id="export-btn",
                className="export-btn",
                disabled=True
            ),
            html.Div(id="workflow-status", className="status-message")
        ], className="step2-controls", id="step2-controls", style={"display": "none"})
    ], className="control-section")

def create_results_section():
    """Create the results display section."""
    return html.Div([
        html.Div([
            html.H4("Analysis Results", className="results-title"),
            html.P("Extracted product features and pricing information", className="results-subtitle")
        ], className="results-header"),
        
        html.Div([
            dash_table.DataTable(
                id="workflow-results",
                columns=[
                    {"name": "Input File", "id": "input", "type": "text"},
                    {"name": "Issuing Company", "id": "issuing_company", "type": "text"},
                    {"name": "Min Premium", "id": "min_premium", "type": "text"},
                    {"name": "Withdrawal Options", "id": "withdrawal_options", "type": "text"},
                    {"name": "Interest Crediting", "id": "interest_crediting", "type": "text"},
                    {"name": "Surrender Charge", "id": "surrender_charge_schedule", "type": "text"},
                    {"name": "Death Benefit", "id": "death_benefit", "type": "text"},
                    {"name": "Available Riders", "id": "available_riders", "type": "text"},
                    {"name": "Issue Ages", "id": "issue_ages", "type": "text"},
                    {"name": "Guarantee Period", "id": "guarantee_period", "type": "text"},
                ],
                page_size=10,
                style_table={
                    'overflowX': 'auto',
                    'border': '1px solid #e0e0e0',
                    'borderRadius': '8px',
                    'backgroundColor': '#ffffff'
                },
                style_header={
                    'backgroundColor': '#f5f5f5',
                    'fontWeight': 'bold',
                    'border': '1px solid #e0e0e0',
                    'color': '#333333'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '14px',
                    'color': '#333333'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#fafafa'
                    }
                ],
                sort_action="native",
                filter_action="native",
                export_format="csv"
            )
        ], className="results-content")
    ], id="results-section", className="results-section", style={"display": "none"})

def create_footer():
    """Create the application footer."""
    return html.Div([
        html.P("© 2024 Pricing Cell Generation - Powered by Databricks AI", 
               className="footer-text")
    ], className="app-footer")

def create_loading_modal():
    """Create a loading modal for long operations."""
    return dbc.Modal([
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Spinner(size="lg"),
                    html.H4("Processing...", className="text-center mt-3"),
                    html.P("Please wait while we process your files", className="text-center text-muted"),
                    html.Div([
                        dbc.Progress(
                            id="progress-bar",
                            value=0,
                            max=100,
                            color="success",
                            className="mb-3",
                            style={"height": "20px"}
                        ),
                        html.Div(id="progress-text", className="text-center text-muted")
                    ], className="mt-4")
                ], width=12)
            ])
        ])
    ], id="loading-modal", is_open=False, backdrop="static", keyboard=False)
