#-------------------------------------------------------------------
# Variables - Configuración del proyecto
#-------------------------------------------------------------------

variable "region" {
  description = "Región de AWS donde se desplegará la infraestructura"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Nombre del ambiente (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "Rango de IPs para la VPC principal"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR para la subnet pública donde vivirá el EC2"
  type        = string
  default     = "10.0.1.0/24"
}

variable "instance_type" {
  description = "Tipo de instancia EC2 (t4g.micro es free tier ARM)"
  type        = string
  default     = "t4g.micro"
}

variable "key_name" {
  description = "Nombre del Key Pair en AWS para acceso SSH"
  type        = string
  default     = "cvia-key"
}
