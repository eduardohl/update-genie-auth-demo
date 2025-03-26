import os
import dash
import yaml
from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from app_components.home.home_frontend import homepage_layout

# Define Databricks official color scheme
DATABRICKS_COLORS = {
    "primary": "#FF3621",    # Orange 600 - Primary
    "secondary": "#2272B4",  # Blue 600 - Secondary
    "accent": "#FFAB00",     # Yellow 600 - Secondary
    "light": "#F9F7F4",      # Oat Light - Primary
    "dark": "#1B3139",       # Navy 800 - Primary
    "navy": "#1B3139",       # Navy 800 - Primary
    "gray_nav": "#303F47",   # Gray - Navigation
}


def load_config():
    """Load configuration from app.yaml file."""
    try:
        with open('app.yaml', 'r') as file:
            yaml_content = yaml.safe_load(file)
            if 'env_variables' in yaml_content:
                return yaml_content['env_variables']
            return {}
    except Exception:
        return {}


def is_component_configured(component_name, config):
    """Check if a component has the necessary configuration."""
    if component_name == "dbsql":
        return bool(config.get("DATABRICKS_SQL_WAREHOUSE_ID", ""))
    elif component_name == "genie":
        # For Genie, we need both the SPACE_ID and check if the connection works
        space_id = config.get("DATABRICKS_GENIE_SPACE_ID", "")
        if not space_id:
            return False
            
        # Import on demand to avoid circular imports
        try:
            from app_components.genie.app_functions import get_genie_status
            status = get_genie_status()
            return status.get("status") == "available"
        except Exception:
            return False
    elif component_name == "vector_search":
        return bool(config.get("DATABRICKS_HOST", "")) and bool(
            config.get("DATABRICKS_TOKEN", ""))
    return True


# Load configuration
config = load_config()

# Import components
try:
    from app_components.dbsql.app_frontend import dbsql_layout
    is_dbsql_available = True
except Exception as e:
    is_dbsql_available = False
    dbsql_layout = html.Div([
        html.H3("Error importing DBSQL component"),
        html.P(f"Error: {str(e)}")
    ])

# Import Genie component
try:
    from app_components.genie.app_frontend import genie_layout
    is_genie_available = True
except Exception as e:
    is_genie_available = False
    genie_layout = html.Div([
        html.H3("Error importing Genie component"),
        html.P(f"Error: {str(e)}")
    ])

# Initialize the Dash app
FONT_AWESOME_CSS = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"
)

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        FONT_AWESOME_CSS
    ],
    suppress_callback_exceptions=True,
    assets_folder="assets"
)

app.title = "Databricks Demos"

# HTML template
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Create sidebar with homepage, DBSQL and Genie components 
sidebar = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Img(
                                            src=(
                                                "https://raw.githubusercontent.com"
                                                "/plotly/Dash-Databricks-SDK"
                                                "-Article/main/assets"
                                                "/databricks.png"
                                            ),
                                            className="logo",
                                            style={
                                                "height": "30px", 
                                                "margin-right": "10px"
                                            }
                                        ),
                                        html.Span(
                                            "Databricks Apps Examples",
                                            id="app-title",
                                            style={
                                                "font-weight": "bold",
                                                "color": (
                                                    DATABRICKS_COLORS["dark"]
                                                ),
                                                "font-size": "1.1rem"
                                            }
                                        ),
                                    ],
                                    className="d-flex align-items-center"
                                ),
                            ],
                            className=(
                                "d-flex justify-content-between "
                                "align-items-center"
                            ),
                        ),
                    ],
                    className="border-bottom",
                    style={
                        "background-color": "white",
                        "border-color": "#eee"
                    }
                ),
                dbc.CardBody(
                    [
                        dbc.Nav(
                            [
                                # Homepage nav item
                                dbc.NavItem(
                                    dbc.NavLink(
                                        [
                                            html.I(
                                                className="fas fa-home me-2",
                                                style={"font-size": "1.2rem"},
                                                id="home-icon"
                                            ),
                                            html.Span(
                                                "Home",
                                                id="home-text",
                                            ),
                                        ],
                                        href="#",
                                        active=True,
                                        id="sidebar-item-home",
                                    ),
                                    className="w-100",
                                ),
                                # DBSQL nav item
                                dbc.NavItem(
                                    dbc.NavLink(
                                        [
                                            html.I(
                                                className=(
                                                    "fas " + 
                                                    ("fa-check-circle text-success" 
                                                     if is_component_configured(
                                                         'dbsql', 
                                                         config
                                                     ) 
                                                     else "fa-times-circle text-danger") +
                                                    " me-2"
                                                ),
                                                style={"font-size": "1.2rem"},
                                                id="dbsql-icon"
                                            ),
                                            html.Span(
                                                "DBSQL",
                                                id="dbsql-text",
                                            ),
                                        ],
                                        href="#",
                                        active=False,
                                        id="sidebar-item-dbsql",
                                    ),
                                    className="w-100",
                                ),
                                # Genie nav item
                                dbc.NavItem(
                                    dbc.NavLink(
                                        [
                                            html.I(
                                                className=(
                                                    "fas " + 
                                                    ("fa-check-circle text-success" 
                                                     if is_component_configured(
                                                         'genie', 
                                                         config
                                                     ) 
                                                     else "fa-times-circle text-danger") +
                                                    " me-2"
                                                ),
                                                style={"font-size": "1.2rem"},
                                                id="genie-icon"
                                            ),
                                            html.Span(
                                                "Genie",
                                                id="genie-text",
                                            ),
                                        ],
                                        href="#",
                                        active=False,
                                        id="sidebar-item-genie",
                                    ),
                                    className="w-100",
                                ),
                            ],
                            vertical=True,
                            pills=True,
                            className="flex-column",
                            style={"border-bottom": "1px solid #eee"}
                        ),
                    ],
                    className="p-0",
                    style={"background-color": "white"}
                ),
            ],
            className="h-100 border-0",
            style={"box-shadow": "2px 0 10px rgba(0, 0, 0, 0.1)"}
        ),
        # Toggle button at the bottom
        html.I(
            id="sidebar-toggle",
            className="fas fa-chevron-left sidebar-toggle",
        ),
    ],
    className="sidebar",
    id="sidebar",
    style={"width": "250px"},
)

