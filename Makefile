include .env

project = $(PROJECT)
dataset = $(DATASET)

search_bucket = $(SEARCH_BUCKET)
search_table = $(SEARCH_TABLE)
search_dataset_table = $(dataset).$(search_table)

benefits_bucket = $(BENEFITS_BUCKET)
benefits_table = $(BENEFITS_TABLE)
benefits_dataset_table = $(dataset).$(benefits_table)
benefits_datastore = $(BENEFITS_DATASTORE)

token := $(shell gcloud auth print-access-token)

help: ## Show this help.
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-20s\033[0m %s\n", $$1, $$2}'

run: ## Run the search scraping app.
	@echo "Running..."
	@env/bin/python search.py

runb: ## Run the benefits content app.
	@echo "Running content app..."
	@env/bin/python benefits.py

req: ## Make requirements.
	@echo "Making requirements..."
	@env/bin/python -m pip freeze > requirements.txt

clean: ## Clean up.
	@rm -rf __pycache__
	@rm -rf env

mb: ## Make search bucket.
	@echo "Making search bucket..."
	@gsutil mb gs://$(search_bucket)

sync: ## Synce markdown to GCS.
	gsutil -m rsync -r cache/markdown/  gs://$(search_bucket)/ 

loadbq: ## Load BigQuery.
	@echo "Loading BigQuery..."
	bq rm -f --table $(search_dataset_table)
	bq load --source_format=NEWLINE_DELIMITED_JSON $(search_dataset_table) gs://$(search_bucket)/metadata.jsonl schema.json

mb-benefits: ## Make bucket for benefits content.
	@echo "Making bucket for benefits content..."
	@gsutil mb gs://$(benefits_bucket)

sync-benefits: ## Sync benefits content to GCS.
	gsutil -m rsync -r cache/benefits/  gs://$(benefits_bucket)/ 

sync-benefits-txt: ## Sync benefits content to GCS.
	gsutil -m rsync -r cache/benefits-txt/  gs://$(benefits_bucket)-txt/ 

loadbq-benefits: ## Load BigQuery - Benefits content.
	@echo "Loading BigQuery for benefits..."
	bq rm -f --table $(benefits_dataset_table)
	bq load --source_format=NEWLINE_DELIMITED_JSON $(benefits_dataset_table) gs://$(benefits_bucket)/metadata.jsonl schema.json

datastore: ## Create the datastore.
	@echo "Creating the datastore..."
	@curl -X POST \
	-H "Authorization: Bearer $(token)" \
	-H "Content-Type: application/json" \
	-H "X-Goog-User-Project: $(project)" \
	"https://discoveryengine.googleapis.com/v1alpha/projects/$(project)/locations/global/collections/default_collection/dataStores?dataStoreId=$(benefits_datastore)" \
	-d '{ "displayName": "$(benefits_datastore)", "industryVertical": "GENERIC", "solutionTypes": ["SOLUTION_TYPE_CHAT"], "contentConfig": "CONTENT_REQUIRED", "searchTier": "STANDARD", "searchAddOns": ["LLM"] }'
	@ curl -X POST \
	-H "Authorization: Bearer $(token)" \
	-H "Content-Type: application/json" \
	"https://discoveryengine.googleapis.com/v1/projects/$(project)/locations/global/collections/default_collection/dataStores/$(benefits_datastore)/branches/0/documents:import" \
	-d '{  "bigquerySource": { "projectId": "$(project)", "datasetId":"$(dataset)", "tableId": "$(benefits_table)" } }'

delete_datastore: ## Delete the datastore.
	@echo "Deleting the datastore..."
	@curl -X DELETE \
	-H "Authorization: Bearer $(token)" \
	-H "X-Goog-User-Project: $(project)" \
	"https://discoveryengine.googleapis.com/v1alpha/projects/$(project)/locations/global/dataStores/$(benefits_datastore)"
