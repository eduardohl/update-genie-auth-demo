from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from flask import request
import requests
import json

cfg = Config()
w = WorkspaceClient()

# Basic configuration validation
if not cfg.host:
    print("WARNING: No Databricks host configured")
if not w:
    print("WARNING: WorkspaceClient not initialized")


def fetch_sp_details():
    local_sp_display_info = "Unknown"
    if w:
        try:
            me = w.current_user.me()
            
            if hasattr(me, "service_principal_name") and me.service_principal_name:
                local_sp_display_info = me.service_principal_name
            elif hasattr(me, "user_name") and me.user_name:
                local_sp_display_info = me.user_name
            else:
                local_sp_display_info = "Unknown"
        except Exception as e:
            local_sp_display_info = f"Error ({e})"
            print(f"ERROR: Exception in fetch_sp_details: {e}")
    else:
        print("ERROR: WorkspaceClient (w) is None")
    
    return local_sp_display_info


def get_user_token():
    try:
        headers = request.headers
        
        # Check for OBO token
        token = headers.get("X-Forwarded-Access-Token")
        
        if not token:
            print("INFO: No OBO token found in request headers")
            
        return token
    except Exception as e:
        print(f"ERROR: Exception in get_user_token: {e}")
        return None


def get_connection_sp(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )


def get_connection_obo(http_path, user_token):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        access_token=user_token,
    )


def get_genie_spaces_sp():
    """List Genie spaces using Service Principal auth"""
    try:
        response = w.api_client.do("GET", "/api/2.0/genie/spaces")
        
        # Check if response has 'spaces' key
        if isinstance(response, dict):
            if len(response) == 0:
                print("WARNING: SP received empty response - check Service Principal permissions for Genie spaces")
            elif 'spaces' in response:
                spaces = response['spaces']
                print(f"INFO: Found {len(spaces)} Genie spaces using Service Principal")
            else:
                print(f"WARNING: Unexpected response structure from Genie spaces API: {list(response.keys())}")
        else:
            print(f"WARNING: Unexpected response type from Genie spaces API: {type(response)}")
            
        return response
        
    except Exception as e:
        print(f"ERROR: Failed to get Genie spaces with Service Principal: {e}")
        return None


def get_genie_spaces_obo(user_token):
    """List Genie spaces using OBO token"""
    if not user_token:
        print("ERROR: No OBO token provided")
        return None
        
    try:
        # Clean host URL construction
        host = cfg.host.strip()
        host = host.replace('https://', '').replace('http://', '').strip('/')
        url = f"https://{host}/api/2.0/genie/spaces"
        
        response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                
                if isinstance(json_response, dict) and 'spaces' in json_response:
                    spaces = json_response['spaces']
                    print(f"INFO: Found {len(spaces)} Genie spaces using OBO")
                else:
                    print("WARNING: OBO response missing 'spaces' key or not a dict")
                    
                return json_response
                
            except json.JSONDecodeError as je:
                print(f"ERROR: Failed to parse JSON response: {je}")
                return None
        else:
            print(f"ERROR: Genie spaces OBO request failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR: Failed to get Genie spaces with OBO: {e}")
        return None


def get_genie_conversations_sp(space_id):
    """List conversations in a space using Service Principal auth"""
    if not space_id:
        print("ERROR: No space_id provided")
        return None
        
    try:
        endpoint = f"/api/2.0/genie/spaces/{space_id}/conversations"
        response = w.api_client.do("GET", endpoint)
        
        # Check if response has 'conversations' key
        if isinstance(response, dict):
            if 'conversations' in response:
                conversations = response['conversations']
                print(f"INFO: Found {len(conversations)} conversations in space {space_id} using Service Principal")
            else:
                print("WARNING: No 'conversations' key in response")
        else:
            print(f"WARNING: Unexpected response type from conversations API: {type(response)}")
            
        return response
        
    except Exception as e:
        print(f"ERROR: Failed to get conversations with Service Principal: {e}")
        return None


def get_genie_conversations_obo(space_id, user_token):
    """List conversations in a space using OBO token"""
    if not space_id:
        print("ERROR: No space_id provided")
        return None
        
    if not user_token:
        print("ERROR: No OBO token provided")
        return None
        
    try:
        # Clean host URL construction
        host = cfg.host.strip()
        host = host.replace('https://', '').replace('http://', '').strip('/')
        url = f"https://{host}/api/2.0/genie/spaces/{space_id}/conversations"
        
        response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                
                if isinstance(json_response, dict) and 'conversations' in json_response:
                    conversations = json_response['conversations']
                    print(f"INFO: Found {len(conversations)} conversations in space {space_id} using OBO")
                else:
                    print("WARNING: OBO conversations response missing 'conversations' key or not a dict")
                    
                return json_response
                
            except json.JSONDecodeError as je:
                print(f"ERROR: Failed to parse JSON response: {je}")
                return None
        else:
            print(f"ERROR: Genie conversations OBO request failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR: Failed to get conversations with OBO: {e}")
        return None


