from databricks.sdk import WorkspaceClient
import yaml


def load_config():
    """Load configuration from app.yaml file."""
    try:
        with open('app.yaml', 'r') as file:
            yaml_content = yaml.safe_load(file)
            if 'env_variables' in yaml_content:
                return yaml_content['env_variables']
            return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


def get_genie_space_id():
    """Get the Genie Space ID from the app.yaml configuration."""
    config = load_config()
    return config.get("DATABRICKS_GENIE_SPACE_ID", "")


def get_client():
    """Create and return a Databricks SDK client."""
    # Load credentials from app.yaml
    config = load_config()
    host = config.get("DATABRICKS_HOST", "")
    token = config.get("DATABRICKS_TOKEN", "")
    
    if not host or not token:
        print("Error: Missing DATABRICKS_HOST or DATABRICKS_TOKEN "
              "in app.yaml")
        return None
        
    # Clean the host URL if needed
    if host.endswith("/"):
        host = host[:-1]
    
    try:
        # Create the client without testing the connection
        client = WorkspaceClient(host=host, token=token)
        return client
    except Exception as e:
        print(f"Failed to create client: {e}")
        return None


def get_genie_status():
    """Check if Genie is properly configured and available."""
    config = load_config()
    host = config.get("DATABRICKS_HOST", "")
    token = config.get("DATABRICKS_TOKEN", "")
    space_id = config.get("DATABRICKS_GENIE_SPACE_ID", "")
    
    status = {
        "is_configured": bool(host and token and space_id),
        "status": "unconfigured",
        "details": [],
        "debug_info": {}
    }

    if not host or not token:
        status["details"].append("Missing DATABRICKS_HOST or DATABRICKS_TOKEN")
        status["debug_info"]["host_configured"] = bool(host)
        status["debug_info"]["token_configured"] = bool(token)
        return status
        
    if not space_id:
        status["details"].append("Missing DATABRICKS_GENIE_SPACE_ID")
        status["debug_info"]["space_id_configured"] = False
        return status
    
    # Try to connect to Databricks
    client = get_client()
    if not client:
        status["status"] = "connection_error"
        status["details"].append("Could not create Databricks client")
        return status

    # Try to test the connection and Genie API
    try:
        # First, test the basic connection
        try:
            # Test the connection
            client.current_user.me()
        except Exception as e:
            status["status"] = "connection_error"
            status["details"].append(f"Connection failed: {str(e)}")
            status["debug_info"]["connection_error"] = str(e)
            return status
            
        # Check if the Genie API exists by attempting to access it
        try:
            # Just try to see if the genie attribute exists
            # This will raise an AttributeError if genie isn't available
            hasattr(client, "genie")
            
            # Try to access the space ID we have configured
            status["status"] = "available"
            status["details"].append(
                "Databricks connection successful, Genie space configured"
            )
            status["debug_info"]["space_info"] = {
                "id": space_id
            }
        except Exception as e:
            status["status"] = "api_error"
            status["details"].append(f"Error accessing Genie API: {str(e)}")
            status["debug_info"]["api_error"] = str(e)
            
    except Exception as e:
        status["status"] = "error"
        status["details"].append(f"Error: {str(e)}")
        status["debug_info"]["error"] = str(e)
        
    return status


def ask_genie_question(question, space_id=None):
    """Ask a question to Genie and return the response."""
    if not question:
        return {"error": "No question provided"}
        
    client = get_client()
    if not client:
        return {"error": "Could not connect to Databricks"}
    
    # If no space_id provided, get from config
    if not space_id:
        space_id = get_genie_space_id()
        if not space_id:
            return {"error": "No Genie Space ID provided or configured"}
    
    try:
        # Call the Genie API to ask a question
        response = client.genie.ask(
            space_id=space_id,
            question=question
        )
        
        return {
            "success": True,
            "question": question,
            "response": response
        }
        
    except AttributeError as e:
        # Handle the case where the Genie API doesn't exist or doesn't have the ask method
        error_message = f"Genie API not available: {str(e)}"
        return {
            "success": False,
            "error": error_message,
            "question": question
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error asking Genie: {str(e)}",
            "question": question
        } 