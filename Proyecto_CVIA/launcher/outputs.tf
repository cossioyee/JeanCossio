#-------------------------------------------------------------------
# Outputs - Lo que necesitas copiar después del apply
#-------------------------------------------------------------------

output "tf_state_bucket" {
  description = "Nombre del bucket S3 para el estado de Terraform — copiar como GitHub Variable TF_STATE_BUCKET"
  value       = aws_s3_bucket.tf_state.bucket
}

output "sitio_web_url" {
  description = "URL del sitio web estático para lanzar el cluster"
  value       = "http://${aws_s3_bucket_website_configuration.sitio_web.website_endpoint}"
}

output "sitio_web_bucket" {
  description = "Nombre del bucket del sitio web — para subir index.html"
  value       = aws_s3_bucket.sitio_web.bucket
}
