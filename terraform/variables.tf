variable "aws_region" {
  description = "AWS region for Lab 6"
  type        = string
  default     = "eu-north-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "cognito_domain_prefix" {
  description = "Unique lowercase Cognito hosted UI domain prefix"
  type        = string

  validation {
    condition = (
      length(var.cognito_domain_prefix) >= 1 &&
      length(var.cognito_domain_prefix) <= 63 &&
      can(regex("^[a-z][a-z0-9-]*[a-z0-9]$", var.cognito_domain_prefix))
    )

    error_message = "Use lowercase letters, numbers, and hyphens. Start with a letter and end with a letter or number."
  }
}
