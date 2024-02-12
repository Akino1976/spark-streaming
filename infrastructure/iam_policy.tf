data "aws_iam_policy_document" "access_kms" {
  statement {
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:GenerateDataKey"
    ]
    resources = ["*"]
  }
  version = "2012-10-17"
}

data "aws_iam_policy_document" "ssm_access_policy_document" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:Get*",
      "ssm:Describe*"
    ]
    resources = [
      "arn:aws:ssm:*:${var.aws_account}:parameter/${var.namespace}/*",
    ]
  }
}
data "aws_iam_policy_document" "s3_access" {
  version = "2012-10-17"
  statement {
    actions = ["s3:*"]
    resources = [
      "${aws_s3_bucket.s3_spark_streaming_bucket.arn}/*",
      aws_s3_bucket.s3_spark_streaming_bucket.arn,
      "arn:aws:s3:::aws-athena-query-results-*",
      "arn:aws:s3:::*",
      "arn:aws:s3:::aws-glue-*",
      "arn:aws:s3:::finance-data*/*",
      "arn:aws:s3:::aws-glue-*/*",
    ]
  }

  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
      "s3:PutObject",
      "s3:PutObjectAcl",
      "s3:PutObjectTagging",
      "s3:PutObjectVersionAcl"
    ]
    resources = [
      "${aws_s3_bucket.spark_logs.arn}/*",
      aws_s3_bucket.spark_logs.arn,
    ]
  }
}

data "aws_iam_policy_document" "access_logs" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  version = "2012-10-17"
}

data "aws_iam_policy_document" "cloudwatch_logs_access" {
  statement {
    effect = "Allow"
    actions = [
      "cloudwatch:Describe*",
      "cloudwatch:Get*",
      "cloudwatch:List*",
      "cloudwatch:PutDashboard",
      "cloudwatch:PutMetric*",
      "cloudwatch:DeleteAlarms",
      "cloudwatch:DeleteDashboards",
      "cloudwatch:SetAlarmState"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "cloudwatch:*",
    ]
    resources = [
      "arn:aws:cloudwatch:*:${var.aws_account}:alarm:finance-data*",
    "arn:aws:cloudwatch:*:${var.aws_account}:dashboard/finance-data*"]
  }
  version = "2012-10-17"
}

data "aws_iam_policy_document" "athena_policy" {
  policy_id = "access_athena"
  version   = "2012-10-17"
  statement {
    sid = "Stmt1710"
    actions = [
      "athena:Create*",
      "athena:BatchGet*",
      "athena:Get*",
      "athena:List*",
      "athena:RunQuery",
      "athena:StartQueryExecution"
    ]
    resources = ["*"]
  }
  statement {
    sid = "Stmt71101"
    actions = [
      "glue:Batch*",
      "glue:Cancel*",
      "glue:Create*",
      "glue:Delete*",
      "glue:Get*",
      "glue:List*",
      "glue:Reset*",
      "glue:Start*",
      "glue:Stop*",
      "glue:Update*",
      "glue:Use*",
      "glue:SearchTables"
    ]
    resources = ["*"]
  }
  statement {
    sid     = "Stmt711034"
    actions = ["glue:*"]
    resources = [
      "arn:aws:glue:*:${var.aws_account}:table*/*/finance-data*",
      "arn:aws:glue:*:${var.aws_account}:catalog"
    ]
  }
}


data "aws_iam_policy_document" "glue_vpc_ec2_networking_policy_document" {
  policy_id = "access_ec2"
  version   = "2012-10-17"
  statement {
    effect = "Allow"
    actions = [
      "ec2:DescribeVpcs",
      "ec2:DescribeVpcEndpoints",
      "ec2:DescribeRouteTables",
      "ec2:DescribeSubnets",
      "ec2:DescribeSecurityGroups",
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeNetworkInterfaces"
    ]
    resources = ["*"]
  }
  statement {
    effect    = "Allow"
    actions   = ["ec2:*Tags"]
    resources = ["*"]
  }
}
