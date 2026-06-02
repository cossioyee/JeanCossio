#-------------------------------------------------------------------
# Outputs
#-------------------------------------------------------------------

output "instance_public_ip" {
  description = "IP pública de la instancia k3s"
  value       = aws_instance.k3s_node.public_ip
}

output "ssh_command" {
  description = "Comando para conectarse por SSH"
  value       = "ssh ec2-user@${aws_instance.k3s_node.public_ip}"
}

output "nginx_url" {
  description = "URL para verificar nginx"
  value       = "http://${aws_instance.k3s_node.public_ip}:30080"
}

output "ami_used" {
  description = "AMI utilizada"
  value       = data.aws_ami.al2023_arm64.name
}
