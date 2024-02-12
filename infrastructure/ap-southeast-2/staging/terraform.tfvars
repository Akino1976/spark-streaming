provider_region = "ap-southeast-2"
aws_region      = "ap-southeast-2"
aws_account     = ""
aws_role        = ""
environment     = "staging"
region          = "ap1"
namespace       = "finance-data"

kafka_endpoints = [
  "kafka-1.staging.ap1",
  "kafka-2.staging.ap1",
  "kafka-3.staging.ap1"
]
availability_zone   = "ap-southeast-2b"
kafka_user_names    = "integration.spark-streaming"
kafka_ack_name      = "integration.acknowledgements"
