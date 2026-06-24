terraform {
  backend "s3" {
    bucket         = "your-name-terraform-state"
    key            = "study/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}