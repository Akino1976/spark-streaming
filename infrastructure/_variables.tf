locals {
  tags = {
    Project           = "data-streaming"
    Environment       = title("${var.environment}")
  }
  configuration_path = "s3://streaming-${var.environment}-${var.aws_region}/assets"
  jars               = "s3://streaming-${var.environment}-${var.aws_region}/jars"
}
data "aws_caller_identity" "this" {}

data "aws_ssm_parameter" "spark_streaming_keys" {
  name = "/${var.namespace}/${var.kafka_user_names}/${var.region}"
}

data "aws_ssm_parameter" "spark_acknowledgements_keys" {
  name = "/${var.namespace}/${var.kafka_ack_name}/${var.region}"
}

variable "environment" {
  type = string

  validation {
    condition     = var.environment == "staging" || var.environment == "production"
    error_message = "Environment must be either `staging` or `production`."
  }
}

variable "sql_schema" {
  type = map(object({
    tablename = string
    filename  = string
  }))
  default = {}
}

variable "aws_account" {
  description = "AWS account to use"
  type        = string
}

variable "kafka_endpoints" {
  description = "Kafka endpoints to access 'inbound' (ack/nack) topics"
  type        = set(string)
}

variable "availability_zone" {
  description = "Kafka availability_zone"
  type        = string
}


variable "kafka_access_vpc_id" {
  description = "ID of the vpc from which Kafka endpoints are available."
  type        = string
}

variable "kafka_access_sg_id" {
  description = "ID of the security group allowing access to Kafka endpoints. Must be within the vpc of id='var.kafka_access_vpc_id'"
  type        = string
}

variable "kafka_user_names" {
  description = "Username to authenticate against Kafka endpoints."
  type        = string
}
