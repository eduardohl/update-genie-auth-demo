import dash
import dash_mantine_components as dmc
from dash import Input, Output, callback, html
import jwt
import json

from auth import fetch_sp_details, fetch_warehouses


@callback(
    [
        Output("header-username", "children"),
        Output("obo-token-status", "children"),
        Output("obo-token-status", "color"),
        Output("obo-token-status", "title"),
        Output("run-query-obo", "disabled"),
        Output("obo-token-store", "data"),
        Output("obo-username", "children"),
        Output("sql-http-path", "data"),
        Output("sql-http-path", "value"),
        Output("sp-name-display", "children"),
        Output("jwt-raw-token", "children"),
        Output("jwt-decoded", "children"),
        Output("jwt-scopes-list", "children"),
        Output("accordion-container", "style"),
        # Genie-specific outputs
        Output("sp-name-display-genie", "children"),
        Output("obo-username-genie", "children"),
        Output("obo-token-status-genie", "children"),
        Output("obo-token-status-genie", "color"),
        Output("obo-token-status-genie", "title"),
        Output("list-spaces-obo", "disabled"),
    ],
    Input("initial-load-trigger", "children"),
)
def update_header_and_warehouses(_):
    # Call fetch_warehouses() and get the results directly
    wh_options, wh_value = fetch_warehouses()

    # Call fetch_sp_details() and get the result directly
    sp_name = fetch_sp_details()

    header_username_display = ["User: ", dmc.Code("Unknown")]
    obo_status_msg = "Checking OBO status..."
    obo_color = "gray"
    obo_title = "Checking..."
    obo_disabled = True
    has_token = False
    obo_username = ["Current user: ", html.B("Unknown")]
    jwt_raw = "No token available"
    jwt_decoded = "No token to decode"
    jwt_scopes_list = dmc.Text("No scopes available", size="sm", c="dimmed")
    accordion_style = {"display": "none"}

    try:
        from flask import request

        headers = dict(request.headers)
        username = headers.get("X-Forwarded-Preferred-Username")
        obo_token = headers.get("X-Forwarded-Access-Token")

        header_username_display = username if username else "Not available"
        obo_username = [
            "Current user: ",
            html.B(username if username else "Not available"),
        ]

        has_token = bool(obo_token)
        has_sql_scope = False

        if has_token:
            # Show accordion when token is present
            accordion_style = {"display": "block"}
            
            # Store the raw JWT
            jwt_raw = obo_token
            
            # Try to decode the JWT
            try:
                # Decode without verification (since we don't have the public key)
                decoded_token = jwt.decode(obo_token, options={"verify_signature": False})
                jwt_decoded = json.dumps(decoded_token, indent=2)
                
                # Parse scopes
                scopes = decoded_token.get("scope", "").split()
                
                # Check if SQL scope is present
                # Looking for scopes that contain 'sql' (case-insensitive)
                has_sql_scope = any('sql' in scope.lower() for scope in scopes)
                
                if scopes:
                    jwt_scopes_list = dmc.List(
                        [dmc.ListItem(dmc.Code(scope)) for scope in scopes],
                        size="sm",
                        spacing="xs",
                    )
                else:
                    jwt_scopes_list = dmc.Text("No scopes found in token", size="sm", c="dimmed")
                    
            except Exception as e:
                jwt_decoded = f"Error decoding JWT: {str(e)}"
                jwt_scopes_list = dmc.Text("Error parsing scopes", size="sm", c="red")
            
            # Update OBO status based on SQL scope presence
            if has_sql_scope:
                obo_status_msg = [
                    "✅ OBO Token found with SQL scope. You can run queries using your identity.",
                ]
                obo_color = "green"
                obo_title = "OBO Ready"
                obo_disabled = False
            else:
                obo_status_msg = [
                    "⚠️ OBO Token found but missing SQL scope. Cannot run queries.",
                ]
                obo_color = "yellow"
                obo_title = "Missing SQL Scope"
                obo_disabled = True
        else:
            obo_status_msg = [
                "❌ No OBO token found. Cannot run queries using your identity.",
            ]
            obo_color = "red"
            obo_title = "No OBO Token"
            obo_disabled = True

    except Exception as e:
        obo_status_msg = [
            "❌ Error checking OBO status: ",
            dmc.Code(str(e)),
        ]
        obo_color = "red"
        obo_title = "Error"
        obo_disabled = True

    return (
        header_username_display,  # header-username
        obo_status_msg,  # obo-token-status children
        obo_color,  # obo-token-status color
        obo_title,  # obo-token-status title
        obo_disabled,  # run-query-obo disabled
        {"token": has_token},  # obo-token-store data
        obo_username,  # obo-username
        wh_options,  # sql-http-path data
        wh_value,  # sql-http-path value
        sp_name,  # sp-name-display
        jwt_raw,  # jwt-raw-token
        jwt_decoded,  # jwt-decoded
        jwt_scopes_list,  # jwt-scopes-list
        accordion_style,  # accordion-container style
        sp_name,  # sp-name-display-genie
        obo_username,  # OBO username for Genie section
        obo_status_msg,  # OBO status message for Genie section
        obo_color,  # OBO color for Genie section
        obo_title,  # OBO title for Genie section
        obo_disabled,  # OBO disabled state for Genie section
    )
