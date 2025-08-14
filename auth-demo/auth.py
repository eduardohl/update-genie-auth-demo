from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from flask import request
import requests

cfg = Config()
w = WorkspaceClient()


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
            print(f"Error fetching SP details: {e}")
    return local_sp_display_info


def get_user_token():
    headers = request.headers
    token = headers.get("X-Forwarded-Access-Token")
    return token


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
    url = f"https://{cfg.host}/api/2.0/genie/spaces"
    headers = {"Authorization": f"Bearer {cfg.authenticate().token}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


def get_genie_spaces_obo(user_token):
    """List Genie spaces using OBO token"""
    url = f"https://{cfg.host}/api/2.0/genie/spaces"
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


def get_genie_conversations_sp(space_id):
    """List conversations in a space using Service Principal auth"""
    url = f"https://{cfg.host}/api/2.0/genie/spaces/{space_id}/conversations"
    headers = {"Authorization": f"Bearer {cfg.authenticate().token}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


def get_genie_conversations_obo(space_id, user_token):
    """List conversations in a space using OBO token"""
    url = f"https://{cfg.host}/api/2.0/genie/spaces/{space_id}/conversations"
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
