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
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.region
}

#-------------------------------------------------------------------
# Sufijo aleatorio para hacer los nombres de bucket únicos en S3
# Los nombres de bucket son globales en AWS, no pueden repetirse
#-------------------------------------------------------------------
resource "random_string" "sufijo" {
  length  = 6
  special = false
  upper   = false
}

#-------------------------------------------------------------------
# Bucket S3 - Almacena el estado de Terraform (terraform.tfstate)
# Con versionado para poder recuperar estados anteriores
#-------------------------------------------------------------------
resource "aws_s3_bucket" "tf_state" {
  bucket = "cvia-tf-state-${random_string.sufijo.result}"

  tags = {
    Name        = "cvia-tf-state"
    Environment = var.environment
    Proyecto    = "CVIA"
  }
}

resource "aws_s3_bucket_versioning" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Bloquear acceso público al bucket de estado (nadie debe ver el tfstate)
resource "aws_s3_bucket_public_access_block" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#-------------------------------------------------------------------
# Bucket S3 - Aloja el sitio web estático (index.html)
#-------------------------------------------------------------------
resource "aws_s3_bucket" "sitio_web" {
  bucket = "cvia-sitio-web-${random_string.sufijo.result}"

  tags = {
    Name        = "cvia-sitio-web"
    Environment = var.environment
    Proyecto    = "CVIA"
  }
}

# Habilitar el hosting de sitio web estático
resource "aws_s3_bucket_website_configuration" "sitio_web" {
  bucket = aws_s3_bucket.sitio_web.id

  index_document {
    suffix = "index.html"
  }
}

# Permitir acceso público para que el sitio sea visible desde el navegador
resource "aws_s3_bucket_public_access_block" "sitio_web" {
  bucket = aws_s3_bucket.sitio_web.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Política que permite a cualquiera leer los archivos del sitio
resource "aws_s3_bucket_policy" "sitio_web" {
  bucket = aws_s3_bucket.sitio_web.id

  depends_on = [aws_s3_bucket_public_access_block.sitio_web]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.sitio_web.arn}/*"
      }
    ]
  })
}
