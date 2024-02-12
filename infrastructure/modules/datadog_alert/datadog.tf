terraform {
  required_providers {
    datadog = {
      source = "DataDog/datadog"
    }
  }
}

resource "datadog_monitor" "this" {
  type     = "query alert"
  name     = "Job run had failed tasks for ${var.glue_job_name} in ${var.environment}"
  query    = "sum(last_${coalesce(var.alert_evaluation_period, "30m")}):sum:aws.glue.glue_driver_aggregate_num_failed_tasks{aws_account:${var.aws_account} , jobname:${var.glue_job_name}}.as_count() > 0"
  priority = "4"
  notify_no_data = true
  no_data_timeframe = var.environment == "production" ? 5 : 60

  evaluation_delay = 900

  message = <<EOF
  {{#is_alert}}**Job runs had failed task(s) in ${var.environment}**{{/is_alert}}
  {{#is_no_data}} No metrics recieved for ${var.glue_job_name}. Is job running? @slack-flow-monitoring{{/is_no_data}}
  {{#is_alert_recovery}} ${var.glue_job_name} recovered @slack-flow-monitoring{{/is_alert_recovery}}

  {{#is_alert}}
  Spark streaming job run had failed tasks in the last ${coalesce(var.alert_evaluation_period, "1h")}.
  Check job [${var.glue_job_name}](https://${var.aws_region}.console.aws.amazon.com/gluestudio/home?region=${var.aws_region}#/editor/job/${var.glue_job_name})

  Notify @slack-flow-monitoring
  {{/is_alert}}
EOF
  tags = [
    for k, v in var.tags :
    "${k}:${v}"
  ]
}
