data "aws_iam_role" "admin_role" {
  name = "finance-data.IdP_admin"
}

module "main_role" {
  source               = "./modules/iam"
  name                 = "${var.namespace}-spark-streaming-${var.environment}-${var.aws_region}"
  namespace            = var.namespace
  assume_role_policy   = data.aws_iam_policy_document.assume_role.json
  policy               = data.aws_iam_policy_document.combined.json
  permissions_boundary = "arn:aws:iam::${var.aws_account}:policy/edge-case/${var.namespace}/${var.namespace}.spark-boundary"
  tags                 = local.tags
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "glue.amazonaws.com",
        "ecs-tasks.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "combined" {
  source_policy_documents = [
    data.aws_iam_policy_document.access_kms.json,
    data.aws_iam_policy_document.ssm_access_policy_document.json,
    data.aws_iam_policy_document.s3_access.json,
    data.aws_iam_policy_document.glue_vpc_ec2_networking_policy_document.json,
    data.aws_iam_policy_document.cloudwatch_logs_access.json,
    data.aws_iam_policy_document.access_logs.json,
    data.aws_iam_policy_document.athena_policy.json,
  ]
}
