# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks Apps and Vector Search Gradio Sample - Setup Notebook
# MAGIC
# MAGIC Follow the instruction in this notebook to deploy the Databricks Apps and Vector Search Gradio example application.
# MAGIC
# MAGIC This application requires the following three Databricks resources:
# MAGIC 1. A Unity Catalog schema to store the vector search index
# MAGIC 1. Vector search endpoint
# MAGIC 1. Databricks app compute resource
# MAGIC
# MAGIC Start by configuring a Unity Catalog schema name in the next notebook section in **cell 5: Define schema name and existing resources**.
# MAGIC
# MAGIC Optionally, input an existing vector search endpoint and app resource name. If you do not specify these resources, they will be created for you.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configure schema name and existing resources

# COMMAND ----------

# DBTITLE 1,Install required packages
# MAGIC %pip install databricks-sdk>=0.38.0 pyyaml --quiet

# COMMAND ----------

# DBTITLE 1,Restart Python
dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Define schema name and existing resources
# Input a Unity Catalog schema where your vector search index should be created
schema_name = ""  # Example: catalog.schema

# Optionally, input your existing resources here
vector_search_endpoint_name = ""
app_compute_name = ""

# COMMAND ----------

# MAGIC %md
# MAGIC Choose **Run all** to deploy your application. This will take a couple of minutes.
# MAGIC
# MAGIC You will find the app URL  in the output of the last cell in this notebook.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Get or create vector search endpoint and index
# MAGIC
# MAGIC If you have provided vector search endpoint and index names above, the following cells will check if they exist.
# MAGIC
# MAGIC If you didn't provide these resources, the following cells will create them for you.

# COMMAND ----------

# DBTITLE 1,Import dependencies and create workspace client
import os
import json
import uuid
import yaml
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.vectorsearch import (
    DirectAccessVectorIndexSpec,
    EmbeddingVectorColumn,
    VectorIndexType,
    EndpointType,
    EndpointStatusState,
)
from databricks.sdk.service.apps import (
    App,
    ApplicationState,
    AppDeployment,
    AppDeploymentMode,
)

w = WorkspaceClient()

# COMMAND ----------

# DBTITLE 1,Get or create vector search endpoint
if vector_search_endpoint_name:
    print(f"Checking vector search endpoint {vector_search_endpoint_name}...")
    try:
        endpoint = w.vector_search_endpoints.get_endpoint(vector_search_endpoint_name)

        if endpoint.endpoint_status.state == EndpointStatusState.ONLINE:
            print(f"Endpoint {endpoint.name} confirmed and in status ONLINE.")
        else:
            print("Endpoint exists but does not appear to be in status ONLINE.")
    except Exception as e:
        print(e)
else:
    endpoint_name = f"{str(uuid.uuid4().hex)[:12]}_vs_endpoint"
    print(
        f"Creating vector search endpoint {endpoint_name}. This will take a few minutes."
    )
    try:
        endpoint = w.vector_search_endpoints.create_endpoint_and_wait(
            name=endpoint_name, endpoint_type=EndpointType.STANDARD
        )
        vector_search_endpoint_name = endpoint.name
        print(f"Created vector search endpoint {endpoint.name}")
    except Exception as e:
        print(e)

# COMMAND ----------

# DBTITLE 1,Create vector search index
vector_search_index_name = f"{str(uuid.uuid4().hex)[:12]}_vs_index"

schema = json.dumps({"id": "string", "text": "string", "text_vector": "array<float>"})

try:
    index = w.vector_search_indexes.create_index(
        name=f"{schema_name}.{vector_search_index_name}",
        endpoint_name=vector_search_endpoint_name,
        primary_key="id",
        index_type=VectorIndexType.DIRECT_ACCESS,
        direct_access_index_spec=DirectAccessVectorIndexSpec(
            embedding_vector_columns=[
                EmbeddingVectorColumn(
                    name="text_vector",
                    embedding_dimension=1024,
                )
            ],
            schema_json=schema,
        ),
    )
    vector_search_index_name = index.vector_index.name
except Exception as e:
    print(e)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Get or create Databricks app compute

# COMMAND ----------

# DBTITLE 1,Get or create Databricks app compute
if app_compute_name:
    print(f"Checking app compute {app_compute_name}...")
    try:
        app = w.apps.get(app_compute_name)
        if app.app_status.state == ApplicationState.RUNNING:
            print(f"App compute {app.name} confirmed and in status RUNNING.")
        else:
            print("App compute exists but does not appear to be in status RUNNING.")
    except Exception as e:
        print(e)
else:
    compute_name = f"{str(uuid.uuid4().hex)[:12]}_app"
    print(f"Creating app compute {compute_name}. This will take a few minutes.")
    try:
        new_app = App(name=compute_name)
        app = w.apps.create_and_wait(app=new_app)
        app_compute_name = app.name
        print(f"App compute {app_compute_name} created.")
    except Exception as e:
        print(e)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Deploy the app

# COMMAND ----------

# DBTITLE 1,Update app.yaml with vector search endpoint and index
with open("app.yaml", "r") as file:
    config = yaml.safe_load(file)

for env_var in config.get("env", []):
    if env_var["name"] == "VECTOR_SEARCH_ENDPOINT_NAME":
        env_var["value"] = vector_search_endpoint_name
    elif env_var["name"] == "VECTOR_SEARCH_INDEX_NAME":
        env_var["value"] = f"{schema_name}.{vector_search_index_name}"

with open("app.yaml", "w") as file:
    yaml.safe_dump(config, file)

# COMMAND ----------

# DBTITLE 1,Deploy the application
try:
    new_deployment = AppDeployment(
        source_code_path=os.getcwd(),
    )

    deployment = w.apps.deploy_and_wait(
        app_name=app_compute_name, app_deployment=new_deployment
    )
    print(f"Your app {app_compute_name} has been deployed successfully.")

    url = w.apps.get(name=app_compute_name).url
    print(f"Your app URL: {url}")
except Exception as e:
    print(e)
