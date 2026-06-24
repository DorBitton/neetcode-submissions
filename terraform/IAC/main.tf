terraform {
  backend "s3" {
    bucket       = "dor-bitton-terraform-state"
    key          = "study/terraform.tfstate"
    region       = "eu-north-1"
    encrypt      = true
    use_lockfile = true # replaces dynamodb_table
  }
}