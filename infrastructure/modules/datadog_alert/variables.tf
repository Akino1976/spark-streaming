variable "environment" {
  type    = string
  default = null
}

variable "aws_region" {
  type    = string
  default = null
}

variable "aws_account" {
  type    = string
  default = null
}

variable "alert_type" {
  type    = string
  default = null
}

variable "alert_evaluation_period" {
  type    = string
  default = null
}

variable "glue_job_name" {
  type    = string
  default = null
}

variable "tags" {
  type    = map(string)
  default = null
}
