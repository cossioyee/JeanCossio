terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "us-east-1"
}

resource "aws_instance" "app_server" {
  ami           = "ami-08b5b3a93ed654d19"
  instance_type = "t2.micro"
  vpc_security_group_ids = [
    "sg-0982f4b699100a2b5"
  ]

  tags = {
    Name = "NextWork-WebApp"
  }
}

