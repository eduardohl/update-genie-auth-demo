# OBO (On-Behalf-Of) User Passthrough for Genie API

This document explains how the user passthrough mechanism works in the Databricks App demo, specifically for accessing the Genie API using the requesting user's identity instead of the app's service principal credentials.

## Overview

The OBO mechanism allows the Databricks App to make API calls on behalf of the authenticated user, preserving their identity and permissions. This is crucial for maintaining proper access control and audit trails.

## How It Works

### 1. Token Retrieval

The app extracts the user's JWT token from the `X-Forwarded-Access-Token` HTTP header that Databricks automatically provides.

**File:** `auth.py`  
**Function:** `get_user_token()` (lines 42-52)

```python
def get_user_token():
    try:
        headers = request.headers
        # Check for OBO token
        token = headers.get("X-Forwarded-Access-Token")
        return token
    except Exception as e:
        print(f"ERROR: Exception in get_user_token: {e}")
        return None
```

**File:** `callbacks/auth_callbacks.py`  
**Function:** `update_header_and_warehouses()` (lines 60-62)

```python
headers = dict(request.headers)
username = headers.get("X-Forwarded-Preferred-Username")
obo_token = headers.get("X-Forwarded-Access-Token")
```

### 2. Token Storage and Validation

The JWT token is stored in a Dash Store component and decoded to extract user information and scopes.

**File:** `callbacks/auth_callbacks.py`  
**Function:** `update_header_and_warehouses()` (lines 75-95)

```python
# Store the raw JWT
jwt_raw = obo_token

# Decode without verification (since we don't have the public key)
decoded_token = jwt.decode(obo_token, options={"verify_signature": False})
jwt_decoded = json.dumps(decoded_token, indent=2)

# Parse scopes
scopes = decoded_token.get("scope", "").split()
```

### 3. Genie API Calls with OBO

When making Genie API calls, the app uses the user's token in the Authorization header instead of the service principal credentials.

**File:** `auth.py`  
**Function:** `get_genie_spaces_obo()` (lines 100-130)

```python
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
        
        # Use user's token in Authorization header
        response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
        
        if response.status_code == 200:
            json_response = response.json()
            return json_response
        else:
            print(f"ERROR: Genie spaces OBO request failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR: Failed to get Genie spaces with OBO: {e}")
        return None
```

**File:** `auth.py`  
**Function:** `get_genie_conversations_obo()` (lines 150-190)

```python
def get_genie_conversations_obo(space_id, user_token):
    """List conversations in a space using OBO token"""
    if not user_token:
        print("ERROR: No OBO token provided")
        return None
        
    try:
        # Clean host URL construction
        host = cfg.host.strip()
        host = host.replace('https://', '').replace('http://', '').strip('/')
        url = f"https://{host}/api/2.0/genie/spaces/{space_id}/conversations"
        
        # Use user's token in Authorization header
        response = requests.get(url, headers={"Authorization": f"Bearer {user_token}"})
        
        if response.status_code == 200:
            json_response = response.json()
            return json_response
        else:
            print(f"ERROR: Genie conversations OBO request failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR: Failed to get conversations with OBO: {e}")
        return None
```

## Key Components

### HTTP Headers
- **`X-Forwarded-Access-Token`**: Contains the user's JWT token
- **`X-Forwarded-Preferred-Username`**: Contains the user's username

### Authentication Flow
1. **User Access**: User accesses the Databricks App
2. **Token Forwarding**: Databricks forwards the user's JWT token in headers
3. **Token Extraction**: App extracts token from `X-Forwarded-Access-Token`
4. **Token Validation**: App decodes JWT to verify structure and extract scopes
5. **API Calls**: App uses user's token in `Authorization: Bearer {token}` header
6. **Identity Preservation**: Genie API sees the request as coming from the user, not the app

## Implementation Notes

- The app uses the `requests` library for direct HTTP calls to Genie API
- JWT tokens are decoded without signature verification (demo purposes)
- Error handling includes HTTP status code checking and JSON parsing
- The UI dynamically enables/disables OBO functionality based on token availability
- All OBO calls include proper error handling and user feedback

## File Locations Summary

| Component | File | Lines |
|-----------|------|-------|
| Token Retrieval | `auth.py` | 42-52 |
| Token Storage | `callbacks/auth_callbacks.py` | 60-95 |
| Genie Spaces OBO | `auth.py` | 100-130 |
| Genie Conversations OBO | `auth.py` | 150-190 |
| UI Callbacks | `callbacks/genie_callbacks.py` | 200-300 |
