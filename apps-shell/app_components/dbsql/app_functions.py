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


def get_warehouse_id():
    """Get the SQL warehouse ID from the app.yaml configuration."""
    config = load_config()
    return config.get("DATABRICKS_SQL_WAREHOUSE_ID", "")


def get_client():
    """Create and return a Databricks SDK client using credentials from config."""
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
        # Create and test the client
        client = WorkspaceClient(host=host, token=token)
        try:
            client.current_user.me()  # Test connection
            return client
        except Exception as e:
            print(f"Connection test failed: {e}")
            return None
            
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return None


def get_dbsql_status():
    """
    Check the status of the SQL warehouse defined in app.yaml.
    
    Returns:
        dict: Status information about the SQL warehouse.
    """
    # Get the warehouse ID from configuration
    warehouse_id = get_warehouse_id()
    
    if not warehouse_id:
        return {
            "status": "not_configured",
            "message": "SQL Warehouse ID not configured in app.yaml",
            "color": "not_configured"
        }
    
    # Initialize the Databricks SDK client
    client = get_client()
    
    if not client:
        return {
            "status": "config_error",
            "message": "Failed to connect to Databricks. Check credentials.",
            "color": "not_configured"
        }
    
    try:
        # Retrieve warehouse information using the SDK
        warehouse = client.warehouses.get(id=warehouse_id)
        
        if not warehouse:
            return {
                "status": "not_found",
                "message": f"SQL warehouse with ID {warehouse_id} not found",
                "color": "not_configured"
            }
        
        # Warehouse exists, extract the state
        state = warehouse.state
        
        # Convert state to string for comparison (state is an enum/object)
        state_str = str(state) if state else "UNKNOWN"
        
        # Extract the actual state name (remove 'State.' prefix if present)
        if state_str.startswith("State."):
            state_name = state_str[6:]  # Remove 'State.' prefix
        else:
            state_name = state_str
        
        # Map the warehouse state to a user-friendly status
        status_map = {
            "running": {
                "status": "running",
                "message": "SQL Warehouse ready",
                "color": "running"
            },
            "starting": {
                "status": "starting",
                "message": "SQL Warehouse is starting...",
                "color": "starting"
            },
            "stopping": {
                "status": "stopping",
                "message": "SQL Warehouse is stopping...",
                "color": "stopping"
            },
            "stopped": {
                "status": "stopped",
                "message": "SQL Warehouse is stopped",
                "color": "stopped"
            }
        }
        
        # Get the status from the map, or use a default
        default_status = {
            "status": state_name.lower(),
            "message": f"SQL Warehouse state: {state_name}",
            "color": "unknown"
        }
        
        return status_map.get(state_name.lower(), default_status)
        
    except Exception as e:
        print(f"Error checking warehouse status: {e}")
        return {
            "status": "error",
            "message": f"Error getting warehouse status: {str(e)}",
            "color": "error"
        }


def start_warehouse(warehouse_id):
    """
    Start a stopped SQL warehouse.
    
    Args:
        warehouse_id (str): The ID of the warehouse to start.
        
    Returns:
        bool: True if the warehouse was started successfully, False otherwise.
    """
    if not warehouse_id:
        return False
    
    client = get_client()
    if not client:
        return False
    
    try:
        # Start the warehouse
        client.warehouses.start(id=warehouse_id)
        return True
    except Exception as e:
        print(f"Failed to start warehouse: {e}")
        return False


