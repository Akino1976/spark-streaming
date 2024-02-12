provider_region = "eu-west-1"
aws_region      = "eu-west-1"
aws_account     = ""
aws_role        = ""
environment     = "staging"
region          = "eu"
namespace       = "finance-data"

kafka_endpoints = [
  "kafka-1.staging.eu1",
  "kafka-2.staging.eu1",
  "kafka-3.staging.eu1"
]
availability_zone = "eu-west-1a"

kafka_access_vpc_id = "vpc-0de5f04f013a89493"
kafka_access_sg_id  = "sg-0a642829290fdbfb2"
kafka_user_names    = "integration.spark-streaming"
kafka_ack_name      = "integration.acknowledgements"