# Modal for configuration requirements
config_modal = dbc.Modal(
    [
        dbc.ModalHeader("Configuration Required"),
        dbc.ModalBody(
            html.Div([
                html.P(
                    "This component requires configuration in app.yaml "
                    "before it can be used.",
                    className="mb-3",
                ),
                html.P(
                    "Please add the necessary configuration variables to the "
                    "app.yaml file and restart the application.",
                    className="mb-3",
                ),
                html.Code(
                    id="config-requirements",
                    style={
                        "white-space": "pre-wrap", 
                        "display": "block", 
                        "padding": "10px"
                    },
                ),
            ])
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-config-modal", className="ms-auto")
        ),
    ],
    id="config-modal",
    size="lg",
)

# Content area
content = html.Div(
    [
        html.Div(id="app-content", children=homepage_layout),
        config_modal,
    ],
    className="content",
    id="content",
)

# Main layout
app.layout = html.Div([sidebar, content])


# Callback to toggle sidebar
@callback(
    [
        Output("sidebar", "style"),
        Output("sidebar", "className"),
        Output("content", "className"),
        Output("sidebar-toggle", "className"),
        Output("home-text", "style"),
        Output("dbsql-text", "style"),
        Output("genie-text", "style"),
        Output("app-title", "style"),
    ],
    Input("sidebar-toggle", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks):
    """Toggle the sidebar open and closed."""
    if n_clicks and n_clicks % 2 == 1:
        # Collapsed sidebar
        toggle_class = (
            "fas fa-chevron-right sidebar-toggle "
            "sidebar-toggle-collapsed"
        )
        return (
            {"width": "60px"},  # sidebar style
            "sidebar sidebar-collapsed",  # sidebar className
            "content content-collapsed",  # content className
            toggle_class,  # toggle className
            {"display": "none"},  # home-text
            {"display": "none"},  # dbsql-text
            {"display": "none"},  # genie-text
            {"display": "none"},  # app-title
        )
    else:
        # Expanded sidebar
        return (
            {"width": "250px"},  # sidebar
            "sidebar",  # sidebar className
            "content",  # content
            "fas fa-chevron-left sidebar-toggle",  # toggle className
            {},  # home-text
            {},  # dbsql-text
            {},  # genie-text
            {
                "fontWeight": "bold",
                "color": DATABRICKS_COLORS["dark"],
                "fontSize": "1.1rem"
            },  # app-title
        )


# Callback to update content based on navigation
@callback(
    [
        Output("app-content", "children"),
        Output("sidebar-item-home", "style", allow_duplicate=True),
        Output("sidebar-item-dbsql", "style", allow_duplicate=True),
        Output("sidebar-item-genie", "style", allow_duplicate=True),
    ],
    [
        Input("sidebar-item-home", "n_clicks"),
        Input("sidebar-item-dbsql", "n_clicks"),
        Input("sidebar-item-genie", "n_clicks"),
    ],
    [
        State("sidebar-item-home", "style"),
        State("sidebar-item-dbsql", "style"),
        State("sidebar-item-genie", "style"),
    ],
    prevent_initial_call=True
)
def update_content(home_clicks, dbsql_clicks, genie_clicks, 
                  home_style, dbsql_style, genie_style):
    """Update the content area based on which sidebar item was clicked."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Reset all nav items to default style
    default_style = {}
    
    # Style for the active nav item
    active_style = {}
    
    if triggered_id == "sidebar-item-home":
        return homepage_layout, active_style, default_style, default_style
    elif triggered_id == "sidebar-item-dbsql":
        # Even if the component is not configured, we'll show the layout
        # The layout itself will display the proper error message
        return dbsql_layout, default_style, active_style, default_style
    elif triggered_id == "sidebar-item-genie":
        # Always return the genie_layout - even if there are configuration issues
        # The layout itself will show appropriate error messages
        try:
            return genie_layout, default_style, default_style, active_style
        except Exception as e:
            # Fallback if there's an error loading the component
            error_layout = html.Div([
                html.H3("Error Loading Genie Component"),
                html.P(f"There was an error loading the Genie component: {str(e)}"),
                html.Hr(),
                html.P("Please check your configuration in app.yaml and ensure:"),
                html.Ul([
                    html.Li("DATABRICKS_HOST is set correctly"),
                    html.Li("DATABRICKS_TOKEN is valid"),
                    html.Li("DATABRICKS_GENIE_SPACE_ID is set to a valid Genie space ID")
                ])
            ])
            return error_layout, default_style, default_style, active_style
    
    # Default case (should not happen)
    return homepage_layout, active_style, default_style, default_style


# Callback to close the config modal
@callback(
    Output("config-modal", "is_open"),
    Input("close-config-modal", "n_clicks"),
    prevent_initial_call=True,
)
def close_config_modal(n_clicks):
    """Close the configuration modal."""
    return False


# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run_server(
        debug=True, 
        host="0.0.0.0", 
        port=port
    ) 