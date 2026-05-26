#-------------------------------------------------------------------
# Outputs
#-------------------------------------------------------------------

output "instance_id" {
  description = "OCID de la instancia"
  value       = oci_core_instance.vm.id
}

output "instance_public_ip" {
  description = "IP pública de la VM"
  value       = oci_core_instance.vm.public_ip
}

output "instance_private_ip" {
  description = "IP privada de la VM"
  value       = oci_core_instance.vm.private_ip
}

output "instance_shape" {
  description = "Shape de la instancia"
  value       = oci_core_instance.vm.shape
}

output "image_used" {
  description = "Nombre de la imagen usada"
  value       = data.oci_core_images.oracle_linux_8.images[0].display_name
}

output "vcn_id" {
  description = "OCID de la VCN"
  value       = oci_core_vcn.vcn.id
}

output "ssh_command" {
  description = "Comando para conectarse por SSH"
  value       = "ssh opc@${oci_core_instance.vm.public_ip}"
}
