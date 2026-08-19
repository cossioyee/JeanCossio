#-------------------------------------------------------------------
# Outputs - Información útil después del apply
#-------------------------------------------------------------------

output "instancia_ip_publica" {
  description = "IP pública de la instancia EC2 con k3s"
  value       = aws_instance.k3s_node.public_ip
}

output "instancia_id" {
  description = "ID de la instancia EC2"
  value       = aws_instance.k3s_node.id
}

output "comando_ssh" {
  description = "Comando para conectarse por SSH a la instancia"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_instance.k3s_node.public_ip}"
}

output "url_nginx" {
  description = "URL para ver nginx en el navegador (esperar ~2 min después del apply)"
  value       = "http://${aws_instance.k3s_node.public_ip}:30080"
}

output "vpc_id" {
  description = "ID de la VPC creada"
  value       = aws_vpc.main.id
}
