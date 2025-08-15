import dash
import dash_mantine_components as dmc
from dash import Input, Output, callback, html

from auth import get_genie_spaces_sp, get_genie_spaces_obo, get_genie_conversations_sp, get_genie_conversations_obo, get_user_token
from utils import create_genie_list


@callback(
    [
        Output("spaces-output-sp", "children"),
        Output("spaces-container-sp", "style"),
        Output("list-conversations-sp", "disabled"),
        Output("alert-genie-sp", "children"),
        Output("alert-genie-sp", "color"),
        Output("alert-genie-sp", "title"),
    ],
    Input("list-spaces-sp", "n_clicks"),
    prevent_initial_call=True,
)
def list_spaces_sp_callback(n_clicks):
    """List Genie spaces using Service Principal credentials"""
    if not n_clicks:
        return dash.no_update
    
    container_style = {"display": "none"}
    
    try:
        spaces_data = get_genie_spaces_sp()
        if spaces_data and 'spaces' in spaces_data and len(spaces_data['spaces']) > 0:
            spaces_list = create_genie_list(spaces_data['spaces'])
            alert_msg = [
                "Success! Found ",
                html.B(f"{len(spaces_data['spaces'])}"),
                " Genie spaces using Service Principal credentials.",
            ]
            alert_color = "green"
            alert_title = "Spaces Retrieved"
            container_style = {"display": "block"}
            # Enable conversations button if spaces found
            conversations_disabled = len(spaces_data['spaces']) == 0
            return spaces_list, container_style, conversations_disabled, alert_msg, alert_color, alert_title
        else:
            alert_msg = "No Genie spaces found or error occurred."
            alert_color = "yellow"
            alert_title = "No Spaces"
            return "", container_style, True, alert_msg, alert_color, alert_title
    except Exception as e:
        alert_msg = ["Error retrieving Genie spaces with Service Principal: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "Error"
        return "", container_style, True, alert_msg, alert_color, alert_title


@callback(
    [
        Output("conversations-output-sp", "children"),
        Output("conversations-container-sp", "style"),
        Output("alert-genie-sp", "children", allow_duplicate=True),
        Output("alert-genie-sp", "color", allow_duplicate=True),
        Output("alert-genie-sp", "title", allow_duplicate=True),
    ],
    Input("list-conversations-sp", "n_clicks"),
    prevent_initial_call=True,
)
def list_conversations_sp_callback(n_clicks):
    """List conversations in a space using Service Principal credentials"""
    if not n_clicks:
        return dash.no_update
    
    container_style = {"display": "none"}
    
    # For demo, use first available space ID (in real app, let user select)
    try:
        spaces_data = get_genie_spaces_sp()
        if spaces_data and 'spaces' in spaces_data and len(spaces_data['spaces']) > 0:
            first_space = spaces_data['spaces'][0]
            # Try different possible ID field names
            first_space_id = first_space.get('id') or first_space.get('space_id') or first_space.get('_id') or first_space.get('genie_space_id')
            if not first_space_id:
                print(f"ERROR: No valid ID found in space: {first_space}")
                alert_msg = "Error: Could not find valid space ID in response."
                alert_color = "red"
                alert_title = "Invalid Response"
                return "", container_style, alert_msg, alert_color, alert_title
            space_name = spaces_data['spaces'][0].get('title', 'Unknown Space')
            conv_data = get_genie_conversations_sp(first_space_id)
            if conv_data and 'conversations' in conv_data:
                conversations_list = create_genie_list(conv_data['conversations'], 'title', 'id')
                alert_msg = [
                    "Success! Found ",
                    html.B(f"{len(conv_data['conversations'])}"),
                    " conversations in space ",
                    dmc.Code(space_name),
                    " using Service Principal credentials.",
                ]
                alert_color = "green"
                alert_title = "Conversations Retrieved"
                container_style = {"display": "block"}
                return conversations_list, container_style, alert_msg, alert_color, alert_title
            else:
                alert_msg = f"No conversations found in space {space_name}."
                alert_color = "yellow"
                alert_title = "No Conversations"
                return "", container_style, alert_msg, alert_color, alert_title
        else:
            alert_msg = "No spaces available to query for conversations."
            alert_color = "yellow"
            alert_title = "No Spaces"
            return "", container_style, alert_msg, alert_color, alert_title
    except Exception as e:
        alert_msg = ["Error retrieving conversations with Service Principal: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "Error"
        return "", container_style, alert_msg, alert_color, alert_title


@callback(
    [
        Output("spaces-output-obo", "children"),
        Output("spaces-container-obo", "style"),
        Output("list-conversations-obo", "disabled"),
        Output("alert-genie-obo", "children"),
        Output("alert-genie-obo", "color"),
        Output("alert-genie-obo", "title"),
    ],
    Input("list-spaces-obo", "n_clicks"),
    prevent_initial_call=True,
)
def list_spaces_obo_callback(n_clicks):
    """List Genie spaces using On-Behalf-Of (OBO) credentials"""
    if not n_clicks:
        return dash.no_update
    
    container_style = {"display": "none"}
    
    try:
        user_token = get_user_token()
        if not user_token:
            alert_msg = [
                "Error: ",
                dmc.InlineCodeHighlight(code="X-Forwarded-Access-Token"),
                " not found. Cannot access Genie API with OBO. Ensure OBO is enabled for the App.",
            ]
            alert_color = "red"
            alert_title = "OBO Token Missing"
            return "", container_style, True, alert_msg, alert_color, alert_title
            
        spaces_data = get_genie_spaces_obo(user_token)
        if spaces_data and 'spaces' in spaces_data:
            spaces_list = create_genie_list(spaces_data['spaces'])
            alert_msg = [
                "Success! Found ",
                html.B(f"{len(spaces_data['spaces'])}"),
                " Genie spaces using OBO authorization.",
            ]
            alert_color = "green"
            alert_title = "Spaces Retrieved"
            container_style = {"display": "block"}
            # Enable conversations button if spaces found
            conversations_disabled = len(spaces_data['spaces']) == 0
            return spaces_list, container_style, conversations_disabled, alert_msg, alert_color, alert_title
        else:
            alert_msg = "No Genie spaces found or error occurred with OBO authorization."
            alert_color = "yellow"
            alert_title = "No Spaces"
            return "", container_style, True, alert_msg, alert_color, alert_title
    except Exception as e:
        alert_msg = ["Error retrieving Genie spaces with OBO: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "Error"
        return "", container_style, True, alert_msg, alert_color, alert_title


@callback(
    [
        Output("conversations-output-obo", "children"),
        Output("conversations-container-obo", "style"),
        Output("alert-genie-obo", "children", allow_duplicate=True),
        Output("alert-genie-obo", "color", allow_duplicate=True),
        Output("alert-genie-obo", "title", allow_duplicate=True),
    ],
    Input("list-conversations-obo", "n_clicks"),
    prevent_initial_call=True,
)
def list_conversations_obo_callback(n_clicks):
    """List conversations in a space using On-Behalf-Of (OBO) credentials"""
    if not n_clicks:
        return dash.no_update
    
    container_style = {"display": "none"}
    
    # For demo, use first available space ID (in real app, let user select)
    try:
        user_token = get_user_token()
        if not user_token:
            alert_msg = [
                "Error: ",
                dmc.InlineCodeHighlight(code="X-Forwarded-Access-Token"),
                " not found. Cannot access Genie API with OBO.",
            ]
            alert_color = "red"
            alert_title = "OBO Token Missing"
            return "", container_style, alert_msg, alert_color, alert_title
            
        spaces_data = get_genie_spaces_obo(user_token)
        if spaces_data and 'spaces' in spaces_data and len(spaces_data['spaces']) > 0:
            first_space = spaces_data['spaces'][0]
            # Try different possible ID field names
            first_space_id = first_space.get('id') or first_space.get('space_id') or first_space.get('_id') or first_space.get('genie_space_id')
            if not first_space_id:
                print(f"ERROR: No valid ID found in space: {first_space}")
                alert_msg = "Error: Could not find valid space ID in response."
                alert_color = "red"
                alert_title = "Invalid Response"
                return "", container_style, alert_msg, alert_color, alert_title
            space_name = spaces_data['spaces'][0].get('title', 'Unknown Space')
            conv_data = get_genie_conversations_obo(first_space_id, user_token)
            if conv_data and 'conversations' in conv_data:
                conversations_list = create_genie_list(conv_data['conversations'], 'title', 'id')
                alert_msg = [
                    "Success! Found ",
                    html.B(f"{len(conv_data['conversations'])}"),
                    " conversations in space ",
                    dmc.Code(space_name),
                    " using OBO authorization.",
                ]
                alert_color = "green"
                alert_title = "Conversations Retrieved"
                container_style = {"display": "block"}
                return conversations_list, container_style, alert_msg, alert_color, alert_title
            else:
                alert_msg = f"No conversations found in space {space_name} with OBO authorization."
                alert_color = "yellow"
                alert_title = "No Conversations"
                return "", container_style, alert_msg, alert_color, alert_title
        else:
            alert_msg = "No spaces available to query for conversations with OBO authorization."
            alert_color = "yellow"
            alert_title = "No Spaces"
            return "", container_style, alert_msg, alert_color, alert_title
    except Exception as e:
        alert_msg = ["Error retrieving conversations with OBO: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "Error"
        return "", container_style, alert_msg, alert_color, alert_title
