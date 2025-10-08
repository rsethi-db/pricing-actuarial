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
            # Column 1: Logo and Company Info
            html.Div([
                html.Div([
                    html.Img(src="/assets/nw_logo.png", className="nationwide-logo", alt="Nationwide Insurance Logo",
                             style={
                                 "maxHeight": "100px",
                                 "width": "auto",
                                 "objectFit": "contain",
                                 "backgroundColor": "white",
                                 "padding": "8px 15px",
                                 "borderRadius": "8px",
                                 "display": "block",
                                 "marginBottom": "12px"
                             })
                ], style={"marginBottom": "10px"}),
                html.Div([
                    html.Span("Powered by", className="powered-by-text", style={"marginRight": "8px"}),
                    html.Img(src="/assets/logo.png", className="powered-by-logo", alt="Databricks Logo")
                ], style={
                    "display": "flex",
                    "alignItems": "center",
                    "flexDirection": "row"
                })
            ], className="header-column header-logo", role="banner", 
               style={
                   "display": "flex",
                   "flexDirection": "column",
                   "alignItems": "flex-start",
                   "justifyContent": "center",
                   "paddingLeft": "20px"
               }),
            
            # Column 2: Title and subtitle
            html.Div([
                html.H1("NWAG Rosie", className="main-title"),
                html.P("AI-powered Underwriter Workbench", className="main-subtitle")
            ], className="header-column header-title", role="main"),
            
                    # Column 3: User area
                    html.Div([
                        # Profile card
                        html.Div([
                            html.I(className="fas fa-user-circle profile-avatar", id="user-avatar"),
                            html.Div([
                                html.P(id="greeting-text", className="profile-name", children="Hello!")
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
                html.H3("Explore your Portfolio KPIs", className="section-title")
            ], className="section-header"),
            
            # Embedded Databricks Dashboard
            html.Div([
                html.Div([
                    # Databricks Dashboard iframe
                    html.Iframe(
                        src="https://e2-demo-field-eng.cloud.databricks.com/embed/dashboardsv3/01f0a3e0dca7189989989ed60b77666a",
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
                        href="https://e2-demo-field-eng.cloud.databricks.com/dashboardsv3/01f0a3e0dca7189989989ed60b77666a/published?o=1444828305810485",
                        target="_blank",
                        className="dashboard-btn",
                        style={"text-decoration": "none", "display": "inline-block"}
                    )
                ], className="dashboard-controls")
            ], className="dashboard-container")
        ], className="dashboard-section", id="dashboard-section"),
        
        # Genie Space Section - Chat with your data
        html.Div([
            html.Div([
                html.H3("Chat with your data", className="section-title")
            ], className="section-header"),
            
            # Embedded Genie Chat Interface
            html.Div([
                html.Div([
                    # Chat messages container
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-robot me-2", style={"color": "#667eea"}),
                                html.Span("Ask me anything about your insurance portfolio data!", style={"color": "#666"})
                            ], style={"textAlign": "center", "padding": "20px", "color": "#999"})
                        ], id="genie-messages", className="genie-messages-container")
                    ], id="genie-messages-scroll-container", style={
                        "height": "400px",
                        "overflowY": "auto",
                        "padding": "15px",
                        "background": "#f8f9fa",
                        "borderRadius": "8px 8px 0 0",
                        "border": "1px solid #e0e0e0",
                        "borderBottom": "none",
                        "scrollBehavior": "smooth"
                    }),
                    
                    # Chat input area
                    html.Div([
                        dcc.Input(
                            id="genie-input",
                            type="text",
                            placeholder="Ask a question about your data... (e.g., 'What are the top 5 products by premium?')",
                            style={
                                "width": "100%",
                                "padding": "12px 15px",
                                "border": "1px solid #e0e0e0",
                                "borderRadius": "0 0 0 8px",
                                "fontSize": "14px",
                                "outline": "none"
                            },
                            n_submit=0
                        ),
                        html.Button(
                            [html.I(className="fas fa-paper-plane me-2"), "Send"],
                            id="genie-send-btn",
                            type="button",
                            style={
                                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                "color": "white",
                                "border": "none",
                                "padding": "12px 20px",
                                "borderRadius": "0 0 8px 0",
                                "cursor": "pointer",
                                "fontSize": "14px",
                                "transition": "all 0.3s ease",
                                "fontWeight": "500"
                            },
                            className="genie-send-button"
                        )
                    ], style={"display": "flex", "borderTop": "none"}),
                    
                    # Hidden storage for conversation ID
                    dcc.Store(id="genie-conversation-id", data=None),
                    
                    # Pending message indicator
                    html.Div(id="genie-pending-message", style={"display": "none"}),
                    
                    # Auto-scroll script
                    html.Script('''
                        document.addEventListener('DOMContentLoaded', function() {
                            const observer = new MutationObserver(function() {
                                const container = document.getElementById('genie-messages-scroll-container');
                                if (container) {
                                    container.scrollTop = container.scrollHeight;
                                }
                            });
                            
                            const config = { childList: true, subtree: true };
                            const target = document.getElementById('genie-messages');
                            if (target) {
                                observer.observe(target, config);
                            }
                        });
                    '''),
                    
                    # External link
                    html.Div([
                        html.A(
                            [html.I(className="fas fa-external-link-alt me-2"), "Open in Genie Space"],
                            href="https://e2-demo-field-eng.cloud.databricks.com/genie/rooms/01f0a3bc10ba1357bde100a5f8527509?o=1444828305810485",
                            target="_blank",
                            className="btn btn-sm",
                            style={
                                "textDecoration": "none",
                                "color": "#667eea",
                                "fontSize": "14px",
                                "marginTop": "10px",
                                "display": "inline-block"
                            }
                        )
                    ], style={"textAlign": "center", "marginTop": "10px"})
                    
                ], style={"padding": "0 15px"})
            ], className="dashboard-container")
        ], className="genie-section", id="genie-section"),
        
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
                ], className="pdf-management-section", id="pdf-management", style={"display": "none"}),
                
                # Document Summarization Section
                html.Div([
                    html.H4("📋 Document Summarization", className="upload-title", style={"marginTop": "30px", "marginBottom": "15px"}),
                    
                    # Summarize Button
                    html.Div([
                        html.Button(
                            [html.I(className="fas fa-magic me-2"), "Summarize Document"],
                            id="summarize-btn",
                            className="process-btn",
                            style={
                                "width": "100%",
                                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                "color": "white",
                                "border": "none",
                                "padding": "12px 20px",
                                "borderRadius": "8px",
                                "fontSize": "16px",
                                "fontWeight": "600",
                                "cursor": "pointer",
                                "transition": "all 0.3s ease",
                                "boxShadow": "0 4px 6px rgba(102, 126, 234, 0.3)"
                            }
                        )
                    ], style={"marginBottom": "15px"}),
                    
                    # Summary Content (initially hidden)
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-file-alt", style={"fontSize": "48px", "color": "#667eea", "marginBottom": "15px"}),
                            html.P("Document Summary", style={"fontWeight": "600", "color": "#333", "marginBottom": "10px", "fontSize": "16px"}),
                        ], style={"textAlign": "center", "marginBottom": "15px"}),
                        html.Div([
                            html.P([
                                "This document presents a sample farm risk assessment form from the ",
                                html.Strong("Canada FarmSafe Plan"),
                                ", demonstrating the recommended five-column format for health and safety inspection checklists that includes equipment identification, hazard description, priority rating, accountability assignments, and correction deadlines."
                            ], style={"marginBottom": "12px", "lineHeight": "1.6", "textAlign": "justify"}),
                            html.P([
                                "The example assessment, conducted by Tom and Jerry on April 26, 2011, identifies four safety issues ranging from high-priority concerns like a missing PTO shield on a yard tractor and forklift operator certification problems, to moderate and low-priority items such as depleted respirator inventory and upcoming fire extinguisher recertification requirements."
                            ], style={"marginBottom": "12px", "lineHeight": "1.6", "textAlign": "justify"}),
                            html.P([
                                "Each identified hazard includes specific corrective actions, priority classifications, assigned responsible parties, and target completion dates, illustrating how farms can systematically document, prioritize, and track the resolution of safety concerns to maintain a safer working environment."
                            ], style={"marginBottom": "0", "lineHeight": "1.6", "textAlign": "justify"})
                        ], style={"fontSize": "14px", "color": "#555"})
                    ], id="document-summary-content", style={
                        "padding": "20px",
                        "background": "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)",
                        "borderRadius": "10px",
                        "border": "1px solid rgba(102, 126, 234, 0.2)",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
                        "display": "none"
                    })
                ], className="document-summary-section", style={"marginTop": "20px"})
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
                    html.H4("From uploaded doc", className="subsection-title"),
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
        html.P("© 2025 NWAG Rosie - Powered by Databricks", 
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
