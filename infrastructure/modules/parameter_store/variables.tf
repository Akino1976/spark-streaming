variable "name" {
  type = string
}

variable "tier" {
  type = string
}

variable "type" {
  type    = string
  default = "SecureString"
}

variable "overwrite" {
  type    = bool
  default = true
}

variable "value" {
  type    = string
  default = false
}

variable "tags" {
  type    = map(string)
  default = null
}
