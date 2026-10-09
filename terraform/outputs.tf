output "dynamodb_table_name" {
  description = "DynamoDB table used by the task API"
  value       = aws_dynamodb_table.tasks.name
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}
output "api_endpoint" {
  description = "Public HTTPS endpoint for the HTTP API"
  value       = aws_apigatewayv2_api.http.api_endpoint
}