import os
import json
import logging
from datetime import datetime, timedelta

import azure.functions as func
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    filename = req.params.get("filename")
    if filename:
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )

        container_name = "images"

        blob_client = blob_service_client.get_blob_client(container_name, filename)

        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_client.blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True, write=True, create=True),
            expiry=datetime.utcnow() + timedelta(minutes=5),
        )

        return func.HttpResponse(
            json.dumps({"url": blob_client.url + "?" + sas_token}), status_code=200
        )
    else:
        return func.HttpResponse(
            "Please pass a filename on the query string or in the request body",
            status_code=400,
        )
