#-------------------------------------------------------------------
# Provider - Conexión a AWS
#-------------------------------------------------------------------
terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend S3 - el bucket lo crea launcher/main.tf
  # El nombre del bucket se pasa con: terraform init -backend-config="bucket=<nombre>"
  # En GitHub Actions esto lo maneja el workflow automáticamente via TF_STATE_BUCKET
  backend "s3" {
    key    = "k3s/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}

#-------------------------------------------------------------------
# Data Source - AMI Amazon Linux 2023 ARM64 (más reciente)
#-------------------------------------------------------------------
data "aws_ami" "amazon_linux_2023" {
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
# Data Source - Zonas de disponibilidad de la región
#-------------------------------------------------------------------
data "aws_availability_zones" "disponibles" {
  state = "available"
}

#-------------------------------------------------------------------
# VPC Principal
#-------------------------------------------------------------------
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-cvia-vpc"
    Environment = var.environment
  }
}

#-------------------------------------------------------------------
# Internet Gateway - Permite salida a internet desde la VPC
#-------------------------------------------------------------------
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.environment}-cvia-igw"
    Environment = var.environment
  }
}

#-------------------------------------------------------------------
# Subnet Pública - Aquí vive el EC2 con k3s
#-------------------------------------------------------------------
resource "aws_subnet" "publica" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = data.aws_availability_zones.disponibles.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.environment}-cvia-subnet-publica"
    Environment = var.environment
  }
}

#-------------------------------------------------------------------
# Route Table - Dirige el tráfico de la subnet pública al IGW
#-------------------------------------------------------------------
resource "aws_route_table" "publica" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "${var.environment}-cvia-rt-publica"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "publica" {
  subnet_id      = aws_subnet.publica.id
  route_table_id = aws_route_table.publica.id
}

#-------------------------------------------------------------------
# Security Group - Reglas de firewall para el EC2
#-------------------------------------------------------------------
resource "aws_security_group" "k3s_sg" {
  name        = "${var.environment}-cvia-k3s-sg"
  description = "Permite SSH, HTTP y el puerto de nginx en k3s"
  vpc_id      = aws_vpc.main.id

  # SSH para administrar la instancia
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP estándar
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # NodePort donde nginx estará expuesto en k3s
  ingress {
    description = "Nginx NodePort"
    from_port   = 30080
    to_port     = 30080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Permitir todo el tráfico saliente (para descargar paquetes, imágenes, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-cvia-k3s-sg"
    Environment = var.environment
  }
}

#-------------------------------------------------------------------
# EC2 - Instancia ARM t4g.micro con k3s instalado al iniciar
#-------------------------------------------------------------------
resource "aws_instance" "k3s_node" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.publica.id
  vpc_security_group_ids = [aws_security_group.k3s_sg.id]
  key_name               = var.key_name

  # Script que se ejecuta al lanzar la instancia por primera vez
  user_data = file("${path.module}/../scripts/install-k3s.sh")

  # Disco de 20 GB es suficiente para k3s + nginx
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name        = "${var.environment}-cvia-k3s-node"
    Environment = var.environment
    Proyecto    = "CVIA"
  }
}
