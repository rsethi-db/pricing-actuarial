"""
UI components for the pricing cell automation app.
"""
import dash_bootstrap_components as dbc
from dash import html, dcc

def create_header():
    """Create the application header with 3-column layout and modern styling."""
    return html.Header([
        # Main header with 3-column layout
        html.Div([
            # Column 1: Logo and branding
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-shield-alt", style={"font-size": "1.8rem", "color": "#ffffff"})
                    ], className="logo-icon"),
                    html.Div([
                        html.Span("I", className="logo-letter"),
                        html.Span("T", className="logo-letter")
                    ], className="logo-letters")
                ], className="company-logo"),
                html.Div([
                    html.H2("InsurTech", className="company-name"),
                    html.P("Insurance Reinvented with AI", className="company-tagline"),
                    html.Div([
                        html.Span("Powered by", className="powered-by-text"),
                        html.Img(src="/assets/logo.png", className="powered-by-logo", alt="Databricks Logo")
                    ], className="powered-by-databricks")
                ], className="company-info")
            ], className="header-column header-logo", role="banner"),
            
            # Column 2: Title and subtitle
            html.Div([
                html.H1("Pricing Cell Generation", className="main-title"),
                html.P("AI-powered insurance pricing insights", className="main-subtitle")
            ], className="header-column header-title", role="main"),
            
                    # Column 3: User area
                    html.Div([
                        # Profile card
                        html.Div([
                            html.I(className="fas fa-user-circle profile-avatar", id="user-avatar"),
                            html.Div([
                                html.P("Loading...", className="profile-name", id="greeting-text")
                            ], className="profile-content")
                        ], className="profile-card", role="button", tabIndex="0", 
                           **{"aria-label": "User profile menu"})
                    ], className="header-column header-user", role="complementary")
        ], className="header-main")
    ], className="app-header")

def create_main_content():
    """Create the main content section with dashboard at top."""
    return html.Div([
        # Dashboard Section - Moved to Top
        html.Div([
            html.Div([
                html.H3("Interactive Pricing Dashboard", className="section-title"),
                html.P("Explore pricing analytics and insights from your extracted product features", className="dashboard-description")
            ], className="section-header"),
            
            # Embedded Databricks Dashboard
            html.Div([
                html.Div([
                    # Databricks Dashboard iframe
                    html.Iframe(
                        src="https://e2-demo-field-eng.cloud.databricks.com/embed/dashboardsv3/01f0956986c61040ac04a2287fd5a23f",
                        width="100%",
                        height="600px",
                        style={"border": "none", "borderRadius": "8px", "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"},
                        id="databricks-dashboard"
                    )
                ], id="dashboard-iframe-container"),
                
                # Dashboard Controls
                html.Div([
                    html.Button(
                        [html.I(className="fas fa-refresh me-2"), "Refresh Dashboard"],
                        id="refresh-dashboard",
                        className="dashboard-btn"
                    ),
                    html.A(
                        [html.I(className="fas fa-external-link-alt me-2"), "Open in New Tab"],
                        href="https://e2-demo-field-eng.cloud.databricks.com/dashboardsv3/01f0956986c61040ac04a2287fd5a23f/published?o=1444828305810485",
                        target="_blank",
                        className="dashboard-btn",
                        style={"text-decoration": "none", "display": "inline-block"}
                    )
                ], className="dashboard-controls", style={"margin-top": "15px"})
            ], className="dashboard-container")
        ], className="dashboard-section", id="dashboard-section"),
        
        # Three-Column Layout: Upload (Left), Features (Middle), Scenarios (Right)
        html.Div([
            # Left Column - Upload & Document Management
            html.Div([
                html.Div([
                    html.H3("Upload Documents", className="section-title")
                ], className="section-header"),
                
                html.Div([
                    html.H4("📄 Upload PDF Files", className="upload-title"),
                    html.P("Upload PDF brochures to extract reference product specifications", className="upload-description"),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div([
                            html.Div([
                                html.Span("📄", style={"font-size": "3rem", "margin-right": "10px"}),
                                html.Span("⬆️", style={"font-size": "3rem"})
                            ], className="mb-3"),
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
                    html.H4("Uploaded File(s)", className="pdf-management-title"),
                    html.Div(id="uploaded-pdfs-list", className="pdf-list"),
                    html.Div(id="pdf-management-status", className="pdf-status")
                ], className="pdf-management-section", id="pdf-management", style={"display": "none"})
            ], className="three-col-left", id="upload-section"),
            
            # Middle Column - Extracted Features/Specifications
            html.Div([
                html.Div([
                    html.H3("Extract Features", className="section-title")
                ], className="section-header"),
                
                # Extract Features Button
                html.Div([
                    html.Div([
                        html.Button(
                            [html.I(className="fas fa-play me-2"), "Extract Features"],
                            id="parse_ai_btn",
                            className="process-btn"
                        ),
                        html.Div(id="workflow_status", className="status-message")
                    ], className="extract-features-section")
                ], className="extract-section"),
                
                # Reference Product Specs Section
                html.Div([
                    html.H4("From reference product specs", className="subsection-title"),
                    html.Div([
                        html.Div([
                            html.Span("Surrender Charge Period: ", className="feature-label"),
                            html.Div([
                                html.I(className="fas fa-file-upload", style={"color": "#6c757d", "margin-right": "8px", "font-size": "16px"}),
                                html.Span("Upload docs", id="surrender-charge-period", className="feature-value placeholder-text")
                            ], className="placeholder-content")
                        ], className="feature-item no-data placeholder-item"),
                        html.Div([
                            html.Span("Initial Guarantee Period: ", className="feature-label"),
                            html.Div([
                                html.I(className="fas fa-file-upload", style={"color": "#6c757d", "margin-right": "8px", "font-size": "16px"}),
                                html.Span("Upload docs", id="initial-guarantee-period", className="feature-value placeholder-text")
                            ], className="placeholder-content")
                        ], className="feature-item no-data placeholder-item"),
                        html.Div([
                            html.Span("Guaranteed Minimum Interest Rate: ", className="feature-label"),
                            html.Div([
                                html.I(className="fas fa-file-upload", style={"color": "#6c757d", "margin-right": "8px", "font-size": "16px"}),
                                html.Span("Upload docs", id="guaranteed-minimum-interest-rate", className="feature-value placeholder-text")
                            ], className="placeholder-content")
                        ], className="feature-item no-data placeholder-item")
                    ], className="reference-features")
                ], className="reference-section")
            ], className="three-col-middle", id="processing-section"),
            
            # Right Column - Scenario Adjustments & Quick Insights
            html.Div([
                html.Div([
                    html.H3("Scenario Adjustment", className="section-title")
                ], className="section-header"),
                
                # Scenarios Container (initially empty)
                html.Div([
                    # Empty state illustration
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-cogs fa-3x", style={"color": "#6c757d", "margin-bottom": "15px"}),
                            html.H5("No Scenarios Yet", style={"color": "#6c757d", "margin-bottom": "10px"}),
                            html.P("Create your first scenario to start adjusting product features", style={"color": "#6c757d", "font-size": "14px", "margin-bottom": "20px"})
                        ], className="text-center empty-state")
                    ], className="mb-4", id="empty-scenarios-state"),
                    
                    # Add New Scenario button (always visible)
                    html.Div([
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-plus me-2"),
                                "Add New Scenario"
                            ], id="add-scenario-btn", className="add-scenario-btn")
                        ], className="text-center")
                    ], className="mb-4")
                ], id="scenarios-container", className="scenarios-container")
            ], className="three-col-right", id="adjust-features-section", style={"display": "block"})
        ], className="three-column-layout")
    ], className="main-content")



