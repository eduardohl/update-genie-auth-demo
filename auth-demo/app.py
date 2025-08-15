import dash
import dash_mantine_components as dmc
from dash import Dash, Input, Output, State, callback, dcc, html
import jwt
import json

from auth import (
    cfg,
    fetch_sp_details,
    get_connection_obo,
    get_connection_sp,
    get_user_token,
    get_genie_spaces_sp,
    get_genie_spaces_obo,
    get_genie_conversations_sp,
    get_genie_conversations_obo,
)
from sql import (
    fetch_warehouses,
    run_query,
)
from utils import create_data_table, get_icon, create_genie_list

# Import callbacks
from callbacks.auth_callbacks import update_header_and_warehouses
from callbacks.sql_callbacks import run_sp_query_callback, run_obo_query_callback
from callbacks.genie_callbacks import (
    list_spaces_sp_callback,
    list_conversations_sp_callback,
    list_spaces_obo_callback,
    list_conversations_obo_callback,
)
from callbacks.message_callbacks import (
    list_messages_sp_callback,
    list_messages_obo_callback,
)

app = Dash(external_stylesheets=[dmc.styles.ALL])
app.title = "Databricks Auth Demo"

app.layout = dmc.MantineProvider(
    theme={
        "fontFamily": "DM Sans, sans-serif",
        "primaryColor": "lava",
        "colors": {
            "lava": [
                "#ffe9e6",
                "#ffd2cd",
                "#ffa49a",
                "#ff7264",
                "#ff4936",
                "#ff2e18",
                "#ff1e07",
                "#e40f00",
                "#cc0500",
                "#b20000",
            ]
        },
    },
    children=dmc.AppShell(
        header={"height": 60},
        padding="md",
        children=[
            dmc.AppShellHeader(
                style={"backgroundColor": "#F9F7F4"},
                children=[
                    dmc.Container(
                        children=[
                            dmc.Group(
                                justify="space-between",
                                align="center",
                                h="100%",
                                children=[
                                    dmc.Group(
                                        gap="sm",
                                        align="center",
                                        children=[
                                            html.Img(
                                                src=app.get_asset_url("logo.svg"),
                                                height=28,
                                            ),
                                            dmc.Title(
                                                "Databricks Apps Authorization Demo",
                                                order=2,
                                            ),
                                        ],
                                    ),
                                    dmc.Badge(
                                        id="header-username",
                                        variant="outline",
                                        leftSection=get_icon(
                                            "material-symbols:person-outline"
                                        ),
                                    ),
                                ],
                            )
                        ],
                        fluid=False,
                        h="100%",
                        px=0,
                    )
                ],
            ),
            dmc.AppShellMain(
                style={"backgroundColor": "#F9F7F4"},
                children=dmc.Container(
                    [
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    dmc.Select(
                                        id="sql-http-path",
                                        label="Select SQL Warehouse",
                                        description="Choose a running SQL warehouse.",
                                        data=[],
                                        value=None,
                                        required=True,
                                        style={"width": "100%"},
                                        searchable=True,
                                        nothingFoundMessage="No warehouses found",
                                        leftSection=get_icon(
                                            "material-symbols:database-outline"
                                        ),
                                    ),
                                    span=6,
                                ),
                                dmc.GridCol(
                                    dmc.TextInput(
                                        id="table-name-input",
                                        label="Unity Catalog Table Name",
                                        description="Format: catalog.schema.table",
                                        placeholder="main.sandbox.my_table",
                                        value="samples.nyctaxi.trips",
                                        required=True,
                                        style={"width": "100%"},
                                        leftSection=get_icon(
                                            "material-symbols:table-outline"
                                        ),
                                    ),
                                    span=6,
                                ),
                            ],
                            mb="lg",
                            gutter="xl",
                        ),
                        dmc.Stack(
                            [
                                dmc.Paper(
                                    [
                                        dmc.Title(
                                            "Service Principal (SP) Authorization",
                                            order=3,
                                            mb="md",
                                        ),
                                        dmc.Text(
                                            [
                                                "Uses this app's SP credentials via the ",
                                                dmc.InlineCodeHighlight(
                                                    code="DATABRICKS_CLIENT_ID"
                                                ),
                                                " and ",
                                                dmc.InlineCodeHighlight(
                                                    code="DATABRICKS_CLIENT_SECRET"
                                                ),
                                                " headers.",
                                            ],
                                            size="sm",
                                            mb="xs",
                                        ),
                                        dmc.Text(
                                            [
                                                "Service principal: ",
                                                html.B(id="sp-name-display"),
                                            ],
                                            size="sm",
                                            mb="md",
                                        ),
                                        dmc.Button(
                                            "Run Query (SP)",
                                            id="run-query-sp",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:play-arrow-outline"
                                            ),
                                            mb="md",
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Alert(
                                            id="alert-sp",
                                            children="Status will appear here.",
                                            title="Status",
                                            color="gray",
                                            withCloseButton=True,
                                            hide=True,
                                            radius="sm",
                                        ),
                                        html.Div(
                                            create_data_table("table-output-sp"),
                                            id="table-container-sp",
                                            style={"display": "none"},
                                        ),
                                        dmc.LoadingOverlay(
                                            id="loading-overlay-sp",
                                            visible=False,
                                            loaderProps={"variant": "dots"},
                                        ),
                                    ],
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    withBorder=True,
                                    style={"position": "relative"},
                                ),
                                dmc.Paper(
                                    [
                                        dmc.Title(
                                            "On-Behalf-Of User (OBO) Authorization",
                                            order=3,
                                            mb="md",
                                        ),
                                        dmc.Text(
                                            [
                                                "Uses the accessing user's credentials via the ",
                                                dmc.InlineCodeHighlight(
                                                    code="X-Forwarded-Access-Token"
                                                ),
                                                " header.",
                                            ],
                                            size="sm",
                                            mb="xs",
                                        ),
                                        dmc.Text(
                                            id="obo-username",
                                            size="sm",
                                            mb="md",
                                        ),
                                        dmc.Alert(
                                            id="obo-token-status",
                                            title="OBO Status",
                                            color="blue",
                                            mb="md",
                                            radius="sm",
                                        ),
                                        html.Div(
                                            id="accordion-container",
                                            children=dmc.Accordion(
                                                children=[
                                                    dmc.AccordionItem(
                                                        [
                                                            dmc.AccordionControl(
                                                                "View Access Token Details",
                                                                icon=get_icon("material-symbols:key-outline"),
                                                            ),
                                                            dmc.AccordionPanel(
                                                                [
                                                                    dmc.Stack(
                                                                        [
                                                                            dmc.Text("Raw JWT Token:", size="sm", fw=500, mb="xs"),
                                                                            dmc.ScrollArea(
                                                                                dmc.Code(
                                                                                    id="jwt-raw-token",
                                                                                    children="Token will appear here when available",
                                                                                    block=True,
                                                                                    style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
                                                                                ),
                                                                                h=100,
                                                                                type="auto",
                                                                            ),
                                                                            dmc.Divider(my="md"),
                                                                            dmc.Text("Decoded JWT Payload:", size="sm", fw=500, mb="xs"),
                                                                            dmc.ScrollArea(
                                                                                dmc.Code(
                                                                                    id="jwt-decoded",
                                                                                    children="Decoded token will appear here",
                                                                                    block=True,
                                                                                    style={"whiteSpace": "pre"},
                                                                                ),
                                                                                h=200,
                                                                                type="auto",
                                                                            ),
                                                                            dmc.Divider(my="md"),
                                                                            dmc.Text("Parsed Scopes:", size="sm", fw=500, mb="xs"),
                                                                            html.Div(id="jwt-scopes-list"),
                                                                        ],
                                                                        gap="sm",
                                                                    )
                                                                ]
                                                            ),
                                                        ],
                                                        value="token-details",
                                                    )
                                                ],
                                                mb="md",
                                            ),
                                        ),
                                        dmc.Button(
                                            "Run Query (OBO)",
                                            id="run-query-obo",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:play-arrow-outline"
                                            ),
                                            mb="md",
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Alert(
                                            id="alert-obo",
                                            children="Status will appear here.",
                                            title="Status",
                                            color="gray",
                                            withCloseButton=True,
                                            hide=True,
                                            radius="sm",
                                            mt="md",
                                        ),
                                        html.Div(
                                            create_data_table("table-output-obo"),
                                            id="table-container-obo",
                                            style={"display": "none"},
                                        ),
                                        dmc.LoadingOverlay(
                                            id="loading-overlay-obo",
                                            visible=False,
                                            loaderProps={"variant": "dots"},
                                        ),
                                    ],
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    withBorder=True,
                                    style={"position": "relative"},
                                ),
                                dmc.Paper(
                                    [
                                        dmc.Title(
                                            "Service Principal (SP) - Genie API",
                                            order=3,
                                            mb="md",
                                        ),
                                        dmc.Text(
                                            [
                                                "Uses this app's SP credentials via the ",
                                                dmc.InlineCodeHighlight(
                                                    code="DATABRICKS_CLIENT_ID"
                                                ),
                                                " and ",
                                                dmc.InlineCodeHighlight(
                                                    code="DATABRICKS_CLIENT_SECRET"
                                                ),
                                                " headers to access Genie Spaces API.",
                                            ],
                                            size="sm",
                                            mb="xs",
                                        ),
                                        dmc.Text(
                                            [
                                                "Service principal: ",
                                                html.B(id="sp-name-display-genie"),
                                            ],
                                            size="sm",
                                            mb="md",
                                        ),
                                        dmc.Button(
                                            "List Genie Spaces (SP)",
                                            id="list-spaces-sp",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:space-dashboard-outline"
                                            ),
                                            mb="md",
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Select(
                                            id="space-selector-sp",
                                            label="Select Space for Conversations",
                                            placeholder="Choose a space...",
                                            data=[],
                                            mb="md",
                                            style={"display": "none"},
                                        ),
                                        dmc.Select(
                                            id="conversation-selector-sp",
                                            label="Select Conversation for Messages",
                                            placeholder="Choose a conversation...",
                                            data=[],
                                            mb="md",
                                            style={"display": "none"},
                                        ),
                                        dmc.Button(
                                            "List Conversations (SP)",
                                            id="list-conversations-sp",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:chat-outline"
                                            ),
                                            mb="md",
                                            disabled=True,
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Button(
                                            "List Messages (SP)",
                                            id="list-messages-sp",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:message-outline"
                                            ),
                                            mb="md",
                                            disabled=True,
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Alert(
                                            id="alert-genie-sp",
                                            children="Status will appear here.",
                                            title="Status",
                                            color="gray",
                                            withCloseButton=True,
                                            hide=True,
                                            radius="sm",
                                        ),
                                        # Spaces output container
                                        html.Div([
                                            dmc.Text("Genie Spaces", size="sm", fw=500, mb="xs"),
                                            html.Div(id="spaces-output-sp")
                                        ], id="spaces-container-sp", style={"display": "none"}, className="mb-3"),
                                        
                                        # Conversations output container
                                        html.Div([
                                            dmc.Text("Conversations", size="sm", fw=500, mb="xs"),
                                            html.Div(id="conversations-output-sp")
                                        ], id="conversations-container-sp", style={"display": "none"}, className="mb-3"),
                                        
                                        # Messages output container
                                        html.Div([
                                            dmc.Text("Messages", size="sm", fw=500, mb="xs"),
                                            html.Div(id="messages-output-sp")
                                        ], id="messages-container-sp", style={"display": "none"}, className="mb-3"),
                                        dmc.LoadingOverlay(
                                            id="loading-overlay-genie-sp",
                                            visible=False,
                                            loaderProps={"variant": "dots"},
                                        ),
                                    ],
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    withBorder=True,
                                    style={"position": "relative"},
                                ),
                                dmc.Paper(
                                    [
                                        dmc.Title(
                                            "On-Behalf-Of User (OBO) - Genie API",
                                            order=3,
                                            mb="md",
                                        ),
                                        dmc.Text(
                                            [
                                                "Uses the accessing user's credentials via the ",
                                                dmc.InlineCodeHighlight(
                                                    code="X-Forwarded-Access-Token"
                                                ),
                                                " header to access Genie Spaces API.",
                                            ],
                                            size="sm",
                                            mb="xs",
                                        ),
                                        dmc.Text(
                                            id="obo-username-genie",
                                            size="sm",
                                            mb="md",
                                        ),
                                        dmc.Alert(
                                            id="obo-token-status-genie",
                                            title="OBO Status",
                                            color="blue",
                                            mb="md",
                                            radius="sm",
                                        ),
                                        dmc.Button(
                                            "List Genie Spaces (OBO)",
                                            id="list-spaces-obo",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:space-dashboard-outline"
                                            ),
                                            mb="md",
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Select(
                                            id="space-selector-obo",
                                            label="Select Space for Conversations",
                                            placeholder="Choose a space...",
                                            mb="md",
                                            style={"display": "none"},
                                        ),
                                        dmc.Select(
                                            id="conversation-selector-obo",
                                            label="Select Conversation for Messages",
                                            placeholder="Choose a conversation...",
                                            mb="md",
                                            style={"display": "none"},
                                        ),
                                        dmc.Button(
                                            "List Conversations (OBO)",
                                            id="list-conversations-obo",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:chat-outline"
                                            ),
                                            mb="md",
                                            disabled=True,
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Button(
                                            "List Messages (OBO)",
                                            id="list-messages-obo",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:message-outline"
                                            ),
                                            mb="md",
                                            disabled=True,
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Alert(
                                            id="alert-genie-obo",
                                            children="Status will appear here.",
                                            title="Status",
                                            color="gray",
                                            withCloseButton=True,
                                            hide=True,
                                            radius="sm",
                                        ),
                                        # Spaces output container
                                        html.Div([
                                            dmc.Text("Genie Spaces", size="sm", fw=500, mb="xs"),
                                            html.Div(id="spaces-output-obo")
                                        ], id="spaces-container-obo", style={"display": "none"}, className="mb-3"),
                                        
                                        # Conversations output container  
                                        html.Div([
                                            dmc.Text("Conversations", size="sm", fw=500, mb="xs"),
                                            html.Div(id="conversations-output-obo")
                                        ], id="conversations-container-obo", style={"display": "none"}, className="mb-3"),
                                        
                                        # Messages output container
                                        html.Div([
                                            dmc.Text("Messages", size="sm", fw=500, mb="xs"),
                                            html.Div(id="messages-output-obo")
                                        ], id="messages-container-obo", style={"display": "none"}, className="mb-3"),
                                        dmc.LoadingOverlay(
                                            id="loading-overlay-genie-obo",
                                            visible=False,
                                            loaderProps={"variant": "dots"},
                                        ),
                                    ],
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    withBorder=True,
                                    style={"position": "relative"},
                                ),
                            ],
                            gap="xl",
                        ),
                        html.Div(id="initial-load-trigger", style={"display": "none"}),
                        dcc.Store(id="obo-token-store"),
                    ],
                    fluid=False,
                    p="0",
                ),
            ),
        ],
    ),
)


# Callback function moved to callbacks/auth_callbacks.py


# Callback function moved to callbacks/sql_callbacks.py


# Callback function moved to callbacks/sql_callbacks.py


# Genie callback functions moved to callbacks/genie_callbacks.py


if __name__ == "__main__":
    app.run()
