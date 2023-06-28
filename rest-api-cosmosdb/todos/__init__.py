import os
import logging
import json
import uuid
import datetime

from azure.cosmos import CosmosClient
import azure.functions as func


client = CosmosClient.from_connection_string(
    os.environ["AzureCosmosDBConnectionString"]
)
database = client.get_database_client("todos")
container = database.get_container_client("items")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    if req.method == "POST":
        # Handle POST request
        try:
            req_body = req.get_json()

            new_todo = {
                "id": str(uuid.uuid4()),
                "category": req_body.get("category"),
                "task": req_body.get("task"),
                "status": req_body.get("status"),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            container.create_item(new_todo)

            return func.HttpResponse(
                json.dumps(new_todo), mimetype="application/json", status_code=201
            )
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return func.HttpResponse(
                "An error occurred while processing your request.", status_code=500
            )

    elif req.method == "GET":
        # Handle GET request
        try:
            id = req.route_params.get("id")

            if id is None:
                items = list(container.read_all_items())
            else:
                query = f"SELECT * FROM c WHERE c.id = '{id}'"
                items = list(
                    container.query_items(
                        query=query, enable_cross_partition_query=True
                    )
                )

            data = [
                {
                    "id": item.get("id"),
                    "category": item.get("category"),
                    "task": item.get("task"),
                    "status": item.get("status"),
                }
                for item in items
            ]

            return func.HttpResponse(
                json.dumps(data), mimetype="application/json", status_code=200
            )
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return func.HttpResponse(
                "An error occurred while processing your request.", status_code=500
            )

    elif req.method == "PUT":
        # Handle PUT request
        try:
            id = str(req.route_params.get("id"))

            req_body = req.get_json()
            category = req_body.get("category")

            # Read the existing item from the database
            item = container.read_item(item=id, partition_key=id)

            # Prevent updates to the 'id', 'created_at' fields
            non_updatable_fields = ["id", "created_at"]
            for key in req_body.keys():
                if key not in non_updatable_fields:
                    item[key] = req_body[key]

            updated_item = container.upsert_item(item)

            return func.HttpResponse(
                json.dumps(updated_item), mimetype="application/json", status_code=200
            )
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return func.HttpResponse(
                "An error occurred while processing your request.", status_code=500
            )

    elif req.method == "DELETE":
        # Handle DELETE request
        try:
            id = str(req.route_params.get("id"))

            if id is None:
                return func.HttpResponse(
                    "Missing 'id' in the request parameters", status_code=400
                )

            # Read the existing item from the database to get the category for partition key
            item = container.read_item(item=id, partition_key=id)

            container.delete_item(item=id, partition_key=id)

            return func.HttpResponse("Item deleted successfully", status_code=204)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return func.HttpResponse(
                "An error occurred while processing your request.", status_code=500
            )
