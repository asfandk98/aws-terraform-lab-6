data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../lambda/app.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "api" {
  function_name = "aws-terraform-lab6-api"
  role          = aws_iam_role.lambda.arn

  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256

  runtime = "python3.12"
  handler = "app.lambda_handler"

  timeout     = 10
  memory_size = 128

  kms_key_arn = aws_kms_key.logs.arn


  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.tasks.name
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    Project     = "aws-terraform-lab6"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}