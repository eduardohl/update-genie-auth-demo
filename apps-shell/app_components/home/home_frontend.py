"""Homepage layout and components."""
import dash_bootstrap_components as dbc
from dash import html

# Define Databricks official color scheme
DATABRICKS_COLORS = {
    "primary": "#FF3621",    # Orange 600 - Primary
    "secondary": "#2272B4",  # Blue 600 - Secondary
    "accent": "#FFAB00",     # Yellow 600 - Secondary
    "light": "#F9F7F4",      # Oat Light - Primary
    "dark": "#1B3139",       # Navy 800 - Primary
    "oat_medium": "#EEEDE9",  # Oat Medium - Primary
    "navy": "#1B3139",        # Navy 800 - Primary
    "maroon": "#98102A",      # Maroon 600 - Secondary
    "green": "#00A972",       # Green 600 - Secondary
    "gray_nav": "#303F47",    # Gray - Navigation
    "gray_text": "#5A6F77",   # Gray - Text
    "gray_lines": "#DCE0E2",  # Gray - Lines
}

# Homepage layout with Databricks brand colors
homepage_layout = html.Div([
    html.Div([
        html.H2(
            "Welcome to Databricks Apps Examples", 
            className="mb-4", 
            style={"color": DATABRICKS_COLORS["navy"]}
        ),
        html.P([
            "This application demonstrates how to integrate Databricks ",
            "functionality into your Dash applications."
        ], className="mb-3"),
        html.P([
            "Use the sidebar to navigate between different examples."
        ], className="mb-3"),
        dbc.Card([
            dbc.CardHeader(
                "Getting Started", 
                style={
                    "background-color": DATABRICKS_COLORS["navy"], 
                    "color": "white"
                }
            ),
            dbc.CardBody([
                html.P([
                    "To enable all features, configure your Databricks ",
                    "credentials in the app.yaml file."
                ]),
                html.Pre(
                    """
env_variables:
  DATABRICKS_HOST: your-workspace.cloud.databricks.com
  DATABRICKS_TOKEN: your-token
  DATABRICKS_SQL_WAREHOUSE_ID: your-warehouse-id
                    """, 
                    className="bg-light p-3 rounded"
                )
            ])
        ], className="mb-4"),
        dbc.Card([
            dbc.CardHeader(
                "Features", 
                style={
                    "background-color": DATABRICKS_COLORS["secondary"], 
                    "color": "white"
                }
            ),
            dbc.CardBody([
                dbc.ListGroup([
                    dbc.ListGroupItem([
                        html.I(
                            className="fas fa-database me-2",
                            style={"color": DATABRICKS_COLORS["primary"]}
                        ),
                        "DBSQL Connectivity"
                    ], color="light"),
                    dbc.ListGroupItem([
                        html.I(
                            className="fas fa-chart-bar me-2",
                            style={"color": DATABRICKS_COLORS["green"]}
                        ),
                        "Data Visualization"
                    ], color="light"),
                    dbc.ListGroupItem([
                        html.I(
                            className="fas fa-lock me-2",
                            style={"color": DATABRICKS_COLORS["maroon"]}
                        ),
                        "Authentication Integration"
                    ], color="light"),
                ])
            ])
        ])
    ], className="container")
], style={"padding": "20px", "background-color": DATABRICKS_COLORS["light"]}) 