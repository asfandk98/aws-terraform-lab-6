resource "aws_dynamodb_table" "tasks" {
  name         = "aws-terraform-lab6-tasks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Project     = "aws-terraform-lab6"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}