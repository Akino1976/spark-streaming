provider "aws" {
  region = var.provider_region
}

provider "datadog" {
  api_url = "https://api.datadoghq.eu"
  api_key = data.aws_ssm_parameter.datadog_api_key.value
  app_key = data.aws_ssm_parameter.datadog_app_key.value
}

terraform {
  backend "s3" {
    encrypt                = true
    bucket                 = var.bucket
    region                 = var.region
    key                    = var.key
    skip_region_validation = true
  }
}