def run_sql_query(query):
    """
    Run a SQL query against the configured Databricks SQL warehouse.
    
    Args:
        query (str): The SQL query to run.
        
    Returns:
        dict: Results and status information about the query execution.
    """
    if not query or not query.strip():
        return {
            "status": "error",
            "message": "Query must be provided",
            "results": None
        }
    
    # Get warehouse ID from config
    warehouse_id = get_warehouse_id()
    if not warehouse_id:
        return {
            "status": "error",
            "message": "No SQL Warehouse ID configured in app.yaml",
            "results": None
        }
    
    # Get Databricks client
    client = get_client()
    if not client:
        return {
            "status": "error",
            "message": "Cannot connect to Databricks. Check credentials.",
            "results": None
        }
    
    try:
        # First check if warehouse is available
        warehouse_status = get_dbsql_status()
        
        if warehouse_status.get("status") == "stopped":
            # Try to start the warehouse if it's stopped
            start_success = start_warehouse(warehouse_id)
            if not start_success:
                return {
                    "status": "error",
                    "message": "Could not start the stopped SQL warehouse",
                    "results": None
                }
        elif warehouse_status.get("status") not in ["running", "starting"]:
            return {
                "status": "error",
                "message": "SQL Warehouse is not available",
                "results": None
            }
        
        try:
            # Execute the SQL statement
            statement = client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=query
            )
            
            # Get the execution state as a string
            state_obj = statement.status.state
            state_str = str(state_obj) if state_obj else "UNKNOWN"
            
            # Extract actual state name by removing any prefix
            if state_str.startswith("StatementState."):
                state_name = state_str[15:]  # Remove 'StatementState.' prefix
            elif "." in state_str:
                state_name = state_str.split(".", 1)[1]  # Get part after dot
            else:
                state_name = state_str
                
            # Process based on execution status
            if state_name == "SUCCEEDED":
                # Check if there are results to return (e.g., SELECT query)
                has_result_data = (
                    statement.result and 
                    hasattr(statement.result, 'data_array') and
                    statement.result.data_array
                )
                
                if has_result_data:
                    # Extract column names from schema
                    columns = []
                    if (hasattr(statement, 'manifest') and 
                            statement.manifest and 
                            hasattr(statement.manifest, 'schema') and 
                            statement.manifest.schema and
                            hasattr(statement.manifest.schema, 'columns')):
                        columns = [
                            col.name 
                            for col in statement.manifest.schema.columns
                        ]
                    else:
                        # Fallback if schema is not available
                        if statement.result.data_array:
                            first_row = statement.result.data_array[0]
                            columns = [
                                f"Column{i}" 
                                for i in range(len(first_row))
                            ]
                    
                    # Convert rows to dictionaries (limit to 10 rows)
                    results = []
                    display_rows = statement.result.data_array[:10]
                    
                    for row in display_rows:
                        row_dict = {}
                        for i, value in enumerate(row):
                            if i < len(columns):
                                row_dict[columns[i]] = value
                            else:
                                row_dict[f"Column{i}"] = value
                        results.append(row_dict)
                    
                    data_rows = len(statement.result.data_array)
                    return {
                        "status": "success",
                        "message": (
                            f"Query executed successfully ({data_rows} rows)"
                        ),
                        "results": results
                    }
                else:
                    # Handle non-SELECT queries (INSERT, UPDATE, etc.)
                    affected_rows = 0
                    if (statement.result and 
                            hasattr(statement.result, 'row_count')):
                        affected_rows = statement.result.row_count
                    
                    return {
                        "status": "success",
                        "message": (
                            f"Query completed. Affected {affected_rows} rows."
                        ),
                        "results": [],
                        "affected_rows": affected_rows
                    }
            elif state_name == "FAILED":
                # Handle query execution failures
                error_message = "Query failed with unknown error"
                
                if hasattr(statement.status, 'error') and statement.status.error:
                    error_message = statement.status.error.message
                elif hasattr(statement, 'error') and statement.error:
                    error_message = statement.error.message
                
                return {
                    "status": "error",
                    "message": f"Query failed: {error_message}",
                    "results": None
                }
            else:
                # Handle other states (rare)
                return {
                    "status": "incomplete",
                    "message": f"Query in unexpected state: {state_name}",
                    "results": None
                }
                
        except Exception as query_error:
            return {
                "status": "error",
                "message": f"Error executing query: {str(query_error)}",
                "results": None
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing query: {str(e)}",
            "results": None
        } 