def create_footer():
    """Create the application footer."""
    return html.Div([
        html.P("© 2025 Pricing Cell Generation - Powered by Databricks", 
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
                    html.P("Please wait while we process your files", className="text-center text-muted")
                ], width=12)
            ])
        ])
    ], id="loading_modal", is_open=False, backdrop="static", keyboard=False)

def create_chatbot():
    """Create the AI chatbot component."""
    return html.Div([
        # Chatbot Toggle Button
        dbc.Button(
            [html.I(className="fas fa-robot me-2"), "AI Assistant"],
            id="chatbot-toggle",
            color="primary",
            className="chatbot-toggle-btn"
        ),
        
        # Chatbot Modal
        dbc.Modal([
            dbc.ModalHeader([
                html.Div([
                    html.I(className="fas fa-robot me-2", style={"color": "#007bff"}),
                    html.H5("AI Pricing Assistant", className="mb-0"),
                    html.Small("Powered by Claude", className="text-muted ms-2")
                ], className="d-flex align-items-center")
            ]),
            dbc.ModalBody([
                # Chat Messages Container
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-robot me-2", style={"color": "#007bff"}),
                            html.Span("Hello! I'm your AI pricing assistant. I can help you with:")
                        ], className="d-flex align-items-start mb-2"),
                        html.Ul([
                            html.Li("Analyzing product features and pricing data"),
                            html.Li("Explaining actuarial concepts and methodologies"),
                            html.Li("Providing insights on pricing strategies"),
                            html.Li("Answering questions about your uploaded data"),
                            html.Li("Helping with insurance product analysis")
                        ], className="mb-0 small text-muted")
                    ], className="chat-message assistant-message")
                ], id="chat-messages", style={"maxHeight": "400px", "overflowY": "auto", "padding": "10px"}),
                
                # Chat Input
                html.Div([
                    dbc.InputGroup([
                        dbc.Input(
                            id="chat-input",
                            placeholder="Ask me anything about pricing, actuarial analysis, or your data...",
                            type="text",
                            style={"borderRadius": "20px 0 0 20px"}
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-paper-plane")],
                            id="chat-send",
                            color="primary",
                            style={"borderRadius": "0 20px 20px 0"}
                        )
                    ], className="chat-input-group")
                ], className="mt-3")
            ]),
            dbc.ModalFooter([
                html.Small("AI responses are for informational purposes only. Always verify with your actuarial team.", 
                          className="text-muted")
            ])
        ], id="chatbot-modal", is_open=False, size="lg", style={"zIndex": "1050"})
    ])
