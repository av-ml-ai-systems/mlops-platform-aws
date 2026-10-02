resource "aws_s3_bucket" "mlops_data_lake" {
  bucket = "mlops-engineering-data-lake-882507341805"

  tags = {
    Name        = "MLOps Engineering Data Lake"
    Environment = "Learning"
    ManagedBy   = "Terraform"
  }
}