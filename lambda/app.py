
import json
import logging
import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME")
table = dynamodb.Table(table_name) if table_name else None

VALID_STATUSES = {"pending", "in_progress", "completed"}


def response(status_code, body):
    """Return a JSON response compatible with API Gateway HTTP API."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def get_owner_id(event):
    """Read the verified Cognito subject supplied by API Gateway."""
    request_context = event.get("requestContext") or {}
    authorizer = request_context.get("authorizer") or {}
    jwt = authorizer.get("jwt") or {}
    claims = jwt.get("claims") or {}

    return claims.get("sub")


def lambda_handler(event, context):
    """Handle health checks and authenticated task requests."""
    path = event.get("rawPath") or event.get("path", "")

    request_context = event.get("requestContext") or {}
    http_context = request_context.get("http") or {}
    method = http_context.get("method") or event.get("httpMethod")

    # Public health check.
    if path == "/health" and method == "GET":
        return response(
            200,
            {
                "status": "healthy",
                "service": "aws-terraform-lab6",
                "environment": os.environ.get(
                    "ENVIRONMENT", "development"
                ),
            },
        )

    # Only GET and POST are supported on /tasks.
    if path != "/tasks" or method not in {"GET", "POST"}:
        return response(404, {"error": "Route not found"})

    # Protected routes require a verified identity from API Gateway.
    owner_id = get_owner_id(event)

    if not owner_id:
        return response(401, {"error": "Authentication required"})

    if table is None:
        return response(
            500,
            {"error": "DynamoDB table is not configured"},
        )

    # Create a task for the authenticated user.
    if method == "POST":
        try:
            body = json.loads(event.get("body") or "{}")
        except (json.JSONDecodeError, TypeError):
            return response(400, {"error": "Invalid JSON body"})

        if not isinstance(body, dict):
            return response(
                400,
                {"error": "Request body must be a JSON object"},
            )

        title = body.get("title")

        if not isinstance(title, str) or not title.strip():
            return response(
                400,
                {"error": "title must be a non-empty string"},
            )

        title = title.strip()

        if len(title) > 200:
            return response(
                400,
                {"error": "title must be 200 characters or fewer"},
            )

        status = body.get("status", "pending")

        if not isinstance(status, str) or status not in VALID_STATUSES:
            return response(
                400,
                {
                    "error": (
                        "status must be pending, in_progress, or completed"
                    )
                },
            )

        # Never trust owner_id supplied in the request body.
        task = {
            "id": str(uuid.uuid4()),
            "owner_id": owner_id,
            "title": title,
            "status": status,
        }

        try:
            table.put_item(Item=task)
        except Exception:
            logger.exception("Failed to create task")
            return response(
                500,
                {"error": "Unable to create task"},
            )

        return response(201, task)

    # Retrieve only this user's tasks using the DynamoDB GSI.
    if method == "GET":
        tasks = []

        query_args = {
            "IndexName": "owner_id-index",
            "KeyConditionExpression": Key("owner_id").eq(owner_id),
        }

        try:
            while True:
                result = table.query(**query_args)
                tasks.extend(result.get("Items", []))

                last_key = result.get("LastEvaluatedKey")

                if not last_key:
                    break

                query_args["ExclusiveStartKey"] = last_key

        except Exception:
            logger.exception("Failed to list tasks")
            return response(
                500,
                {"error": "Unable to list tasks"},
            )

        return response(200, {"tasks": tasks})

    return response(404, {"error": "Route not found"})
