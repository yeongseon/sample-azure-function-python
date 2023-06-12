import os
import logging
import json

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    if req.method == "POST":
        # Handle POST request
        req_data = json.loads(req.get_body())
        new_records = []
        with open(os.path.join("todos", "data.json"), "r") as json_file:
            data = json_file.read()
            new_records = json.loads(data)
        req_data["id"] = new_records["todos"][-1]["id"] + 1
        new_records["todos"].append(req_data)
        with open(os.path.join("todos", "data.json"), "w") as json_file:
            json_file.write(json.dumps(new_records, indent=2))
        return func.HttpResponse(
            json.dumps(new_records), mimetype="application/json", status_code=201
        )

    elif req.method == "GET":
        # Handle GET request
        id = req.route_params.get("id")
        if id is not None:
            with open(os.path.join("todos", "data.json"), "r") as json_file:
                data = json_file.read()
                records = json.loads(data)
                for record in records["todos"]:
                    if record["id"] == int(id):
                        return func.HttpResponse(
                            json.dumps(record),
                            mimetype="application/json",
                            status_code=200,
                        )
        else:
            with open(os.path.join("todos", "data.json"), "r") as json_file:
                data = json_file.read()
                records = json.loads(data)
                return func.HttpResponse(
                    json.dumps(records["todos"]),
                    mimetype="application/json",
                    status_code=200,
                )

    elif req.method == "PUT":
        # Handle PUT request
        req_data = json.loads(req.get_body())
        logging.info(req_data)
        id = req.route_params.get("id")
        if id is not None:
            with open(os.path.join("todos", "data.json"), "r") as json_file:
                data = json_file.read()
                records = json.loads(data)
                for record in records["todos"]:
                    if record["id"] == int(id):
                        record["task"] = req_data["task"]
                        record["status"] = req_data["status"]
                return func.HttpResponse(
                    json.dumps(records), mimetype="application/json", status_code=200
                )
        else:
            return func.HttpResponse("Invalid request", status_code=400)

    elif req.method == "DELETE":
        # Handle DELETE request
        id = req.route_params.get("id")
        if id is not None:
            new_json = {"todos": []}
            with open(os.path.join("todos", "data.json"), "r") as json_file:
                data = json_file.read()
                records = json.loads(data)
                for record in records["todos"]:
                    if record["id"] == int(id):
                        continue
                    new_json["todos"].append(record)
            with open(os.path.join("todos", "data.json"), "w") as json_file:
                json_file.write(json.dumps(new_json, indent=2))
            return func.HttpResponse(json.dumps(new_json, indent=2), status_code=200)
        else:
            return func.HttpResponse("Invalid request", status_code=400)
