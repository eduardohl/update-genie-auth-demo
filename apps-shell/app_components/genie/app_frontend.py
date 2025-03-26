from dash import callback, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app_components.genie.app_functions import (
    get_genie_status, 
    ask_genie_question
)

# Genie layout
genie_layout = [
    html.Div([
        html.H3("AI/BI Genie", className="mb-3"),
        
        html.P(
            "Ask questions about your data using natural language and get "
            "AI-powered answers.",
            className="text-muted mb-4",
        ),
        
        # Status display
        dbc.Card([
            dbc.CardHeader("Connection Status"),
            dbc.CardBody([
                html.Div(
                    id="genie-status",
                    children=[
                        html.I(className="fas fa-circle-notch fa-spin me-2"),
                        html.Span("Checking connection status...")
                    ],
                ),
            ]),
        ], className="mb-4"),
        
        # Question input
        dbc.Row([
            dbc.Col([
                dbc.Label("Ask a Question"),
                dbc.Input(
                    id="genie-question",
                    placeholder="What was the total revenue last quarter?",
                    type="text",
                ),
                html.Small(
                    "Ask a question in natural language about your data",
                    className="text-muted",
                ),
            ])
        ], className="mb-3"),
        
        # Submit button
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fas fa-paper-plane me-2"),
                        "Ask Genie"
                    ],
                    id="genie-ask-button",
                    color="primary",
                    className="mt-2"
                ),
                # Hidden div to trigger status check
                html.Div(id="genie-check-status", style={"display": "none"})
            ])
        ], className="mb-4"),
        
        # Results area
        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.Div(
                        id="genie-results-status",
                        children=[
                            html.I(
                                className="fas fa-info-circle me-2 text-muted"
                            ),
                            html.Span("Ask a question to see results")
                        ],
                    ),
                ]),
                dbc.CardBody([
                    # Placeholder for Genie response
                    html.Div(id="genie-results-content")
                ]),
            ]),
        ], id="genie-results", style={"display": "none"}),
        
        # Debug info card (hidden by default)
        dbc.Card([
            dbc.CardHeader("Debug Information"),
            dbc.CardBody([
                html.Pre(
                    id="genie-debug-info",
                    className="border p-3 bg-light",
                    style={"maxHeight": "300px", "overflow": "auto"}
                )
            ])
        ], id="genie-debug-card", className="mt-4", style={"display": "none"}),
    ])
]

# Callbacks for Genie component
@callback(
    [
        Output("genie-status", "children"),
        Output("genie-debug-card", "style"),
        Output("genie-debug-info", "children"),
    ],
    [Input("genie-check-status", "children")],
    prevent_initial_call=False,  # Run on page load
)
def update_genie_status(trigger):
    """Update the Genie connection status."""
    status = get_genie_status()
    
    debug_info = f"""
Configuration Status:
--------------------
Is Configured: {status['is_configured']}
Status: {status['status']}
Details: {', '.join(status['details'])}

Debug Info:
----------
{str(status['debug_info'])}
"""
    
    if status["is_configured"] and status["status"] == "available":
        status_ui = [
            html.I(className="fas fa-check-circle text-success me-2"),
            html.Span("Genie is configured and available")
        ]
        debug_style = {"display": "none"}
    else:
        status_ui = [
            html.I(className="fas fa-times-circle text-danger me-2"),
            html.Span(
                f"Genie is not available: {', '.join(status['details'])}"
            )
        ]
        debug_style = {"display": "block"}
    
    return status_ui, debug_style, debug_info


@callback(
    [
        Output("genie-results", "style"),
        Output("genie-results-status", "children"),
        Output("genie-results-content", "children"),
    ],
    [Input("genie-ask-button", "n_clicks")],
    [State("genie-question", "value")],
    prevent_initial_call=True,
)
def ask_genie(n_clicks, question):
    """Submit a question to Genie and display the response."""
    if not question:
        return {"display": "none"}, [
            html.I(className="fas fa-info-circle me-2 text-muted"),
            html.Span("Please enter a question")
        ], []
    
    # Check if Genie is properly configured
    status = get_genie_status()
    if not status["is_configured"] or status["status"] != "available":
        return {"display": "block"}, [
            html.I(className="fas fa-exclamation-circle me-2 text-danger"),
            html.Span("Genie is not properly configured")
        ], [
            html.P("Please check the configuration and connection status.")
        ]
    
    # Ask Genie
    result = ask_genie_question(question)
    
    if not result.get("success"):
        return {"display": "block"}, [
            html.I(className="fas fa-exclamation-circle me-2 text-danger"),
            html.Span("Error querying Genie")
        ], [
            html.P(f"Error: {result.get('error', 'Unknown error')}")
        ]
    
    # Process successful response
    return {"display": "block"}, [
        html.I(className="fas fa-check-circle me-2 text-success"),
        html.Span("Genie Response")
    ], [
        html.Div([
            html.H5("Your Question:"),
            html.P(question, className="border-bottom pb-3"),
            
            html.H5("Genie's Answer:", className="mt-4"),
            # Display the response from Genie
            html.Pre(
                str(result.get("response", {})), 
                className="border p-3 bg-light",
                style={"maxHeight": "400px", "overflow": "auto"}
            )
        ])
    ] 