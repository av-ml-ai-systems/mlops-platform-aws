# ---------------------------------------------------------------------
# AWS Glue ETL - Curated Loan Risk Dataset
# ---------------------------------------------------------------------

variable "curated_loan_risk_dataset_version" {
  description = "Immutable curated dataset version queried by Athena."
  type        = string
  default     = "1.0.1"

  validation {
    condition     = can(regex("^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$", var.curated_loan_risk_dataset_version))
    error_message = "Use 1-64 letters, numbers, dots, underscores, or hyphens; start with a letter or number."
  }
}

# Uploads the Glue ETL script to S3.
resource "aws_s3_object" "glue_curate_loan_dataset_script" {
  bucket = aws_s3_bucket.mlops_data_lake.id
  key    = "scripts/glue/curate_loan_dataset.py"

  source = "${path.root}/../../scripts/glue/curate_loan_dataset.py"

  source_hash = filemd5(
    "${path.root}/../../scripts/glue/curate_loan_dataset.py"
  )
}

# Creates a dedicated IAM role for the Glue ETL job.
resource "aws_iam_role" "glue_etl" {
  name = "MLOpsGlueETLRole"

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

# Attaches standard Glue service permissions.
resource "aws_iam_role_policy_attachment" "glue_etl_service_role" {
  role       = aws_iam_role.glue_etl.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Defines the S3 permissions required by the ETL job.
data "aws_iam_policy_document" "glue_etl_s3_access" {
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
        "curated/loan_risk_dataset/versions/*",
        "metadata/versions/loan_risk_dataset/*"
      ]
    }
  }

  # Reads standardized source datasets.
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

  # Reads the Glue ETL script.
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

  # Reads published CSV objects to calculate artifact hashes.
  statement {
    sid    = "ReadPublishedCuratedArtifacts"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.mlops_data_lake.arn}/curated/loan_risk_dataset/versions/*"
    ]
  }

  # Writes new curated versions without granting object deletion.
  statement {
    sid    = "WriteCuratedVersions"
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:AbortMultipartUpload"
    ]

    resources = [
      "${aws_s3_bucket.mlops_data_lake.arn}/curated/loan_risk_dataset/versions/*"
    ]
  }

  # Writes version metadata; conditional writes protect existing records.
  statement {
    sid    = "WriteDatasetVersionMetadata"
    effect = "Allow"

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.mlops_data_lake.arn}/metadata/versions/loan_risk_dataset/*"
    ]
  }
}

# Attaches the restricted S3 policy to the dedicated Glue role.
resource "aws_iam_role_policy" "glue_etl_s3_access" {
  name   = "MLOpsGlueETLS3Access"
  role   = aws_iam_role.glue_etl.id
  policy = data.aws_iam_policy_document.glue_etl_s3_access.json
}

# Defines the managed AWS Glue Spark job.
resource "aws_glue_job" "curate_loan_dataset" {
  name        = "mlops-curate-loan-dataset"
  description = "Integrates standardized domains into a curated loan-risk dataset."

  role_arn = aws_iam_role.glue_etl.arn

  glue_version      = "5.0"
  worker_type       = "G.1X"
  number_of_workers = 2

  timeout     = 15
  max_retries = 0

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.mlops_data_lake.bucket}/${aws_s3_object.glue_curate_loan_dataset_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
  }

  depends_on = [
    aws_iam_role_policy_attachment.glue_etl_service_role,
    aws_iam_role_policy.glue_etl_s3_access
  ]
}

# ---------------------------------------------------------------------
# Glue Data Catalog - Curated Loan Risk Dataset
# ---------------------------------------------------------------------

resource "aws_glue_catalog_table" "curated_loan_risk_dataset" {
  name          = "curated_loan_risk_dataset"
  database_name = aws_glue_catalog_database.mlops_engineering_data_lake.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL                 = "TRUE"
    "skip.header.line.count" = "1"
  }

  storage_descriptor {
    location = "s3://${aws_s3_bucket.mlops_data_lake.bucket}/curated/loan_risk_dataset/versions/${var.curated_loan_risk_dataset_version}/"

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