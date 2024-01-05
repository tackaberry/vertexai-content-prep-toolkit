# VertexAI Search & Conversation Content Preparation Script

This is a collection of scripts to prepare content for VertexAI Search & Conversation.

Read [Prepare data for ingesting](https://cloud.google.com/generative-ai-app-builder/docs/prepare-data) for more information.

`benefits.py` is a script to prepare benefits content for VertexAI Search & Conversation. This reads from 3 specific files for content, questions, and categories. The content is written to unstructured txt files and a `metadata.jsonl` file is created including a line for each record. The `metadata.jsonl` file is used to create a VertexAI Search & Conversation index.

`search.py` is a script to prepare search content for VertexAI Search & Conversation. This scrapes links from search results pages and then scrapes the content from each link. The content is converted into markdown and written to unstructured files and a `metadata.jsonl` file is created including a line for each record. The `metadata.jsonl` file is used to create a VertexAI Search & Conversation index.

## Get Started 

### Create an `.env` file

```
PROJECT=<project-id>
DATASET=<bigquery-dataset-name>
REGION=<region>

BENEFITS_BUCKET=<gcs-bucket-name>
BENEFITS_TABLE=<bigquery-table-name>
BENEFITS_DATASTORE=<vertexai-datastore-name>

BENEFITS_FILENAME_CATEGORIES=<categories-file-name>
BENEFITS_FILENAME_CONTENT=<content-file-name>
BENEFITS_FILENAME_QUESTIONS=<questions-file-name>

SEARCH_BUCKET=<gcs-bucket-name>
SEARCH_TABLE=<bigquery-table-name>

SEARCH_SESSION_KEY=<session-key-from-search-request>
SEARCH_URL_1=<search-url-endpoint>
SEARCH_URL_2=<search-origin>
SEARCH_URL_3=<search-content-domain>
SEARCH_TERM_1=<search-term>
SEARCH_TERM_2=<search-term>

```


### Login to GCP

```bash
gcloud auth login
gcloud config set project <project-id>
```

### Initialize your environment

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt

```

### All Makefile commands
    
```makefile
  help                 Show this help.
  run                  Run the search scraping app.
  runb                 Run the benefits content app.
  req                  Make requirements.
  clean                Clean up.
  mb                   Make bucket.
  sync                 Synce markdown to GCS.
  loadbq               Load BigQuery.
  mb-benefits          Make bucket for benefits content.
  sync-benefits        Sync benefits content to GCS.
  sync-benefits-txt    Sync benefits content to GCS.
  loadbq-benefits      Load BigQuery - Benefits content.
  datastore            Create the datastore.
  delete_datastore     Delete the datastore.
```


### Run benefits app

```bash
make runb
```