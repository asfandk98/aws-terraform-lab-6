import json
import os
import uuid
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME")

table = dynamodb.Table(table_name) if table_name else None


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, default=str)
    }


def lambda_handler(event, context):
    path = event.get("rawPath") or event.get("path", "")
    method = event.get("requestContext", {}).get("http", {}).get("method")

    # Health check
    if path == "/health" and method == "GET":
        return response(200, {
            "status": "healthy",
            "service": "aws-terraform-lab6",
            "environment": os.environ.get("ENVIRONMENT", "development")
        })

    # Create task
    if path == "/tasks" and method == "POST":
        if table is None:
            return response(500, {
                "error": "DynamoDB table is not configured"
            })

        body = json.loads(event.get("body") or "{}")

        title = body.get("title")
        status = body.get("status", "pending")

        if not title:
            return response(400, {
                "error": "title is required"
            })

        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "status": status
        }

        table.put_item(Item=task)

        return response(201, task)

    # List tasks
    if path == "/tasks" and method == "GET":
        if table is None:
            return response(500, {
                "error": "DynamoDB table is not configured"
            })

        result = table.scan()

        return response(200, {
            "tasks": result.get("Items", [])
        })

    return response(404, {
        "error": "Route not found"
    })