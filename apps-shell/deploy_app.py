    """
    App deployment script for Databricks App Hub.

    """

# #!/usr/bin/env python
# import os
# import sys
# import subprocess
# import yaml
# import time
# from databricks.sdk import WorkspaceClient
# from databricks.sdk.service.apps import (
#     AppResource, AppResourceSqlWarehouse, AppResourceSqlWarehouseSqlWarehousePermission,
#     AppResourceServingEndpoint, AppResourceServingEndpointServingEndpointPermission
# )

# def check_requirements():
#     """Check if all required tools are installed."""
#     print("Checking requirements...")
#     try:
#         # Check if gcloud is installed
#         subprocess.run(["gcloud", "--version"], 
#                        stdout=subprocess.PIPE, 
#                        stderr=subprocess.PIPE, 
#                        check=True)
#         print("✅ gcloud SDK found")
#     except (subprocess.CalledProcessError, FileNotFoundError):
#         print("❌ gcloud SDK not found. Please install it.")
#         sys.exit(1)
        
#     # Check for app.yaml
#     if not os.path.exists("app.yaml"):
#         print("❌ app.yaml not found. Please create it.")
#         sys.exit(1)
#     print("✅ app.yaml found")
    
#     # Check for required Python packages
#     try:
#         with open("requirements.txt", "r") as f:
#             requirements = f.read().splitlines()
#         print("✅ requirements.txt found")
#     except FileNotFoundError:
#         print("❌ requirements.txt not found.")
#         sys.exit(1)
        
#     print("All requirements checked!")

# def validate_yaml():
#     """Validate app.yaml configuration."""
#     print("\nValidating app.yaml configuration...")
    
#     try:
#         with open("app.yaml", "r") as f:
#             config = yaml.safe_load(f)
            
#         # Check for empty credentials
#         env_vars = config.get("env_variables", {})
#         if not env_vars.get("DATABRICKS_HOST") or not env_vars.get("DATABRICKS_TOKEN"):
#             print("⚠️  Warning: Databricks credentials are not set in app.yaml")
            
#         print("✅ app.yaml validation passed")
#         return True
#     except Exception as e:
#         print(f"❌ YAML validation failed: {str(e)}")
#         return False

# def deploy_app():
#     """Deploy the application."""
#     print("\nDeploying application...")
    
#     try:
#         # Load configuration from app.yaml
#         with open('app.yaml', 'r') as file:
#             config = yaml.safe_load(file)

#         # Extract necessary configuration
#         app_name = config.get('app_name')
#         sql_warehouse_id = config.get('DATABRICKS_SQL_WAREHOUSE_ID')
#         serving_endpoint_name = config.get('serving_endpoint_name')

#         # Initialize Databricks client
#         client = WorkspaceClient(
#             host=config.get('DATABRICKS_HOST'),
#             token=config.get('DATABRICKS_TOKEN')
#         )

#         # Check if the app already exists
#         existing_apps = [app.name for app in client.apps.list()]
#         if app_name in existing_apps:
#             print(f"App {app_name} already exists")
#             app = client.apps.get(app_name)
#             print(app.url)
#         else:
#             # Define resources
#             resources = []

#             # Add SQL Warehouse resource
#             sql_resource = AppResource(
#                 name="sql_warehouse",
#                 sql_warehouse=AppResourceSqlWarehouse(
#                     id=sql_warehouse_id,
#                     permission=AppResourceSqlWarehouseSqlWarehousePermission.CAN_USE
#                 )
#             )
#             resources.append(sql_resource)

#             # Add Serving Endpoint resource if specified
#             if serving_endpoint_name:
#                 serving_endpoint = AppResource(
#                     name="serving_endpoint",
#                     serving_endpoint=AppResourceServingEndpoint(
#                         name=serving_endpoint_name,
#                         permission=AppResourceServingEndpointServingEndpointPermission.CAN_QUERY
#                     )
#                 )
#                 resources.append(serving_endpoint)

#             # Create and deploy the app
#             print(f"Creating Lakehouse App with name {app_name}, this step will require a few minutes to complete")
#             app_created = client.apps.create_and_wait(
#                 name=app_name,
#                 resources=resources
#             )
#             app_deploy = client.apps.deploy_and_wait(
#                 app_name=app_name,
#                 source_code_path='path/to/source'
#             )

#             print(app_deploy.status.message)
#             print(app_created.url)

#         return True
#     except Exception as e:
#         print(f"❌ Deployment failed: {str(e)}")
#         return False

# if __name__ == "__main__":
#     print("===== Databricks App Hub Deployment =====")
    
#     check_requirements()
#     if validate_yaml():
#         deploy = input("\nDo you want to proceed with deployment? (y/n): ")
#         if deploy.lower() == "y":
#             if deploy_app():
#                 print("\n🎉 Your Databricks App Hub is now deployed!")
#             else:
#                 print("\n❌ Deployment failed. Please check the logs.")
#         else:
#             print("\nDeployment cancelled.")
#     else:
#         print("\n❌ Fix configuration issues before deploying.") 