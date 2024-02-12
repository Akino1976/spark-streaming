module "datadog_spark_streaming_alert" {
  source      = "./modules/datadog_alert"
  environment = var.environment
  aws_region  = var.aws_region
  aws_account = var.aws_account
  tags        = local.tags
  glue_job_name = resource.aws_glue_job.spark_streaming.id
}