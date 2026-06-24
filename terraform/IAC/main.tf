terraform {
  backend "s3" {
    bucket       = "your-name-terraform-state"
    key          = "study/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true   # replaces dynamodb_table
  }
}