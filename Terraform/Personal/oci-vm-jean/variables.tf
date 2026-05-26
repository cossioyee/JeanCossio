#-------------------------------------------------------------------
# Variables - Oracle Cloud Infrastructure
#-------------------------------------------------------------------

variable "tenancy_ocid" {
  description = "OCID del tenancy de OCI"
  type        = string
}

variable "user_ocid" {
  description = "OCID del usuario de OCI"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint de la API key"
  type        = string
}

variable "private_key_path" {
  description = "Ruta al archivo de la private key de OCI (~/.oci/oci_api_key.pem)"
  type        = string
  default     = "~/.oci/oci_api_key.pem"
}

variable "region" {
  description = "Región de OCI (ej: mx-queretaro-1, us-ashburn-1, sa-saopaulo-1)"
  type        = string
  default     = "mx-queretaro-1"
}

variable "compartment_ocid" {
  description = "OCID del compartment donde se crearán los recursos"
  type        = string
}

variable "ssh_public_key_path" {
  description = "Ruta a la llave pública SSH para conectarse a la VM"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "vm_display_name" {
  description = "Nombre de la VM"
  type        = string
  default     = "jean-vm-oci"
}

variable "vm_ocpus" {
  description = "Número de OCPUs para VM.Standard.A1.Flex (max 4 en free tier)"
  type        = number
  default     = 2
}

variable "vm_memory_gb" {
  description = "Memoria RAM en GB para VM.Standard.A1.Flex (max 24 en free tier)"
  type        = number
  default     = 12
}

variable "vm_boot_volume_gb" {
  description = "Tamaño del boot volume en GB (max 200 en free tier)"
  type        = number
  default     = 50
}

variable "vcn_cidr" {
  description = "Rango CIDR de la VCN"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "Rango CIDR de la subnet pública"
  type        = string
  default     = "10.0.1.0/24"
}

variable "environment" {
  description = "Nombre del ambiente"
  type        = string
  default     = "dev"
}
