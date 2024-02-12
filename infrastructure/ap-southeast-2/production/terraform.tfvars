provider_region = "ap-southeast-2"
aws_region      = "ap-southeast-2"
aws_account     = "1"
aws_role        = ""
environment     = "production"
region          = "ap1"
namespace       = "finance-data"

kafka_endpoints = [
  "kafka-1.production.ap1",
  "kafka-2.production.ap1",
  "kafka-3.production.ap1"
]
availability_zone   = "ap-southeast-2a"
kafka_access_vpc_id = ""
kafka_access_sg_id  = ""
kafka_user_names    = "integration.spark-streaming"
kafka_ack_name      = "integration.acknowledgements"
