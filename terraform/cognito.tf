
resource "aws_cognito_user_pool" "api" {
  name                     = "aws-terraform-lab6-users"
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 3
  }

  tags = {
    Project     = "aws-terraform-lab6"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_cognito_user_pool_domain" "api" {
  domain       = var.cognito_domain_prefix
  user_pool_id = aws_cognito_user_pool.api.id
}

resource "aws_cognito_resource_server" "api" {
  identifier   = "tasks-api"
  name         = "Tasks API"
  user_pool_id = aws_cognito_user_pool.api.id

  scope {
    scope_name        = "read"
    scope_description = "Read the authenticated user's tasks"
  }

  scope {
    scope_name        = "write"
    scope_description = "Create tasks for the authenticated user"
  }
}

resource "aws_cognito_user_pool_client" "api" {
  name         = "aws-terraform-lab6-postman"
  user_pool_id = aws_cognito_user_pool.api.id

  generate_secret               = false
  prevent_user_existence_errors = "ENABLED"

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]

  allowed_oauth_scopes = [
    "openid",
    "email",
    "tasks-api/read",
    "tasks-api/write"
  ]

  supported_identity_providers = ["COGNITO"]

  callback_urls = [
    "https://oauth.pstmn.io/v1/browser-callback"
  ]

  logout_urls = [
    "https://oauth.pstmn.io/v1/browser-callback"
  ]
}