def get_genie_messages_sp(space_id, conversation_id):
    """List messages in a conversation using Service Principal auth"""
    if not space_id:
        print("ERROR: No space_id provided")
        return None
        
    if not conversation_id:
        print("ERROR: No conversation_id provided")
        return None
        
    try:
        # Try multiple API patterns for listing messages
        
        # Pattern 1: Standard messages endpoint (what we were trying)
        try:
            endpoint = f"/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages"
            response = w.api_client.do("GET", endpoint)
            
            if isinstance(response, dict) and 'messages' in response:
                messages = response['messages']
                print(f"INFO: Found {len(messages)} messages using standard endpoint")
                return response
            else:
                print("INFO: Standard messages endpoint didn't return expected format")
        except Exception as e:
            print(f"INFO: Standard messages endpoint failed: {e}")
        
        # Pattern 2: Try with query parameters for pagination/listing
        try:
            endpoint = f"/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages?limit=100"
            response = w.api_client.do("GET", endpoint)
            
            if isinstance(response, dict) and 'messages' in response:
                messages = response['messages']
                print(f"INFO: Found {len(messages)} messages using pagination endpoint")
                return response
            else:
                print("INFO: Pagination endpoint didn't return expected format")
        except Exception as e:
            print(f"INFO: Pagination endpoint failed: {e}")
        
        # Pattern 3: Try conversation details endpoint (might include messages)
        try:
            endpoint = f"/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}"
            response = w.api_client.do("GET", endpoint)
            
            if isinstance(response, dict):
                if 'messages' in response:
                    messages = response['messages']
                    print(f"INFO: Found {len(messages)} messages in conversation details")
                    return response
                elif 'message_count' in response:
                    print(f"INFO: Conversation has {response['message_count']} messages but no message list")
                    # Return a structure indicating we found message count but no list
                    return {
                        'messages': [],
                        'message_count': response['message_count'],
                        'note': 'Message count available but individual messages not accessible via this endpoint'
                    }
                else:
                    print("INFO: Conversation details endpoint didn't include messages")
            else:
                print("INFO: Conversation details endpoint didn't return expected format")
        except Exception as e:
            print(f"INFO: Conversation details endpoint failed: {e}")
        
        # Pattern 4: Try alternative messages endpoint structure
        try:
            endpoint = f"/api/2.0/genie/conversations/{conversation_id}/messages"
            response = w.api_client.do("GET", endpoint)
            
            if isinstance(response, dict) and 'messages' in response:
                messages = response['messages']
                print(f"INFO: Found {len(messages)} messages using alternative endpoint")
                return response
            else:
                print("INFO: Alternative messages endpoint didn't return expected format")
        except Exception as e:
            print(f"INFO: Alternative messages endpoint failed: {e}")
        
        # If all patterns fail, return None
        print("WARNING: All message listing patterns failed - messages endpoint may not be available")
        return None
        
    except Exception as e:
        print(f"ERROR: Failed to get messages with Service Principal: {e}")
        return None


def get_genie_messages_obo(space_id, conversation_id, user_token):
    """List messages in a conversation using OBO token"""
    if not space_id:
        print("ERROR: No space_id provided")
        return None
        
    if not conversation_id:
        print("ERROR: No conversation_id provided")
        return None
        
    if not user_token:
        print("ERROR: No OBO token provided")
        return None
        
    try:
        # Clean host URL construction
        host = cfg.host.strip()
        host = host.replace('https://', '').replace('http://', '').strip('/')
        
        # Try multiple API patterns for listing messages
        
        # Pattern 1: Standard messages endpoint (what we were trying)
        try:
            url = f"https://{host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages"
            response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
            
            if response.status_code == 200:
                json_response = response.json()
                if isinstance(json_response, dict) and 'messages' in json_response:
                    messages = json_response['messages']
                    print(f"INFO: Found {len(messages)} messages using standard endpoint")
                    return json_response
                else:
                    print("INFO: Standard messages endpoint didn't return expected format")
            else:
                print(f"INFO: Standard messages endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"INFO: Standard messages endpoint failed: {e}")
        
        # Pattern 2: Try with query parameters for pagination/listing
        try:
            url = f"https://{host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages?limit=100"
            response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
            
            if response.status_code == 200:
                json_response = response.json()
                if isinstance(json_response, dict) and 'messages' in json_response:
                    messages = json_response['messages']
                    print(f"INFO: Found {len(messages)} messages using pagination endpoint")
                    return json_response
                else:
                    print("INFO: Pagination endpoint didn't return expected format")
            else:
                print(f"INFO: Pagination endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"INFO: Pagination endpoint failed: {e}")
        
        # Pattern 3: Try conversation details endpoint (might include messages)
        try:
            url = f"https://{host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}"
            response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
            
            if response.status_code == 200:
                json_response = response.json()
                if isinstance(json_response, dict):
                    if 'messages' in json_response:
                        messages = json_response['messages']
                        print(f"INFO: Found {len(messages)} messages in conversation details")
                        return json_response
                    elif 'message_count' in json_response:
                        print(f"INFO: Conversation has {json_response['message_count']} messages but no message list")
                        # Return a structure indicating we found message count but no list
                        return {
                            'messages': [],
                            'message_count': json_response['message_count'],
                            'note': 'Message count available but individual messages not accessible via this endpoint'
                        }
                    else:
                        print("INFO: Conversation details endpoint didn't include messages")
                else:
                    print("INFO: Conversation details endpoint didn't return expected format")
            else:
                print(f"INFO: Conversation details endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"INFO: Conversation details endpoint failed: {e}")
        
        # Pattern 4: Try alternative messages endpoint structure
        try:
            url = f"https://{host}/api/2.0/genie/conversations/{conversation_id}/messages"
            response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
            
            if response.status_code == 200:
                json_response = response.json()
                if isinstance(json_response, dict) and 'messages' in json_response:
                    messages = json_response['messages']
                    print(f"INFO: Found {len(messages)} messages using alternative endpoint")
                    return json_response
                else:
                    print("INFO: Alternative messages endpoint didn't return expected format")
            else:
                print(f"INFO: Alternative messages endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"INFO: Alternative messages endpoint failed: {e}")
        
        # If all patterns fail, return None
        print("WARNING: All message listing patterns failed - messages endpoint may not be available")
        return None
            
    except Exception as e:
        print(f"ERROR: Failed to get messages with OBO: {e}")
        return None
