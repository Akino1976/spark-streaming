# Prefix
variable "name" {}
variable "permissions_boundary" {}
# Policy
variable "policy" {}
# AWS Service
variable "assume_role_policy" {}
variable "namespace" {}
variable "tags" {
  type    = map(string)
  default = null
}

# IAM Role
resource "aws_iam_role" "default" {
  name                 = var.name
  path                 = "/self-service/${var.namespace}/"
  permissions_boundary = var.permissions_boundary
  assume_role_policy   = var.assume_role_policy
  tags                 = var.tags
}

# IAM Policy
resource "aws_iam_policy" "default" {
  name   = var.name
  path   = "/self-service/${var.namespace}/"
  policy = var.policy
}

# IAM Role + IAM Policy
resource "aws_iam_role_policy_attachment" "default" {
  role       = aws_iam_role.default.name
  policy_arn = aws_iam_policy.default.arn
}

# output
output "iam_role_arn" {
  value = aws_iam_role.default.arn
}
output "iam_role_name" {
  value = aws_iam_role.default.name
}
