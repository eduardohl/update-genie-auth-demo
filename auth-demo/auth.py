from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from flask import request
import requests
import json

cfg = Config()
w = WorkspaceClient()

# DEBUG: Print configuration details at module load
print("=" * 50)
print("DEBUG: Auth module loaded")
print(f"DEBUG: cfg.host = {cfg.host}")
print(f"DEBUG: cfg.client_id exists = {bool(getattr(cfg, 'client_id', None))}")
print(f"DEBUG: cfg.client_secret exists = {bool(getattr(cfg, 'client_secret', None))}")
print(f"DEBUG: WorkspaceClient initialized = {w is not None}")
print("=" * 50)


def fetch_sp_details():
    print("DEBUG: fetch_sp_details() called")
    local_sp_display_info = "Unknown"
    if w:
        try:
            print("DEBUG: Calling w.current_user.me()")
            me = w.current_user.me()
            print(f"DEBUG: current_user.me() response type: {type(me)}")
            print(f"DEBUG: hasattr service_principal_name: {hasattr(me, 'service_principal_name')}")
            print(f"DEBUG: hasattr user_name: {hasattr(me, 'user_name')}")
            
            if hasattr(me, "service_principal_name") and me.service_principal_name:
                local_sp_display_info = me.service_principal_name
                print(f"DEBUG: Using service_principal_name: {local_sp_display_info}")
            elif hasattr(me, "user_name") and me.user_name:
                local_sp_display_info = me.user_name
                print(f"DEBUG: Using user_name: {local_sp_display_info}")
            else:
                local_sp_display_info = "Unknown"
                print("DEBUG: No valid name found, using 'Unknown'")
        except Exception as e:
            local_sp_display_info = f"Error ({e})"
            print(f"ERROR: Exception in fetch_sp_details: {e}")
            print(f"ERROR: Exception type: {type(e)}")
    else:
        print("ERROR: WorkspaceClient (w) is None")
    
    print(f"DEBUG: fetch_sp_details() returning: {local_sp_display_info}")
    return local_sp_display_info


