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

resource "aws_codebuild_project" "nextwork-devops-cicd-2" {
  name          = "nextwork-devops-cicd-2"
  description   = "Proyecto CodeBuild en Terraform"
  service_role  = "arn:aws:iam::742925356489:role/service-role/codebuild-nextwork-devops-cicd-service-role"
  
  artifacts {
    type                = "S3"                     # Tipo de artefacto: S3
    location            = "my-bucket-1693"    # Nombre del bucket S3
    name                = "nextwork-devops-cicd-artifact"             # Nombre del archivo ZIP
    packaging           = "ZIP"                    # Indica que se empaqueta como ZIP
    encryption_disabled = false                    # Habilita cifrado (opcional)
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    image           = "aws/codebuild/amazonlinux-x86_64-standard:corretto8"
    type            = "LINUX_CONTAINER"
  }

  source {
    type      = "GITHUB"
    location  = "https://github.com/cossioyee/nextwork-web-project.git" # URL del repositorio de GitHub
  }
   
  logs_config {
      cloudwatch_logs {
          status     = "ENABLED"
          group_name = "/aws/codebuild/nextwork-devops-cicd"
      }
  }
}