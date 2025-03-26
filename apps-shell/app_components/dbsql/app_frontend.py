import dash
from dash import callback, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app_components.dbsql.app_functions import (
    get_dbsql_status, 
    run_sql_query
)


def create_header():
    """Create a reusable header component."""
    return dbc.Row([
        # Left column with show code button
        dbc.Col(
            dbc.Button(
                [html.I(className="fab fa-github me-2"), "Show Code"],
                id="dbsql-show-code",
                color="secondary",
                outline=True,
                href="https://github.com",
                target="_blank",
                className="d-flex align-items-center border-2",
                style={
                    "minHeight": "38px",
                    "fontWeight": "500",
                    "borderColor": "var(--databricks-secondary)",
                    "color": "var(--databricks-secondary)",
                },
            ),
            width="auto",
            className="d-flex align-items-center",
        ),
        # Center column with title and subtitle
        dbc.Col([
            html.H3("DBSQL Example", className="text-center mb-2"),
            html.P(
                "Execute SQL queries against your Databricks SQL warehouse.",
                className="text-muted text-center mb-0",
            ),
        ], width=True),
        # Right column with status
        dbc.Col(
            dbc.ButtonGroup([
                dbc.Button(
                    dbc.Spinner(
                        html.Div(
                            id="dbsql-status",
                            children=[
                                html.I(
                                    className=(
                                        "fas fa-circle-notch fa-spin me-2"
                                    )
                                ),
                                html.Span("Checking status...")
                            ],
                        ),
                        size="sm",
                        delay_show=100,
                        show_initially=True,
                    ),
                    id="dbsql-status-button",
                    color="light",
                    className="d-flex align-items-center",
                    style={"minHeight": "38px"},
                ),
                dbc.Button(
                    html.I(className="fas fa-sync-alt"),
                    id="dbsql-check-status",
                    color="light",
                    className="border-start",
                    size="sm",
                ),
            ], className="w-100"),
            width="auto",
            className="d-flex align-items-center",
        ),
    ], className="mb-4")


# DBSQL layout
dbsql_layout = [
    html.Div([
        # Header section
        create_header(),
        
        # SQL query textarea
        dbc.Row([
            dbc.Col([
                dbc.Label("SQL Query"),
                dbc.Textarea(
                    id="dbsql-query",
                    placeholder=(
                        "SELECT * FROM samples.nyctaxi.trips LIMIT 10"
                    ),
                    rows=5,
                    style={"fontFamily": "monospace"},
                ),
                html.Small(
                    (
                        "Write your SQL query here "
                        "(results limited to 10 rows)"
                    ),
                    className="text-muted",
                ),
                # Run query button right-aligned
                dbc.Button(
                    [html.I(className="fas fa-play me-2"), "Run Query"],
                    id="dbsql-run-query",
                    color="success",
                    className="mt-2 float-end px-4",
                    size="lg",
                ),
            ])
        ], className="mb-4"),
        
        # Query results section
        dbc.Card([
            dbc.CardHeader([
                html.H5("Query Results", className="mb-0"),
            ]),
            dbc.CardBody([
                html.Div(id="dbsql-results-status", className="mb-3"),
                html.Div(id="dbsql-results-table"),
            ]),
        ], id="dbsql-results", style={"display": "none"}, className="mt-4"),
        
        # Debug information with collapse
        dbc.Card([
            dbc.CardHeader(
                dbc.Button(
                    "Debug Information",
                    id="dbsql-debug-collapse-button",
                    color="link",
                    className="text-decoration-none p-0",
                )
            ),
            dbc.Collapse(
                dbc.CardBody(
                    html.Pre(
                        id="dbsql-debug-info",
                        className="small text-muted mb-0"
                    )
                ),
                id="dbsql-debug-collapse",
                is_open=False,
            ),
        ], className="mt-4"),
    ])
]