def get_user_token():
    print("DEBUG: get_user_token() called")
    try:
        headers = request.headers
        print(f"DEBUG: Request headers available: {list(headers.keys())}")
        
        # Check for OBO token
        token = headers.get("X-Forwarded-Access-Token")
        username = headers.get("X-Forwarded-Preferred-Username")
        
        print(f"DEBUG: X-Forwarded-Access-Token exists: {token is not None}")
        print(f"DEBUG: X-Forwarded-Preferred-Username: {username}")
        
        if token:
            print(f"DEBUG: Token length: {len(token)} characters")
            print(f"DEBUG: Token starts with: {token[:20]}..." if len(token) > 20 else f"DEBUG: Full token: {token}")
        else:
            print("DEBUG: No OBO token found in headers")
            
        return token
    except Exception as e:
        print(f"ERROR: Exception in get_user_token: {e}")
        print(f"ERROR: Exception type: {type(e)}")
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
    print("=" * 60)
    print("DEBUG: get_genie_spaces_sp() called")
    print(f"DEBUG: WorkspaceClient available: {w is not None}")
    print(f"DEBUG: API client available: {hasattr(w, 'api_client') if w else False}")
    
    try:
        print("DEBUG: Making SP request to /api/2.0/genie/spaces")
        print(f"DEBUG: Using host: {cfg.host}")
        
        response = w.api_client.do("GET", "/api/2.0/genie/spaces")
        
        print(f"DEBUG: SP response received")
        print(f"DEBUG: Response type: {type(response)}")
        print(f"DEBUG: Response content: {response}")
        
        # Check if response has 'spaces' key
        if isinstance(response, dict):
            print(f"DEBUG: Response is dict with keys: {list(response.keys())}")
            if 'spaces' in response:
                spaces = response['spaces']
                print(f"DEBUG: Found {len(spaces)} spaces")
                for i, space in enumerate(spaces):
                    print(f"DEBUG: Space {i}: {space.get('title', 'No title')} (ID: {space.get('id', 'No ID')})")
            else:
                print("WARNING: No 'spaces' key in response")
        else:
            print(f"WARNING: Response is not a dict: {response}")
            
        print("=" * 60)
        return response
        
    except Exception as e:
        print(f"ERROR: Exception in get_genie_spaces_sp: {e}")
        print(f"ERROR: Exception type: {type(e)}")
        print(f"ERROR: Exception details: {str(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        print("=" * 60)
        return None


def get_genie_spaces_obo(user_token):
    """List Genie spaces using OBO token"""
    print("=" * 60)
    print("DEBUG: get_genie_spaces_obo() called")
    print(f"DEBUG: user_token provided: {user_token is not None}")
    
    if user_token:
        print(f"DEBUG: Token length: {len(user_token)} characters")
        print(f"DEBUG: Token starts with: {user_token[:20]}..." if len(user_token) > 20 else f"DEBUG: Full token: {user_token}")
    else:
        print("ERROR: No user_token provided to get_genie_spaces_obo")
        print("=" * 60)
        return None
        
    try:
        # Clean host URL construction
        print(f"DEBUG: Original cfg.host: '{cfg.host}'")
        host = cfg.host.strip()
        print(f"DEBUG: After strip: '{host}'")
        
        # Remove any protocol prefix and leading/trailing slashes
        host = host.replace('https://', '').replace('http://', '').strip('/')
        print(f"DEBUG: After protocol removal: '{host}'")
        
        url = f"https://{host}/api/2.0/genie/spaces"
        print(f"DEBUG: Final URL: {url}")
        
        headers = {"Authorization": f"Bearer {user_token[:20]}..."}  # Truncate for logging
        print(f"DEBUG: Request headers: {headers}")
        
        print("DEBUG: Making OBO request...")
        response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
        
        print(f"DEBUG: OBO Response status: {response.status_code}")
        print(f"DEBUG: Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"DEBUG: Response JSON type: {type(json_response)}")
                print(f"DEBUG: Response JSON content: {json_response}")
                
                if isinstance(json_response, dict) and 'spaces' in json_response:
                    spaces = json_response['spaces']
                    print(f"DEBUG: Found {len(spaces)} spaces in OBO response")
                    for i, space in enumerate(spaces):
                        print(f"DEBUG: OBO Space {i}: {space.get('title', 'No title')} (ID: {space.get('id', 'No ID')})")
                else:
                    print("WARNING: OBO response missing 'spaces' key or not a dict")
                    
                print("=" * 60)
                return json_response
                
            except json.JSONDecodeError as je:
                print(f"ERROR: Failed to parse JSON response: {je}")
                print(f"ERROR: Raw response text: {response.text}")
                print("=" * 60)
                return None
        else:
            print(f"ERROR: HTTP {response.status_code} - {response.text}")
            print(f"ERROR: Response headers: {dict(response.headers)}")
            print("=" * 60)
            return None
            
    except Exception as e:
        print(f"ERROR: Exception in get_genie_spaces_obo: {e}")
        print(f"ERROR: Exception type: {type(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        print("=" * 60)
        return None


def get_genie_conversations_sp(space_id):
    """List conversations in a space using Service Principal auth"""
    print("=" * 60)
    print("DEBUG: get_genie_conversations_sp() called")
    print(f"DEBUG: space_id: {space_id}")
    
    if not space_id:
        print("ERROR: No space_id provided")
        print("=" * 60)
        return None
        
    try:
        endpoint = f"/api/2.0/genie/spaces/{space_id}/conversations"
        print(f"DEBUG: Making SP conversations request to {endpoint}")
        print(f"DEBUG: Using host: {cfg.host}")
        
        response = w.api_client.do("GET", endpoint)
        
        print(f"DEBUG: SP conversations response received")
        print(f"DEBUG: Response type: {type(response)}")
        print(f"DEBUG: Response content: {response}")
        
        # Check if response has 'conversations' key
        if isinstance(response, dict):
            print(f"DEBUG: Response is dict with keys: {list(response.keys())}")
            if 'conversations' in response:
                conversations = response['conversations']
                print(f"DEBUG: Found {len(conversations)} conversations")
                for i, conv in enumerate(conversations):
                    print(f"DEBUG: Conversation {i}: {conv.get('title', 'No title')} (ID: {conv.get('id', 'No ID')})")
            else:
                print("WARNING: No 'conversations' key in response")
        else:
            print(f"WARNING: Response is not a dict: {response}")
            
        print("=" * 60)
        return response
        
    except Exception as e:
        print(f"ERROR: Exception in get_genie_conversations_sp: {e}")
        print(f"ERROR: Exception type: {type(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        print("=" * 60)
        return None


def get_genie_conversations_obo(space_id, user_token):
    """List conversations in a space using OBO token"""
    print("=" * 60)
    print("DEBUG: get_genie_conversations_obo() called")
    print(f"DEBUG: space_id: {space_id}")
    print(f"DEBUG: user_token provided: {user_token is not None}")
    
    if not space_id:
        print("ERROR: No space_id provided")
        print("=" * 60)
        return None
        
    if not user_token:
        print("ERROR: No user_token provided")
        print("=" * 60)
        return None
        
    try:
        # Clean host URL construction
        print(f"DEBUG: Original cfg.host: '{cfg.host}'")
        host = cfg.host.strip()
        host = host.replace('https://', '').replace('http://', '').strip('/')
        print(f"DEBUG: Cleaned host: '{host}'")
        
        url = f"https://{host}/api/2.0/genie/spaces/{space_id}/conversations"
        print(f"DEBUG: Final URL: {url}")
        
        headers = {"Authorization": f"Bearer {user_token[:20]}..."}  # Truncate for logging
        print(f"DEBUG: Request headers: {headers}")
        
        print("DEBUG: Making OBO conversations request...")
        response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
        
        print(f"DEBUG: OBO conversations response status: {response.status_code}")
        print(f"DEBUG: Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"DEBUG: Response JSON type: {type(json_response)}")
                print(f"DEBUG: Response JSON content: {json_response}")
                
                if isinstance(json_response, dict) and 'conversations' in json_response:
                    conversations = json_response['conversations']
                    print(f"DEBUG: Found {len(conversations)} conversations in OBO response")
                    for i, conv in enumerate(conversations):
                        print(f"DEBUG: OBO Conversation {i}: {conv.get('title', 'No title')} (ID: {conv.get('id', 'No ID')})")
                else:
                    print("WARNING: OBO conversations response missing 'conversations' key or not a dict")
                    
                print("=" * 60)
                return json_response
                
            except json.JSONDecodeError as je:
                print(f"ERROR: Failed to parse JSON response: {je}")
                print(f"ERROR: Raw response text: {response.text}")
                print("=" * 60)
                return None
        else:
            print(f"ERROR: HTTP {response.status_code} - {response.text}")
            print(f"ERROR: Response headers: {dict(response.headers)}")
            print("=" * 60)
            return None
            
    except Exception as e:
        print(f"ERROR: Exception in get_genie_conversations_obo: {e}")
        print(f"ERROR: Exception type: {type(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        print("=" * 60)
        return None
