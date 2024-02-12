data "aws_vpc" "kafka_access_vpc" {
  id = var.kafka_access_vpc_id
}

data "aws_subnets" "kafka_access_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.kafka_access_vpc.id]
  }
  filter {
    name   = "availability-zone"
    values = [var.availability_zone]
  }

  tags = {
    Network = "Private"
  }
}

data "aws_security_group" "kafka_access_sg" {
  vpc_id     = data.aws_vpc.kafka_access_vpc.id
  id         = var.kafka_access_sg_id
  depends_on = [data.aws_vpc.kafka_access_vpc]
}

data "aws_security_groups" "kafka_access_sgs" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.kafka_access_vpc.id]
  }
  filter {
    name   = "group-name"
    values = ["*default*"]
  }
}

resource "aws_glue_connection" "self_kafka_connection" {
  name            = "kafka_${var.environment}_connection_${var.aws_region}"
  description     = "Connection to self-hosted cluster ${var.aws_region} ${var.environment}"
  connection_type = "KAFKA"
  connection_properties = {
    KAFKA_BOOTSTRAP_SERVERS = "${join(",", [for s in var.kafka_endpoints : format("%s", s)])}"
    KAFKA_SSL_ENABLED       = "false"
  }

  physical_connection_requirements {
    availability_zone      = var.availability_zone
    subnet_id              = data.aws_subnets.kafka_access_subnets.ids[0]
    security_group_id_list = [var.kafka_access_sg_id]
  }
}
