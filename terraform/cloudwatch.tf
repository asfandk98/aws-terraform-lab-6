resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = 7

  tags = {
    Project     = "aws-terraform-lab6"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}