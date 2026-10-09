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