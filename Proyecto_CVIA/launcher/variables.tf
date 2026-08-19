#-------------------------------------------------------------------
# Variables - Configuración del launcher
#-------------------------------------------------------------------

variable "region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Nombre del ambiente"
  type        = string
  default     = "dev"
}
