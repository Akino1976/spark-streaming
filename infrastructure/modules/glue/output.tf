output "glue_job_arn" {
  value = aws_glue_job.this.arn
}

output "glue_job_name" {
  value = aws_glue_job.this.id
}
