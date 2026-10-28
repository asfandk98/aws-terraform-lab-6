
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = 7
  kms_key_id        = aws_kms_key.logs.arn

  tags = {
    Project     = "aws-terraform-lab6"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_log_group" "api_access" {
  name              = "/aws/apigateway/aws-terraform-lab6-api"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.logs.arn

  tags = {
    Project     = "aws-terraform-lab6"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
