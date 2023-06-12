import logging

import azure.functions as func
from azure.storage.blob import BlobServiceClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python upload function processed a request.")

    for input_file in req.files.values():
        filename = input_file.filename
        contents = input_file.stream.read()

        logging.info("Filename: %s" % filename)
        logging.info("Contents: %s" % contents)

        blob_service_client = BlobServiceClient.from_connection_string(
            "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
        )
        blob_client = blob_service_client.get_blob_client(
            container="container1", blob=filename
        )
        blob_client.upload_blob(contents)

    return func.HttpResponse(f"This upload function executed successfully.")
