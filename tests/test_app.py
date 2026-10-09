import json
import os
import sys
from unittest.mock import MagicMock

os.environ["TABLE_NAME"] = "test-table"
os.environ["ENVIRONMENT"] = "test"

# Mock boto3 before importing the Lambda application
mock_boto3 = MagicMock()
mock_table = MagicMock()

mock_boto3.resource.return_value.Table.return_value = mock_table

sys.modules["boto3"] = mock_boto3

# Add the Lambda source directory to Python's import path
lambda_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "lambda")
)

sys.path.insert(0, lambda_dir)

from app import lambda_handler


def test_health():
    event = {
        "rawPath": "/health",
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    result = lambda_handler(event, None)

    assert result["statusCode"] == 200

    body = json.loads(result["body"])

    assert body["status"] == "healthy"
    assert body["service"] == "aws-terraform-lab6"
    assert body["environment"] == "test"


def test_create_task():
    event = {
        "rawPath": "/tasks",
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": json.dumps({
            "title": "Test Terraform",
            "status": "pending"
        })
    }

    result = lambda_handler(event, None)

    assert result["statusCode"] == 201

    body = json.loads(result["body"])

    assert body["title"] == "Test Terraform"
    assert body["status"] == "pending"

    mock_table.put_item.assert_called_once()


def test_list_tasks():
    mock_table.scan.return_value = {
        "Items": [
            {
                "id": "123",
                "title": "Test Task",
                "status": "pending"
            }
        ]
    }

    event = {
        "rawPath": "/tasks",
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    result = lambda_handler(event, None)

    assert result["statusCode"] == 200

    body = json.loads(result["body"])

    assert len(body["tasks"]) == 1
    assert body["tasks"][0]["title"] == "Test Task"