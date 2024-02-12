# consumer
module "cloudwatch_streaming_log_group" {
  source        = "./modules/cloudwatch"
  log_name      = format("/aws-glue/job/%s", "${var.project}-${var.aws_region}")
  log_retention = 5
  tags          = local.tags
}