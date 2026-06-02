#-------------------------------------------------------------------
# Variables - AWS k3s node
#-------------------------------------------------------------------

variable "region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia EC2 (t4g.micro = ARM, free tier)"
  type        = string
  default     = "t4g.micro"
}

variable "key_name" {
  description = "Nombre del key pair de AWS para SSH"
  type        = string
}

variable "environment" {
  description = "Nombre del ambiente"
  type        = string
  default     = "cvia"
}
