# 1. Top-level Terraform Settings
terraform {
  backend "s3" {
    bucket       = "dor-bitton-terraform-state"
    key          = "study/terraform.tfstate"
    region       = "eu-north-1"
    encrypt      = true
    use_lockfile = true # Native S3 locking (Terraform 1.10+)
  }
}

# 2. Provider Configuration (Outside the terraform block)
provider "aws" {
  region = "eu-north-1"
}

# 3. Resource Definitions (Outside the terraform block)
resource "aws_instance" "example" {
  ami           = "ami-0aba19e56f3eaec05"
  instance_type = "t3.micro"
  vpc_security_group_ids = [aws_security_group.instance.id]

user_data = <<-EOF
#!/bin/bash
echo "Hello, World" > index.html
nohup busybox httpd -f -p 8080 &
EOF

  user_data_replace_on_change = true

  tags = {
    Name = "terraform-example"
  }
}

# 4.SGs
resource "aws_security_group" "instance" {
  name = "terraform-example-instance"

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}