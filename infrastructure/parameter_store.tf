module "kafka_password" {
  source = "./modules/parameter_store"
  name   = "/${var.namespace}/${var.kafka_user_names}/${var.region}"
  value  = data.aws_ssm_parameter.spark_streaming_keys.value
  tags   = local.tags
  tier   = "Standard"
}
