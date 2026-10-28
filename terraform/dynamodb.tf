
resource "aws_dynamodb_table" "tasks" {
  name         = "aws-terraform-lab6-tasks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  point_in_time_recovery {
    enabled = true
  }
  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "owner_id"
    type = "S"
  }

  global_secondary_index {
    name            = "owner_id-index"
    projection_type = "ALL"

    key_schema {
      attribute_name = "owner_id"
      key_type       = "HASH"
    }
  }

  tags = {
    Project     = "aws-terraform-lab6"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
