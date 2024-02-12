terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.6.2"
    }
    archive = {
      source = "hashicorp/archive"
    }
    datadog = {
      source = "DataDog/datadog"
    }
  }
  required_version = "~> 1.5.2"
}
