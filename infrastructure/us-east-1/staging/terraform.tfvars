provider_region = "eu-west-1"
aws_region      = "us-east-1"
aws_account     = ""
aws_role        = ""
environment     = "staging"
region          = "us"
namespace       = "finance-data"

kafka_endpoints = [
  "kafka-1.staging.eu1",
  "kafka-2.staging.eu1",
  "kafka-3.staging.eu1"
]
availability_zone = "eu-west-1a"
kafka_user_names    = "integration.spark-streaming"
kafka_ack_name      = "integration.acknowledgements"
