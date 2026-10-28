
resource "aws_apigatewayv2_api" "http" {
  name          = "aws-terraform-lab6-api"
  protocol_type = "HTTP"

  tags = {
    Project   = "aws-terraform-lab6"
    ManagedBy = "Terraform"
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.http.id
  name             = "aws-terraform-lab6-cognito-jwt"
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.api.id]
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.api.id}"
  }
}

resource "aws_apigatewayv2_route" "health" {
  #checkov:skip=CKV_AWS_309:Public health endpoint is intentional for uptime monitoring; task routes require Cognito authorization.
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /health"
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
  authorization_type = "NONE"
}
resource "aws_apigatewayv2_route" "create_task" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "POST /tasks"
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
  authorization_scopes = [
    "tasks-api/write"
  ]
}

resource "aws_apigatewayv2_route" "list_tasks" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /tasks"
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
  authorization_scopes = [
    "tasks-api/read"
  ]
}


resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_access.arn

    format = jsonencode({
      requestId  = "$context.requestId"
      routeKey   = "$context.routeKey"
      status     = "$context.status"
      sourceIp   = "$context.identity.sourceIp"
      httpMethod = "$context.httpMethod"
      path       = "$context.path"
    })
  }
}


resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromHttpApi"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}
