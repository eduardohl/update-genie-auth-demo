import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html

from auth import get_genie_messages_sp, get_genie_messages_obo, get_genie_spaces_sp, get_genie_spaces_obo, get_user_token
from utils import create_genie_messages_list


@callback(
    [
        Output("messages-output-sp", "children"),
        Output("messages-container-sp", "style"),
        Output("alert-genie-sp", "children", allow_duplicate=True),
        Output("alert-genie-sp", "color", allow_duplicate=True),
        Output("alert-genie-sp", "title", allow_duplicate=True),
    ],
    Input("list-messages-sp", "n_clicks"),
    State("space-selector-sp", "value"),
    State("conversation-selector-sp", "value"),
    prevent_initial_call=True,
)
def list_messages_sp_callback(n_clicks, selected_space_id, selected_conversation_id):
    """List messages in a conversation using Service Principal credentials"""
    if not n_clicks:
        return dash.no_update
    
    if not selected_space_id:
        alert_msg = "Please select a space first."
        alert_color = "yellow"
        alert_title = "No Space Selected"
        return "", {"display": "none"}, alert_msg, alert_color, alert_title
    
    if not selected_conversation_id:
        alert_msg = "Please select a conversation first."
        alert_color = "yellow"
        alert_title = "No Conversation Selected"
        return "", {"display": "none"}, alert_msg, alert_color, alert_title
    
    container_style = {"display": "none"}
    
    try:
        # Get space and conversation details to find the names
        spaces_data = get_genie_spaces_sp()
        space_name = "Unknown Space"
        conversation_name = "Unknown Conversation"
        
        if spaces_data and 'spaces' in spaces_data:
            for space in spaces_data['spaces']:
                space_id = space.get('id') or space.get('space_id') or space.get('_id') or space.get('genie_space_id')
                if space_id == selected_space_id:
                    space_name = space.get('title', 'Unknown Space')
                    # Get conversations to find conversation name
                    from auth import get_genie_conversations_sp
                    convs_data = get_genie_conversations_sp(selected_space_id)
                    if convs_data and 'conversations' in convs_data:
                        for conv in convs_data['conversations']:
                            conv_id = conv.get('id') or conv.get('conversation_id') or conv.get('_id') or conv.get('genie_conversation_id')
                            if conv_id == selected_conversation_id:
                                conversation_name = conv.get('title', 'Unknown Conversation')
                                break
                    break
        
        messages_data = get_genie_messages_sp(selected_space_id, selected_conversation_id)
        if messages_data and 'messages' in messages_data:
            messages_list = create_genie_messages_list(messages_data['messages'])
            alert_msg = [
                "Success! Found ",
                html.B(f"{len(messages_data['messages'])}"),
                " messages in conversation ",
                dmc.Code(conversation_name),
                " in space ",
                dmc.Code(space_name),
                " using Service Principal credentials.",
            ]
            alert_color = "green"
            alert_title = "Messages Retrieved"
            container_style = {"display": "block"}
            return messages_list, container_style, alert_msg, alert_color, alert_title
        else:
            alert_msg = f"No messages found in conversation {conversation_name} in space {space_name}."
            alert_color = "yellow"
            alert_title = "No Messages"
            return "", container_style, alert_msg, alert_color, alert_title
    except Exception as e:
        alert_msg = ["Error retrieving messages with Service Principal: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "Error"
        return "", container_style, alert_msg, alert_color, alert_title


@callback(
    [
        Output("messages-output-obo", "children"),
        Output("messages-container-obo", "style"),
        Output("alert-genie-obo", "children", allow_duplicate=True),
        Output("alert-genie-obo", "color", allow_duplicate=True),
        Output("alert-genie-obo", "title", allow_duplicate=True),
    ],
    Input("list-messages-obo", "n_clicks"),
    State("space-selector-obo", "value"),
    State("conversation-selector-obo", "value"),
    prevent_initial_call=True,
)
def list_messages_obo_callback(n_clicks, selected_space_id, selected_conversation_id):
    """List messages in a conversation using On-Behalf-Of (OBO) credentials"""
    if not n_clicks:
        return dash.no_update
    
    if not selected_space_id:
        alert_msg = "Please select a space first."
        alert_color = "yellow"
        alert_title = "No Space Selected"
        return "", {"display": "none"}, alert_msg, alert_color, alert_title
    
    if not selected_conversation_id:
        alert_msg = "Please select a conversation first."
        alert_color = "yellow"
        alert_title = "No Conversation Selected"
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
        
        # Get space and conversation details to find the names
        spaces_data = get_genie_spaces_obo(user_token)
        space_name = "Unknown Space"
        conversation_name = "Unknown Conversation"
        
        if spaces_data and 'spaces' in spaces_data:
            for space in spaces_data['spaces']:
                space_id = space.get('id') or space.get('space_id') or space.get('_id') or space.get('genie_space_id')
                if space_id == selected_space_id:
                    space_name = space.get('title', 'Unknown Space')
                    # Get conversations to find conversation name
                    from auth import get_genie_conversations_obo
                    convs_data = get_genie_conversations_obo(selected_space_id, user_token)
                    if convs_data and 'conversations' in convs_data:
                        for conv in convs_data['conversations']:
                            conv_id = conv.get('id') or conv.get('conversation_id') or conv.get('_id') or conv.get('genie_conversation_id')
                            if conv_id == selected_conversation_id:
                                conversation_name = conv.get('title', 'Unknown Conversation')
                                break
                    break
        
        messages_data = get_genie_messages_obo(selected_space_id, selected_conversation_id, user_token)
        if messages_data and 'messages' in messages_data:
            messages_list = create_genie_messages_list(messages_data['messages'])
            alert_msg = [
                "Success! Found ",
                html.B(f"{len(messages_data['messages'])}"),
                " messages in conversation ",
                dmc.Code(conversation_name),
                " in space ",
                dmc.Code(space_name),
                " using OBO authorization.",
            ]
            alert_color = "green"
            alert_title = "Messages Retrieved"
            container_style = {"display": "block"}
            return messages_list, container_style, alert_msg, alert_color, alert_title
        else:
            alert_msg = f"No messages found in conversation {conversation_name} in space {space_name} with OBO authorization."
            alert_color = "yellow"
            alert_title = "No Messages"
            return "", container_style, alert_msg, alert_color, alert_title
    except Exception as e:
        alert_msg = ["Error retrieving messages with OBO: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "Error"
        return "", container_style, alert_msg, alert_color, alert_title
