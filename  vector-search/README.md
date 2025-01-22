# Databricks Apps: Vector Search with Gradio example
This code sample shows how you can integrate [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html) with a [Mosaic AI Vector Search](https://docs.databricks.com/en/generative-ai/vector-search.html) direct query index.

Use this sample as a starting point to build your own applications based on Databricks Apps and Mosaic AI Vector Search.

## Features

* Document ingestion: upload a PDF, chunks PDF, ingests vector embeddings into vector search index
* Search: perform a vector search query on the index
* [Gradio](https://www.gradio.app/) for UI and [LangChain](https://python.langchain.com/docs/introduction/) for chunking
* Deployment notebook to set up necessary resources

![Databricks Vector Search example Gradio app screenshot](screenshot.png "Databricks Vector Search example Gradio app")

## Setup

[Clone this GitHub repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) and [load it as a Git folder](https://docs.databricks.com/en/repos/index.html) in your Databricks Workspace.

Next, follow the instructions in the [setup.py](setup.py) notebook to deploy the application and required Databricks resources.