
import json
import os
import sys
from types import ModuleType
from unittest.mock import MagicMock

os.environ["TABLE_NAME"] = "test-table"
os.environ["ENVIRONMENT"] = "test"

# Mock boto3 and its DynamoDB condition builder before importing the app.
mock_boto3 = MagicMock()
mock_table = MagicMock()
mock_boto3.resource.return_value.Table.return_value = mock_table

mock_boto3_module = ModuleType("boto3")
mock_boto3_module.resource = mock_boto3.resource

mock_dynamodb_module = ModuleType("boto3.dynamodb")
mock_conditions_module = ModuleType("boto3.dynamodb.conditions")

mock_key = MagicMock()
mock_conditions_module.Key = mock_key

sys.modules["boto3"] = mock_boto3_module
sys.modules["boto3.dynamodb"] = mock_dynamodb_module
sys.modules["boto3.dynamodb.conditions"] = mock_conditions_module

lambda_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "lambda")
)
sys.path.insert(0, lambda_dir)

from app import lambda_handler


def authenticated_event(method, path="/tasks", sub="user-123", body=None):
    event = {
        "rawPath": path,
        "requestContext": {
            "http": {"method": method},
            "authorizer": {
                "jwt": {"claims": {"sub": sub}}
            },
        },
    }
    if body is not None:
        event["body"] = body
    return event


def test_health_is_public():
    event = {
        "rawPath": "/health",
        "requestContext": {"http": {"method": "GET"}},
    }

    result = lambda_handler(event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["status"] == "healthy"
    assert body["service"] == "aws-terraform-lab6"
    assert body["environment"] == "test"


def test_create_task_assigns_authenticated_owner():
    mock_table.reset_mock()

    event = authenticated_event(
        "POST",
        body=json.dumps({
            "title": "Test Terraform",
            "status": "pending",
            "owner_id": "attacker-selected-user",
        }),
    )

    result = lambda_handler(event, None)

    assert result["statusCode"] == 201
    body = json.loads(result["body"])
    assert body["title"] == "Test Terraform"
    assert body["status"] == "pending"
    assert body["owner_id"] == "user-123"

    saved_task = mock_table.put_item.call_args.kwargs["Item"]
    assert saved_task["owner_id"] == "user-123"
    assert saved_task["owner_id"] != "attacker-selected-user"


def test_list_tasks_queries_only_authenticated_owner():
    mock_table.reset_mock()
    mock_table.query.return_value = {
        "Items": [
            {
                "id": "123",
                "owner_id": "user-123",
                "title": "My Task",
                "status": "pending",
            }
        ]
    }

    result = lambda_handler(authenticated_event("GET"), None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert len(body["tasks"]) == 1
    assert body["tasks"][0]["title"] == "My Task"

    mock_key.assert_called_with("owner_id")
    mock_key.return_value.eq.assert_called_with("user-123")
    mock_table.query.assert_called_once_with(
        IndexName="owner_id-index",
        KeyConditionExpression=mock_key.return_value.eq.return_value,
    )
    mock_table.scan.assert_not_called()



def test_tasks_reject_missing_identity():
    mock_table.reset_mock()

    event = {
        "rawPath": "/tasks",
        "requestContext": {"http": {"method": "GET"}},
    }

    result = lambda_handler(event, None)

    assert result["statusCode"] == 401
    mock_table.query.assert_not_called()


def test_create_task_rejects_invalid_json():
    result = lambda_handler(
        authenticated_event("POST", body="{invalid"),
        None,
    )

    assert result["statusCode"] == 400
    mock_table.put_item.assert_not_called()


def test_create_task_rejects_blank_title():
    result = lambda_handler(
        authenticated_event(
            "POST",
            body=json.dumps({"title": "   "}),
        ),
        None,
    )

    assert result["statusCode"] == 400
    mock_table.put_item.assert_not_called()


def test_create_task_rejects_invalid_status():
    result = lambda_handler(
        authenticated_event(
            "POST",
            body=json.dumps({
                "title": "Test",
                "status": "not-a-valid-status",
            }),
        ),
        None,
    )

    assert result["statusCode"] == 400
    mock_table.put_item.assert_not_called()
def test_create_task_rejects_non_string_status():
    mock_table.reset_mock()

    result = lambda_handler(
        authenticated_event(
            "POST",
            body=json.dumps({
                "title": "Test",
                "status": [],
            }),
        ),
        None,
    )

    assert result["statusCode"] == 400
    mock_table.put_item.assert_not_called()
