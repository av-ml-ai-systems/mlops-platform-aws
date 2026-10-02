# Creates the physical S3 bucket that will act as the data lake.
resource "aws_s3_bucket" "mlops_data_lake" {
  bucket = "mlops-engineering-data-lake-882507341805"

  tags = {
    Name        = "MLOps Engineering Data Lake"
    Environment = "Learning"
    ManagedBy   = "Terraform"
  }
}

# Enables object versioning so S3 keeps previous versions of objects.
resource "aws_s3_bucket_versioning" "mlops_data_lake" {
  bucket = aws_s3_bucket.mlops_data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enables server-side encryption using S3-managed AES256 encryption.
resource "aws_s3_bucket_server_side_encryption_configuration" "mlops_data_lake" {
  bucket = aws_s3_bucket.mlops_data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Prevents the bucket from being exposed through public access settings.
resource "aws_s3_bucket_public_access_block" "mlops_data_lake" {
  bucket = aws_s3_bucket.mlops_data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Disables ACL-based permissions and makes the bucket owner control objects.
resource "aws_s3_bucket_ownership_controls" "mlops_data_lake" {
  bucket = aws_s3_bucket.mlops_data_lake.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
