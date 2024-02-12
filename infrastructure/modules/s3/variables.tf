variable "bucket" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = null
}

variable "environment" {
  type = string
}

variable "restricted_bucket" {
  type    = bool
  default = false
}

variable "enable_logs" {
  type    = bool
  default = false
}

variable "kms_arn" {
  type        = string
  default     = null
  description = "Optional ARN to a KMS key to use for server side encryption"
}
