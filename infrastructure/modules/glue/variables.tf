variable "name" {
  description = "Name of the glue job like eu_staging_banking"
  type        = string
}

variable "role" {
  description = "AWS role to enable execution"
  type        = string
}

variable "nr_of_worker" {
  description = "Number of workers"
  type        = number
}

variable "worker_type" {
  description = "Worker type for job"
  type        = string
  default     = null
}


variable "msk_connection_name" {
  description = "Glue connection to kafka"
  type        = string
}

variable "script_location" {
  description = "Script to execute using glue"
  type        = string
}

variable "cloudwatch_logs" {
  description = "Logs to cloudwatch"
  type        = string
}

variable "spark_logs" {
  description = "Logs to store spark logs"
  type        = string
}

variable "configuration_path" {
  description = "S3 file path to yaml file to exeute the job-paramters from"
  type        = string
}

variable "python_common_path" {
  description = "S3 file path to shared python modules"
  type        = string
}

variable "environment" {
  description = "Enviroment to deploy to"
  type        = string
  validation {
    condition     = var.environment == "staging" || var.environment == "production"
    error_message = "Environment must be either `staging` or `production`."
  }
}

variable "cron_job" {
  description = "execution time cron(0 6 ? * * *)"
  type        = string
  default     = ""
}

variable "description" {
  description = "description of the job"
  type        = string
  default     = ""
}

variable "tags" {
  type    = map(string)
  default = null
}

variable "arguments" {
  type    = map(string)
  default = null
}