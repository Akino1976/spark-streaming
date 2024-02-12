provider_region = "us-east-1"
aws_region      = "us-east-1"
aws_account     = "1"
aws_role        = ""
environment     = "production"
region          = "us"
namespace       = "finance-data"

kafka_endpoints = [
  "kafka-1.production.us1",
  "kafka-2.production.us1",
  "kafka-3.production.us1",
  "kafka-4.production.us1",
  "kafka-5.production.us1",
  "kafka-6.production.us1"
]
availability_zone   = "us-east-1a"
kafka_user_names    = "integration.spark-streaming"
kafka_ack_name      = "integration.acknowledgements"