# Callback to check DBSQL status on page load
@callback(
    [
        Output("dbsql-status", "children"),
        Output("dbsql-status-button", "color"),
        Output("dbsql-debug-info", "children"),
    ],
    [Input("dbsql-check-status", "n_clicks")],
    prevent_initial_call=False,  # Run on page load
)
def update_dbsql_status(n_clicks):
    """Update the status indicator for the Databricks SQL connection."""
    print("\n--- Checking DBSQL Connection Status ---")
    print(f"Event: {'Button click' if n_clicks else 'Page load'}")
    
    # Add a small delay to show loading state
    if n_clicks:
        import time
        time.sleep(0.5)
    
    try:
        # Get the status
        status = get_dbsql_status()
        print(f"Status response: {status}")
        
        # Format display based on status
        if status.get("status") == "running":
            status_display = [
                html.I(className="fas fa-check-circle me-2"),
                html.Span("Warehouse Running"),
            ]
            button_color = "success"
        elif status.get("status") == "starting":
            status_display = [
                html.I(className="fas fa-circle-notch fa-spin me-2"),
                html.Span("Warehouse Starting"),
            ]
            button_color = "warning"
        elif status.get("status") == "stopped":
            status_display = [
                html.I(className="fas fa-stop-circle me-2"),
                html.Span("Warehouse Stopped"),
            ]
            button_color = "danger"
        elif status.get("status") in ["not_configured", "config_error"]:
            status_display = [
                html.I(className="fas fa-exclamation-triangle me-2"),
                html.Span("Configuration Error"),
            ]
            button_color = "danger"
        else:
            status_display = [
                html.I(className="fas fa-question-circle me-2"),
                html.Span("Unknown Status"),
            ]
            button_color = "danger"
        
        # Create a detailed debug info string
        debug_info = (
            f"Status Object: {str(status)}\n\n"
            f"Connection check triggered by: "
            f"{n_clicks if n_clicks else 'page load'}"
        )
        
        return status_display, button_color, debug_info

    except Exception as e:
        import traceback
        traceback.print_exc()
        
        print(f"Error in update_dbsql_status: {str(e)}")
        error_display = [
            html.I(className="fas fa-exclamation-triangle me-2"),
            html.Span(str(e))
        ]
        return error_display, "danger", f"Exception: {str(e)}"


# Callback to run DBSQL query
@callback(
    [
        Output("dbsql-results", "style"),
        Output("dbsql-results-status", "children"),
        Output("dbsql-results-table", "children"),
    ],
    [Input("dbsql-run-query", "n_clicks")],
    [State("dbsql-query", "value")],
    prevent_initial_call=True,
)
def run_dbsql_query(n_clicks, query):
    """Run a SQL query and display the results."""
    print("\n--- Run SQL Query Callback ---")
    print(f"Button clicked: {n_clicks}")
    
    if not query:
        print("No query provided")
        return (
            {"display": "block"},
            [
                html.I(className="fas fa-exclamation-triangle text-warning me-2"),
                html.Span("Please enter a SQL query", className="text-warning"),
            ],
            [],
        )
    
    try:
        # Run the query
        print(f"Running query: {query}")
        result = run_sql_query(query)
        print(f"Query result status: {result.get('status')}")
        
        # Handle success case
        if result.get("status") == "success":
            # Check if we have results to display
            if result.get("results") and len(result.get("results")) > 0:
                print(f"Query returned {len(result.get('results'))} rows")
                
                # Get the columns from the first result
                columns = [
                    {"name": col, "id": col} 
                    for col in result["results"][0].keys()
                ]
                
                # Create a DataTable component
                table = dash_table.DataTable(
                    id="dbsql-data-table",
                    columns=columns,
                    data=result["results"],
                    style_table={
                        "overflowX": "auto",
                        "padding": "10px",
                    },
                    style_header={
                        "backgroundColor": "#0798EC",  # Databricks Blue
                        "fontWeight": "bold",
                        "color": "white",
                        "textAlign": "left",
                    },
                    style_cell={
                        "textAlign": "left",
                        "fontFamily": "Inter, sans-serif",
                        "padding": "10px",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#F9F7F4"  # Light background
                        }
                    ],
                    page_size=10
                )
                
                status_display = [
                    html.I(className="fas fa-check-circle text-success me-2"),
                    html.Span("Query executed successfully", className="text-success"),
                ]
                
                return {"display": "block"}, status_display, table
            else:
                # No results to display (e.g., INSERT, UPDATE statements)
                affected_rows = result.get("affected_rows", 0)
                status_display = [
                    html.I(className="fas fa-check-circle text-success me-2"),
                    html.Span(
                        f"Query executed successfully. Affected {affected_rows} rows.", 
                        className="text-success"
                    ),
                ]
                return {"display": "block"}, status_display, []
                
        # Handle error case
        else:
            error_message = result.get("message", "Unknown error occurred")
            print(f"Query error: {error_message}")
            status_display = [
                html.I(className="fas fa-exclamation-triangle text-danger me-2"),
                html.Span(error_message, className="text-danger"),
            ]
            return {"display": "block"}, status_display, []
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        print(f"Exception in run_dbsql_query: {str(e)}")
        status_display = [
            html.I(className="fas fa-exclamation-triangle text-danger me-2"),
            html.Span(f"Error: {str(e)}", className="text-danger"),
        ]
        return {"display": "block"}, status_display, []


# Add collapse callback
@callback(
    Output("dbsql-debug-collapse", "is_open"),
    [Input("dbsql-debug-collapse-button", "n_clicks")],
    [State("dbsql-debug-collapse", "is_open")],
)
def toggle_debug_collapse(n_clicks, is_open):
    """Toggle the debug information collapse."""
    if n_clicks:
        return not is_open
    return is_open 