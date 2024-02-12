resource "aws_ssm_parameter" "this" {
  name      = var.name
  type      = var.type
  overwrite = var.overwrite
  tier      = var.tier
  value     = var.value
  tags      = var.tags
}

output "parameter_store_arn" {
  value = aws_ssm_parameter.this.arn
}

output "parameter_store_name" {
  value = aws_ssm_parameter.this.name
}
