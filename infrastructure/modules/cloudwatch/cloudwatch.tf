resource "aws_cloudwatch_log_group" "this" {
  name              = var.log_name
  retention_in_days = var.log_retention
  tags              = var.tags
}

variable "log_name" {
  description = "A unique name for your log groups."
  type        = string
}

variable "log_retention" {
  default     = 1
  description = "Specifies the number of days you want to retain log events in the specified log group."
  type        = number
}

variable "tags" {
  default     = {}
  description = "A mapping of tags to assign to the object."
  type        = map(any)
}
output "cloudwatch_name" {
  value = aws_cloudwatch_log_group.this.name
}

output "cloudwatch_arn" {
  value = aws_cloudwatch_log_group.this.arn
}
