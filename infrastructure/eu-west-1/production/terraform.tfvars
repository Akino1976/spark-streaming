provider_region = "eu-west-1"
aws_region      = "eu-west-1"
aws_account     = "1"
aws_role        = ""
environment     = "production"
region          = "eu"
namespace       = "finance-data"

kafka_endpoints = [
  "kafka-1.production.eu1",
  "kafka-2.production.eu1",
  "kafka-3.production.eu1",
  "kafka-4.production.eu1",
  "kafka-5.production.eu1",
  "kafka-6.production.eu1"
]
availability_zone   = "eu-west-1a"
kafka_access_vpc_id = "vpc-029c939fff809e06c"
kafka_access_sg_id  = "sg-087c612febcb5456d"
kafka_user_names    = "integration.spark-streaming"
kafka_ack_name      = "integration.acknowledgements"
