resource "aws_glue_job" "spark_producer_streaming" {
  name              = "${var.namespace}_producer_${var.environment}-${var.region}"
  role_arn          = module.main_role.iam_role_arn
  description       = "Service for streaming as producer in ${var.region} topics in ${var.environment} "
  glue_version      = "4.0"
  worker_type       = var.environment == "staging" ? "G.025X" : "G.1X"
  number_of_workers = var.environment == "staging" ? 2 : 10
  timeout           = null
  command {
    name            = "gluestreaming"
    python_version  = 3
    script_location = "s3://streaming-${var.environment}-${var.aws_region}/producer.py"
  }
  default_arguments = {
    "--continuous-log-logGroup"          = module.cloudwatch_producer_streaming_log_group.cloudwatch_name
    "--class"                            = "GlueApp"
    "--job-language"                     = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-continuous-log-filter"     = "true"
    "--enable-observability-metrics"     = "true"
    "--enable-metrics"                   = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${aws_s3_bucket.spark_logs.id}/${var.region}_spark_producer/"
    "--enable-job-insights"              = "true"
    "--enable-auto-scaling"              = "true"
    "--job-bookmark-option"              = "job-bookmark-disable"
    "--extra-files"                      = "${local.configuration_path}/producer/ack_${var.region}.yaml,${local.configuration_path}/spark_producer_conf.yaml"
    "--extra-py-files"                   = "s3://streaming-${var.environment}-${var.aws_region}/glue_library.zip"
    "--TempDir"                          = "s3://global-resource-${var.environment}/"
    "--environment"                      = var.environment
    "--asset"                            = "ack_${var.region}"
    "--region"                           = var.region
  }
  execution_property {
    max_concurrent_runs = 1
  }
  connections = ["${split(":", aws_glue_connection.self_kafka_connection.id)[1]}"]
  tags        = local.tags
}

