resource "aws_glue_job" "this" {
  name              = var.name
  role_arn          = var.role
  description       = var.description
  glue_version      = "4.0"
  worker_type       = var.worker_type == null ? "G.1X" : var.worker_type
  number_of_workers = var.nr_of_worker
  timeout           = null
  command {
    name            = "gluestreaming"
    python_version  = 3
    script_location = var.script_location
  }
  default_arguments = merge({
    "--continuous-log-logGroup"          = var.cloudwatch_logs
    "--class"                            = "GlueApp"
    "--job-language"                     = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-continuous-log-filter"     = "true"
    "--enable-observability-metrics"     = "true"
    "--enable-spark-ui"                  = "true"
    "--enable-metrics"                   = "true"
    "--enable-job-insights"              = "true"
    "--enable-auto-scaling"              = var.environment == "staging" ? "false" : "true"
    "--spark-event-logs-path"            = var.spark_logs
    "--job-bookmark-option"              = "job-bookmark-disable"
    "--extra-files"                      = var.configuration_path
    "--extra-py-files"                   = var.python_common_path
  }, var.arguments)
  execution_property {
    max_concurrent_runs = 1
  }
  connections = [var.msk_connection_name]
  tags        = var.tags
}