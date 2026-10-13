# ---------------------------------------------------------------------
# AWS Glue ETL — Curated Loan Risk Dataset
# ---------------------------------------------------------------------

# Uploads the Glue ETL script to S3 so the managed Glue runtime can execute it.
resource "aws_s3_object" "glue_curate_loan_dataset_script" {
  bucket = aws_s3_bucket.mlops_data_lake.id
  key    = "scripts/glue/curate_loan_dataset.py"

  # Resolves the script location relative to the Terraform directory.
  source = "${path.root}/../../scripts/glue/curate_loan_dataset.py"

  # Detects local script changes so Terraform can update the uploaded object.
  source_hash = filemd5(
    "${path.root}/../../scripts/glue/curate_loan_dataset.py"
  )
}

# Creates a dedicated IAM role for the Glue ETL job.
# This keeps ETL permissions separate from the existing crawler role.
resource "aws_iam_role" "glue_etl" {
  name = "MLOpsGlueETLRole"

  # Allows the AWS Glue service to assume this role when running the job.
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

# Grants the role standard permissions needed to operate an AWS Glue job,
# including access to Glue-related operational services.
resource "aws_iam_role_policy_attachment" "glue_etl_service_role" {
  role = aws_iam_role.glue_etl.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Defines the S3 permissions required by the ETL job.
data "aws_iam_policy_document" "glue_etl_s3_access" {
  # Allows listing only the S3 prefixes required by this ETL job.
  statement {
    sid    = "ListRequiredS3Prefixes"
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
        "standardized/*",
        "scripts/glue",
        "scripts/glue/*",
        "curated/loan_risk_dataset",
        "curated/loan_risk_dataset/*"
      ]
    }
  }

  # Allows reading the three standardized datasets.
  statement {
    sid    = "ReadStandardizedDatasets"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.mlops_data_lake.arn}/standardized/*"
    ]
  }

  # Allows Glue to download its ETL script from S3.
  statement {
    sid    = "ReadGlueETLScript"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.mlops_data_lake.arn}/scripts/glue/curate_loan_dataset.py"
    ]
  }

  # Allows writing curated output and replacing objects under the
  # dedicated curated prefix when the job uses overwrite mode.
  statement {
    sid    = "WriteCuratedDataset"
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:AbortMultipartUpload"
    ]

    resources = [
      "${aws_s3_bucket.mlops_data_lake.arn}/curated/loan_risk_dataset/*"
    ]
  }
}

# Attaches the restricted S3 permissions to the dedicated Glue ETL role.
resource "aws_iam_role_policy" "glue_etl_s3_access" {
  name = "MLOpsGlueETLS3Access"
  role = aws_iam_role.glue_etl.id

  policy = data.aws_iam_policy_document.glue_etl_s3_access.json
}

# Defines the managed AWS Glue Spark job that creates the curated dataset.
resource "aws_glue_job" "curate_loan_dataset" {
  name        = "mlops-curate-loan-dataset"
  description = "Integrates standardized domains into a curated loan-risk dataset."

  # Supplies the IAM role Glue assumes to access S3 and run the job.
  role_arn = aws_iam_role.glue_etl.arn

  # Uses AWS Glue 5.0 with two small G.1X workers for this dataset.
  glue_version      = "5.0"
  worker_type       = "G.1X"
  number_of_workers = 2

  # Limits the job runtime and disables automatic retries during initial validation.
  timeout     = 15
  max_retries = 0

  # Identifies the Python Spark ETL script stored in S3.
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.mlops_data_lake.bucket}/${aws_s3_object.glue_curate_loan_dataset_script.key}"
    python_version  = "3"
  }

  # Enables job metrics and continuous CloudWatch logging for troubleshooting.
  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
  }

  # Ensures the required IAM policies are attached before the job is created.
  depends_on = [
    aws_iam_role_policy_attachment.glue_etl_service_role,
    aws_iam_role_policy.glue_etl_s3_access
  ]
}

# ---------------------------------------------------------------------
# Glue Data Catalog — Curated Loan Risk Dataset
# ---------------------------------------------------------------------

resource "aws_glue_catalog_table" "curated_loan_risk_dataset" {
  name          = "curated_loan_risk_dataset"
  database_name = aws_glue_catalog_database.mlops_engineering_data_lake.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL              = "TRUE"
    "skip.header.line.count" = "1"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.mlops_data_lake.bucket}/curated/loan_risk_dataset/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.serde2.OpenCSVSerde"

      parameters = {
        separatorChar = ","
        quoteChar     = "\""
        escapeChar    = "\\"
      }
    }

    columns {
      name = "application_id"
      type = "string"
    }

    columns {
      name = "customer_id"
      type = "string"
    }

    columns {
      name = "loan_amount"
      type = "string"
    }

    columns {
      name = "loan_purpose"
      type = "string"
    }

    columns {
      name = "risk_grade"
      type = "string"
    }

    columns {
      name = "loan_interest_rate"
      type = "string"
    }

    columns {
      name = "loan_income_ratio"
      type = "string"
    }

    columns {
      name = "loan_outcome"
      type = "string"
    }

    columns {
      name = "age"
      type = "string"
    }

    columns {
      name = "income"
      type = "string"
    }

    columns {
      name = "home_ownership"
      type = "string"
    }

    columns {
      name = "employment_length"
      type = "string"
    }

    columns {
      name = "default_history"
      type = "string"
    }

    columns {
      name = "credit_history_length"
      type = "string"
    }
  }
}