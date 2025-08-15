import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html

from auth import get_genie_spaces_sp, get_genie_spaces_obo, get_genie_conversations_sp, get_genie_conversations_obo, get_user_token
from utils import create_genie_list


@callback(
    [
        Output("spaces-output-sp", "children"),
        Output("spaces-container-sp", "style"),
        Output("list-conversations-sp", "disabled"),
        Output("space-selector-sp", "data"),
        Output("space-selector-sp", "style"),
        Output("alert-genie-sp", "children"),
        Output("alert-genie-sp", "color"),
        Output("alert-genie-sp", "title"),
        Output("alert-genie-sp", "hide"),
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
        
        # Check for empty response (likely permission issue)
        if not spaces_data:
            alert_msg = [
                "Error: Failed to retrieve Genie spaces. This could be due to:",
                html.Br(),
                "• Missing Service Principal permissions for Genie API",
                html.Br(),
                "• Genie features not enabled in this workspace",
                html.Br(),
                "• API endpoint not accessible with current credentials"
            ]
            alert_color = "red"
            alert_title = "Access Denied"
            space_selector_style = {"display": "none"}
            return "", container_style, True, [], space_selector_style, alert_msg, alert_color, alert_title, False
        
        # Check for empty response structure (permission issue)
        if isinstance(spaces_data, dict) and len(spaces_data) == 0:
            alert_msg = [
                "Error: Service Principal received empty response from Genie API.",
                html.Br(),
                "This typically indicates:",
                html.Br(),
                "• Missing 'dashboards.genie' scope in SP permissions",
                html.Br(),
                "• Genie API access not granted to this Service Principal",
                html.Br(),
                "• Workspace-level restrictions on Genie features"
            ]
            alert_color = "red"
            alert_title = "Permission Denied"
            space_selector_style = {"display": "none"}
            return "", container_style, True, [], space_selector_style, alert_msg, alert_color, alert_title, False
        
        # Check for proper response structure
        if isinstance(spaces_data, dict) and 'spaces' in spaces_data and len(spaces_data['spaces']) > 0:
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
            # Create dropdown options for spaces
            space_options = [{"label": space.get('title', 'Unknown Space'), "value": space.get('id') or space.get('space_id') or space.get('_id') or space.get('genie_space_id')} for space in spaces_data['spaces']]
            space_selector_style = {"display": "block"}
            
            return spaces_list, container_style, conversations_disabled, space_options, space_selector_style, alert_msg, alert_color, alert_title
        else:
            # Handle unexpected response structure
            if isinstance(spaces_data, dict):
                response_keys = list(spaces_data.keys())
                alert_msg = [
                    "Error: Unexpected response structure from Genie API.",
                    html.Br(),
                    "Response keys: ",
                    dmc.Code(str(response_keys)),
                    html.Br(),
                    "This suggests the API response format has changed or there's a configuration issue."
                ]
            else:
                alert_msg = [
                    "Error: Unexpected response type from Genie API.",
                    html.Br(),
                    "Expected dict, got: ",
                    dmc.Code(str(type(spaces_data))),
                    html.Br(),
                    "This suggests an API configuration or authentication issue."
                ]
            alert_color = "red"
            alert_title = "API Error"
            space_selector_style = {"display": "none"}
            return "", container_style, True, [], space_selector_style, alert_msg, alert_color, alert_title
            
    except Exception as e:
        alert_msg = [
            "Error retrieving Genie spaces with Service Principal: ",
            dmc.Code(str(e)),
            html.Br(),
            html.Br(),
            "This could be due to:",
            html.Br(),
            "• Network connectivity issues",
            html.Br(),
            "• Invalid Service Principal credentials",
            html.Br(),
            "• Genie API endpoint not accessible"
        ]
        alert_color = "red"
        alert_title = "Connection Error"
        space_selector_style = {"display": "none"}
        return "", container_style, True, [], space_selector_style, alert_msg, alert_color, alert_title, False


@callback(
    [
        Output("conversations-output-sp", "children"),
        Output("conversations-container-sp", "style"),
        Output("conversation-selector-sp", "data"),
        Output("conversation-selector-sp", "style"),
        Output("list-messages-sp", "disabled"),
        Output("alert-genie-sp", "children", allow_duplicate=True),
        Output("alert-genie-sp", "color", allow_duplicate=True),
        Output("alert-genie-sp", "title", allow_duplicate=True),
    ],
    Input("list-conversations-sp", "n_clicks"),
    State("space-selector-sp", "value"),
    prevent_initial_call=True,
)
def list_conversations_sp_callback(n_clicks, selected_space_id):
    """List conversations in a space using Service Principal credentials"""
    if not n_clicks:
        return dash.no_update
    
    if not selected_space_id:
        alert_msg = "Please select a space first."
        alert_color = "yellow"
        alert_title = "No Space Selected"
        return "", {"display": "none"}, alert_msg, alert_color, alert_title
    
    container_style = {"display": "none"}
    
    try:
        # Get space details to find the name
        spaces_data = get_genie_spaces_sp()
        space_name = "Unknown Space"
        if spaces_data and 'spaces' in spaces_data:
            for space in spaces_data['spaces']:
                space_id = space.get('id') or space.get('space_id') or space.get('_id') or space.get('genie_space_id')
                if space_id == selected_space_id:
                    space_name = space.get('title', 'Unknown Space')
                    break
        
        conv_data = get_genie_conversations_sp(selected_space_id)
        if conv_data and 'conversations' in conv_data:
            conversations_list = create_genie_list(conv_data['conversations'], 'title', 'id')
            
            # Create dropdown options for conversations
            conversation_options = [{"label": conv.get('title', 'Unknown Conversation'), "value": conv.get('id') or conv.get('conversation_id') or conv.get('_id') or conv.get('genie_conversation_id')} for conv in conv_data['conversations']]
            conversation_selector_style = {"display": "block"}
            messages_disabled = len(conv_data['conversations']) == 0
            
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
            return conversations_list, container_style, conversation_options, conversation_selector_style, messages_disabled, alert_msg, alert_color, alert_title
        else:
            alert_msg = f"No conversations found in space {space_name}."
            alert_color = "yellow"
            alert_title = "No Conversations"
            conversation_selector_style = {"display": "none"}
            return "", container_style, [], conversation_selector_style, True, alert_msg, alert_color, alert_title
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
        Output("space-selector-obo", "data"),
        Output("space-selector-obo", "style"),
        Output("alert-genie-obo", "children"),
        Output("alert-genie-obo", "color"),
        Output("alert-genie-obo", "title"),
        Output("alert-genie-obo", "hide"),
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
            space_selector_style = {"display": "none"}
            return "", container_style, True, [], space_selector_style, alert_msg, alert_color, alert_title, False
            
        spaces_data = get_genie_spaces_obo(user_token)
        
        # Check for empty response (likely permission issue)
        if not spaces_data:
            alert_msg = [
                "Error: Failed to retrieve Genie spaces with OBO. This could be due to:",
                html.Br(),
                "• Missing user permissions for Genie API",
                html.Br(),
                "• Genie features not enabled in this workspace",
                html.Br(),
                "• API endpoint not accessible with your user credentials"
            ]
            alert_color = "red"
            alert_title = "Access Denied"
            space_selector_style = {"display": "none"}
            return "", container_style, True, [], space_selector_style, alert_msg, alert_color, alert_title, False
        
        # Check for proper response structure
        if isinstance(spaces_data, dict) and 'spaces' in spaces_data and len(spaces_data['spaces']) > 0:
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
            # Create dropdown options for spaces
            space_options = [{"label": space.get('title', 'Unknown Space'), "value": space.get('id') or space.get('space_id') or space.get('_id') or space.get('genie_space_id')} for space in spaces_data['spaces']]
            space_selector_style = {"display": "block"}
            
            return spaces_list, container_style, conversations_disabled, space_options, space_selector_style, alert_msg, alert_color, alert_title, False
        else:
            # Handle unexpected response structure
            if isinstance(spaces_data, dict):
                response_keys = list(spaces_data.keys())
                alert_msg = [
                    "Error: Unexpected response structure from Genie API with OBO.",
                    html.Br(),
                    "Response keys: ",
                    dmc.Code(str(response_keys)),
                    html.Br(),
                    "This suggests the API response format has changed or there's a configuration issue."
                ]
            else:
                alert_msg = [
                    "Error: Unexpected response type from Genie API with OBO.",
                    html.Br(),
                    "Expected dict, got: ",
                    dmc.Code(str(type(spaces_data))),
                    html.Br(),
                    "This suggests an API configuration or authentication issue."
                ]
            alert_color = "red"
            alert_title = "API Error"
            space_selector_style = {"display": "none"}
            return "", container_style, True, [], space_selector_style, alert_msg, alert_color, alert_title, False
            
    except Exception as e:
        alert_msg = [
            "Error retrieving Genie spaces with OBO: ",
            dmc.Code(str(e)),
            html.Br(),
            html.Br(),
            "This could be due to:",
            html.Br(),
            "• Network connectivity issues",
            html.Br(),
            "• Invalid or expired OBO token",
            html.Br(),
            "• Genie API endpoint not accessible with your credentials"
        ]
        alert_color = "red"
        alert_title = "Connection Error"
        space_selector_style = {"display": "none"}
        return "", container_style, True, [], space_selector_style, alert_msg, alert_color, alert_title, False


@callback(
    [
        Output("conversations-output-obo", "children"),
        Output("conversations-container-obo", "style"),
        Output("conversation-selector-obo", "data"),
        Output("conversation-selector-obo", "style"),
        Output("list-messages-obo", "disabled"),
        Output("alert-genie-obo", "children", allow_duplicate=True),
        Output("alert-genie-obo", "color", allow_duplicate=True),
        Output("alert-genie-obo", "title", allow_duplicate=True),
    ],
    Input("list-conversations-obo", "n_clicks"),
    State("space-selector-obo", "value"),
    prevent_initial_call=True,
)
def list_conversations_obo_callback(n_clicks, selected_space_id):
    """List conversations in a space using On-Behalf-Of (OBO) credentials"""
    if not n_clicks:
        return dash.no_update
    
    if not selected_space_id:
        alert_msg = "Please select a space first."
        alert_color = "yellow"
        alert_title = "No Space Selected"
        return "", {"display": "none"}, alert_msg, alert_color, alert_title
    
    container_style = {"display": "none"}
    
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
            
        # Get space details to find the name
        spaces_data = get_genie_spaces_obo(user_token)
        space_name = "Unknown Space"
        if spaces_data and 'spaces' in spaces_data:
            for space in spaces_data['spaces']:
                space_id = space.get('id') or space.get('space_id') or space.get('_id') or space.get('genie_space_id')
                if space_id == selected_space_id:
                    space_name = space.get('title', 'Unknown Space')
                    break
        
        conv_data = get_genie_conversations_obo(selected_space_id, user_token)
        if conv_data and 'conversations' in conv_data:
            conversations_list = create_genie_list(conv_data['conversations'], 'title', 'id')
            
            # Create dropdown options for conversations
            conversation_options = [{"label": conv.get('title', 'Unknown Conversation'), "value": conv.get('id') or conv.get('conversation_id') or conv.get('_id') or conv.get('genie_conversation_id')} for conv in conv_data['conversations']]
            conversation_selector_style = {"display": "block"}
            messages_disabled = len(conv_data['conversations']) == 0
            
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
            return conversations_list, container_style, conversation_options, conversation_selector_style, messages_disabled, alert_msg, alert_color, alert_title
        else:
            alert_msg = f"No conversations found in space {space_name} with OBO authorization."
            alert_color = "yellow"
            alert_title = "No Conversations"
            conversation_selector_style = {"display": "none"}
            return "", container_style, [], conversation_selector_style, True, alert_msg, alert_color, alert_title
    except Exception as e:
        alert_msg = ["Error retrieving conversations with OBO: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "Error"
        return "", container_style, alert_msg, alert_color, alert_title
