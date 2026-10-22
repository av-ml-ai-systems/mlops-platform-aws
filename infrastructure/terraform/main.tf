# ---------------------------------------------------------------------
# S3 Data Lake
# ---------------------------------------------------------------------

# Creates the physical S3 bucket that acts as the data lake.
resource "aws_s3_bucket" "mlops_data_lake" {
  bucket        = "mlops-engineering-data-lake-882507341805"
  force_destroy = true

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

# ---------------------------------------------------------------------
# Standardized Data Layer
# ---------------------------------------------------------------------

# Uploads the processed customer dataset to the standardized S3 layer.
resource "aws_s3_object" "customer" {
  bucket = aws_s3_bucket.mlops_data_lake.id
  key    = "standardized/customer/customer.csv"
  source = "${path.root}/../../data/processed/customer/customer.csv"
}

# Uploads the processed financial history dataset to the standardized S3 layer.
resource "aws_s3_object" "financial_history" {
  bucket = aws_s3_bucket.mlops_data_lake.id
  key    = "standardized/financial_history/financial_history.csv"
  source = "${path.root}/../../data/processed/financial_history/financial_history.csv"
}

# Uploads the processed loan application dataset to the standardized S3 layer.
resource "aws_s3_object" "loan_application" {
  bucket = aws_s3_bucket.mlops_data_lake.id
  key    = "standardized/loan_application/loan_application.csv"
  source = "${path.root}/../../data/processed/loan_application/loan_application.csv"
}

# ---------------------------------------------------------------------
# AWS Glue Crawler IAM Role
# ---------------------------------------------------------------------

# Creates the IAM role that AWS Glue assumes to run the crawler.
resource "aws_iam_role" "glue_crawler" {
  name = "MLOpsGlueCrawlerRole"

  # Allows the AWS Glue service to assume this IAM role.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "glue.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}

# Grants the standard AWS Glue service permissions to the crawler role.
resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.glue_crawler.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Defines the S3 permissions required by the standardized-data crawler.
data "aws_iam_policy_document" "glue_s3_read" {
  # Allows the crawler to list objects under the standardized data prefix.
  statement {
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.mlops_data_lake.arn
    ]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"

      values = [
        "standardized",
        "standardized/*"
      ]
    }
  }

  # Allows the crawler to read standardized dataset objects.
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.mlops_data_lake.arn}/standardized/*"
    ]
  }
}

# Attaches the crawler's S3 read policy using its existing IAM policy name.
resource "aws_iam_role_policy" "glue_s3_read" {
  name   = "MLOpsGlueCrawlerS3ReadAccess"
  role   = aws_iam_role.glue_crawler.id
  policy = data.aws_iam_policy_document.glue_s3_read.json
}

# ---------------------------------------------------------------------
# AWS Glue Data Catalog
# ---------------------------------------------------------------------

# Creates the Glue Data Catalog database for the MLOps data lake.
resource "aws_glue_catalog_database" "mlops_engineering_data_lake" {
  name = "mlops_engineering_data_lake"
}

# Creates the crawler that discovers standardized datasets and
# registers their schemas in the Glue Data Catalog.
resource "aws_glue_crawler" "standardized_data" {
  name          = "mlops-standardized-data-crawler"
  role          = aws_iam_role.glue_crawler.arn
  database_name = aws_glue_catalog_database.mlops_engineering_data_lake.name

  # Restricts crawler discovery to the standardized data layer.
  s3_target {
    path = "s3://${aws_s3_bucket.mlops_data_lake.bucket}/standardized/"
  }

  # Updates discovered schemas and retains catalog entries when data
  # is no longer detected during a crawl.
  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "DEPRECATE_IN_DATABASE"
  }

  # Ensures the crawler's IAM permissions exist before it is created.
  depends_on = [
    aws_iam_role_policy_attachment.glue_service_role,
    aws_iam_role_policy.glue_s3_read
  ]
}

# ---------------------------------------------------------------------
# Amazon Athena Workgroup
# ---------------------------------------------------------------------

# Creates the dedicated Athena workgroup for Data Foundation queries.
resource "aws_athena_workgroup" "mlops_data_foundation" {
  name          = "mlops-data-foundation"
  description   = "Athena queries for the MLOps ML Data Foundation milestone"
  state         = "ENABLED"

  configuration {
    # Enforces this workgroup's query-result and encryption settings.
    enforce_workgroup_configuration = true

    # Publishes Athena query metrics to CloudWatch.
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      # Stores query results separately from standardized and curated data.
      output_location = "s3://${aws_s3_bucket.mlops_data_lake.bucket}/athena-results/"

      # Encrypts query results using S3-managed encryption.
      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }

  tags = {
    Name        = "MLOps Data Foundation Athena Workgroup"
    Environment = "Learning"
    ManagedBy   = "Terraform"
  }
}