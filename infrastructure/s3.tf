resource "aws_s3_bucket" "s3_spark_streaming_bucket" {
  bucket        = "${var.namespace}-streaming-${var.environment}-${var.aws_region}"
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_public_access_block" "spark_public_settings" {
  bucket                  = aws_s3_bucket.s3_spark_streaming_bucket.id
  restrict_public_buckets = true
  ignore_public_acls      = true
  block_public_policy     = true
  block_public_acls       = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "spark_encryption" {
  bucket = aws_s3_bucket.s3_spark_streaming_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}


resource "aws_s3_bucket" "spark_logs" {
  bucket        = "${var.namespace}-spark-logs-${var.environment}-${var.aws_region}"
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_public_access_block" "spark_query_block" {
  bucket                  = aws_s3_bucket.spark_logs.bucket
  restrict_public_buckets = true
  ignore_public_acls      = true
  block_public_policy     = true
  block_public_acls       = true
}
