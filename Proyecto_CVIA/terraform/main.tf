#-------------------------------------------------------------------
# Provider - AWS
#-------------------------------------------------------------------
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.region
}

#-------------------------------------------------------------------
# AMI - Amazon Linux 2023 ARM64 (dinámica)
#-------------------------------------------------------------------
data "aws_ami" "al2023_arm64" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-arm64"]
  }

  filter {
    name   = "architecture"
    values = ["arm64"]
  }
}

#-------------------------------------------------------------------
# Security Group - SSH, HTTP, NodePort nginx
#-------------------------------------------------------------------
resource "aws_security_group" "k3s_sg" {
  name        = "${var.environment}-k3s-sg"
  description = "k3s node: SSH + HTTP + NodePort nginx"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "nginx NodePort"
    from_port   = 30080
    to_port     = 30080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-k3s-sg"
    Environment = var.environment
  }
}

#-------------------------------------------------------------------
# EC2 - t4g.micro ARM (free tier 12 meses)
#-------------------------------------------------------------------
resource "aws_instance" "k3s_node" {
  ami                    = data.aws_ami.al2023_arm64.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.k3s_sg.id]
  user_data              = file("../scripts/install-k3s.sh")

  root_block_device {
    volume_size = 8
    volume_type = "gp3"
  }

  tags = {
    Name        = "${var.environment}-k3s-node"
    Environment = var.environment
  }
}
