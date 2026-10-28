# AWS Serverless Task API â€” Terraform

A serverless REST API built with AWS and Terraform, featuring Cognito JWT authentication, user-level data isolation, least-privilege IAM permissions, encrypted logging, monitoring, and infrastructure security scanning.

## Project Overview

This project demonstrates how to build and manage an authenticated serverless API using Infrastructure as Code (IaC).

Users authenticate through Amazon Cognito and access task-management endpoints through Amazon API Gateway. AWS Lambda processes requests, while Amazon DynamoDB stores tasks with ownership information so each authenticated user can retrieve only their own records.

## Architecture

**Request flow**

1. A client authenticates through Amazon Cognito.
2. The client sends a JWT access token with an API request.
3. Amazon API Gateway validates the JWT and enforces the required OAuth scopes.
4. AWS Lambda processes authorized requests.
5. Amazon DynamoDB stores and retrieves task records.
6. Amazon CloudWatch collects application and API logs.

**AWS services**

- Amazon API Gateway â€” HTTP API and request authorization
- Amazon Cognito â€” user authentication and OAuth scopes
- AWS Lambda â€” Python 3.12 application logic
- Amazon DynamoDB â€” task storage and owner-based queries
- AWS IAM â€” execution roles and permissions
- AWS KMS â€” encryption key configuration
- Amazon CloudWatch â€” logging and retention policies
- AWS X-Ray â€” distributed tracing
- Terraform â€” infrastructure provisioning and management

## Features

- Infrastructure managed through Terraform.
- JWT-protected API endpoints.
- Separate read and write OAuth scopes.
- Task ownership derived from authenticated identity claims.
- DynamoDB queries scoped to the authenticated user's ID.
- Input validation for task titles and allowed task statuses.
- DynamoDB point-in-time recovery enabled.
- CloudWatch log retention configured through Terraform.
- Lambda active tracing.
- KMS-backed encryption configuration for Lambda and log groups.
- Automated infrastructure security checks using Checkov.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/tasks` | Retrieve the authenticated user's tasks |
| POST | `/tasks` | Create a task for the authenticated user |

The health endpoint is public. The task endpoints require a valid JWT and the relevant OAuth scope.

### Example request

Create a task using an authorized access token:

```http
POST /tasks
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

```json
{
  "title": "Learn Terraform",
  "status": "pending"
}
```

Supported task statuses are `pending`, `in_progress`, and `completed`.

## Security Design

- **Authentication:** API Gateway validates Cognito-issued JWTs.
- **Authorization:** read and write operations use separate OAuth scopes.
- **Data isolation:** task ownership is derived from the authenticated token, not a client-supplied owner ID.
- **Least privilege:** Lambda IAM permissions are scoped to the operations and resources needed by the application.
- **Data recovery:** DynamoDB point-in-time recovery is enabled.
- **Encryption:** KMS is configured for Lambda and CloudWatch log encryption.
- **Monitoring:** CloudWatch logging and active Lambda tracing are configured.
- **Security scanning:** Checkov evaluates Terraform configurations for common AWS security misconfigurations.

## Continuous Integration

The GitHub Actions workflow at `.github/workflows/ci.yml` runs on pushes and pull requests targeting `main`, and can also be started manually.

The workflow:
- Runs the Python test suite with pytest.
- Checks Terraform formatting.
- Initializes Terraform without configuring a remote backend.
- Validates the Terraform configuration.
- Scans Terraform files with Checkov.

**Security scan status:** Checkov is currently configured with `soft_fail: true`. This allows the workflow to continue when Checkov reports findings; it does not mean those findings have passed or been fixed. The previously recorded scan reported 30 passed checks, 7 failed checks, and 1 skipped check. These findings remain documented as follow-up work.
## Validation and Testing

The following checks have been completed:

- Health endpoint returned HTTP 200.
- Unauthenticated task requests returned HTTP 401.
- Authenticated task retrieval returned HTTP 200.
- Authenticated task creation returned HTTP 201.
- Tests using two separate Cognito users demonstrated owner-based task isolation.
- `terraform plan` reported no changes against the configuration at the time of validation.
- Checkov reported 30 passed checks, 7 failed checks, and 1 skipped check in the recorded scan.

The Checkov findings are documented as follow-up work rather than being presented as fully resolved.

## Known Security Improvements

The recorded Checkov scan identified opportunities to improve:

- CloudWatch log retention.
- Explicit customer-managed KMS encryption for DynamoDB.
- Lambda code-signing validation.
- Dead-letter queue configuration where appropriate.
- Function-level concurrency controls.
- VPC deployment where justified by the architecture.

These recommendations require individual assessment. A failed policy check does not necessarily indicate an exploitable vulnerability, and architectural changes should be weighed against operational complexity and cost.

## Repository Structure

```text
aws-terraform-lab-6/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- architecture/
|   `-- aws-terraform-lab-6.mmd
|-- lambda/
|   `-- app.py
|-- terraform/
|   |-- provider.tf
|   |-- variables.tf
|   |-- outputs.tf
|   |-- api_gateway.tf
|   |-- cognito.tf
|   |-- lambda.tf
|   |-- dynamodb.tf
|   |-- iam.tf
|   |-- kms.tf
|   `-- cloudwatch.tf
|-- tests/
|   `-- test_app.py
|-- .gitignore
`-- README.md
```

## Prerequisites

- Terraform 1.6 or later.
- AWS CLI with a configured AWS profile.
- An AWS account with the permissions needed to provision the resources.
- Python 3.12 for the Lambda application.
- Checkov for infrastructure security scanning.

AWS resources may incur charges. Review service pricing and clean up resources when they are no longer required.

## Deployment

Run these commands from the Terraform directory:

```powershell
terraform init
terraform fmt -check
terraform validate
terraform plan
```

Review the plan before applying any changes.

```powershell
terraform apply
```

Supply the required Terraform variables through an appropriate local variables file or another supported mechanism. Do not commit secrets, credentials, or environment-specific private configuration.

## Security Scan

From the Terraform directory, run Checkov using your installed environment:

```powershell
& "..\.venv-checkov\Scripts\python.exe" -u "..\.venv-checkov\Scripts\checkov" -d . --framework terraform
```

Review each failed check, document justified exceptions, and rerun the scan after changes.

## Cleanup

When the environment is no longer needed, review the resources and Terraform state before destroying the lab.

```powershell
terraform plan -destroy
terraform destroy
```

Be aware that destroying resources can permanently remove data and that retained or separately managed resources may require additional cleanup.

## Skills Demonstrated

- AWS cloud architecture
- Terraform and Infrastructure as Code
- Serverless application design
- JWT authentication and OAuth scopes
- IAM least privilege
- Multi-user data isolation
- Encryption and key management
- CloudWatch monitoring and X-Ray tracing
- Infrastructure security scanning
- Troubleshooting and security trade-off analysis

## Project Status

Functional API and core infrastructure checks have been completed. Security review, repository preparation, and portfolio documentation are ongoing.

This project is intended as a hands-on cloud engineering portfolio demonstration.
