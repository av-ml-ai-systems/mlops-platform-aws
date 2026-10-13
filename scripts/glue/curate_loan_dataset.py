"""
Module:
    curate_loan_dataset.py

Path:
    scripts/glue/curate_loan_dataset.py

Purpose:
    Integrate standardized customer, financial history, and loan
    application datasets into a curated loan-risk dataset.

Description:
    Executes an AWS Glue ETL job that validates source keys, joins
    the three data domains, checks row-count consistency and target
    completeness, and writes the curated dataset to Amazon S3.
"""

import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

# ---------------------------------------------------------------------
# Job initialization
# ---------------------------------------------------------------------

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)


# ---------------------------------------------------------------------
# S3 configuration
# ---------------------------------------------------------------------

BUCKET = "mlops-engineering-data-lake-882507341805"

CUSTOMER_PATH = f"s3://{BUCKET}/standardized/customer/"
FINANCIAL_PATH = f"s3://{BUCKET}/standardized/financial_history/"
APPLICATION_PATH = f"s3://{BUCKET}/standardized/loan_application/"

OUTPUT_PATH = f"s3://{BUCKET}/curated/loan_risk_dataset/"


# ---------------------------------------------------------------------
# Read standardized datasets
# ---------------------------------------------------------------------

customer = spark.read.option("header", "true").option("inferSchema", "true").csv(CUSTOMER_PATH)

financial = spark.read.option("header", "true").option("inferSchema", "true").csv(FINANCIAL_PATH)

applications = (
    spark.read.option("header", "true").option("inferSchema", "true").csv(APPLICATION_PATH)
)


# ---------------------------------------------------------------------
# Validate source keys
# ---------------------------------------------------------------------


def validate_keys(
    dataframe: DataFrame,
    key: str,
    dataset_name: str,
) -> None:
    """Reject datasets containing null or duplicate key values."""
    if dataframe.filter(F.col(key).isNull()).limit(1).count() > 0:
        raise ValueError(f"{dataset_name}: null {key} detected")

    duplicate_exists = (
        dataframe.groupBy(key).count().filter(F.col("count") > 1).limit(1).count() > 0
    )

    if duplicate_exists:
        raise ValueError(f"{dataset_name}: duplicate {key} detected")


validate_keys(customer, "customer_id", "customer")
validate_keys(financial, "customer_id", "financial_history")
validate_keys(applications, "application_id", "loan_application")

if applications.filter(F.col("customer_id").isNull()).limit(1).count() > 0:
    raise ValueError("loan_application: null customer_id detected")


# ---------------------------------------------------------------------
# Integrate the three domains
# ---------------------------------------------------------------------

application_count = applications.count()

curated = (
    applications.alias("l")
    .join(
        customer.alias("c"),
        F.col("l.customer_id") == F.col("c.customer_id"),
        "inner",
    )
    .join(
        financial.alias("f"),
        F.col("l.customer_id") == F.col("f.customer_id"),
        "inner",
    )
    .select(
        F.col("l.application_id"),
        F.col("l.customer_id"),
        F.col("l.loan_amount"),
        F.col("l.loan_purpose"),
        F.col("l.risk_grade"),
        F.col("l.loan_interest_rate"),
        F.col("l.loan_income_ratio"),
        F.col("l.loan_outcome"),
        F.col("c.age"),
        F.col("c.income"),
        F.col("c.home_ownership"),
        F.col("c.employment_length"),
        F.col("f.default_history"),
        F.col("f.credit_history_length"),
    )
)

curated_count = curated.count()

if curated_count != application_count:
    raise ValueError(
        f"Join changed application count: input={application_count}, curated={curated_count}"
    )

if curated.filter(F.col("loan_outcome").isNull()).limit(1).count() > 0:
    raise ValueError("Curated dataset contains null loan_outcome values")


# ---------------------------------------------------------------------
# Persist curated dataset
# ---------------------------------------------------------------------

(
    curated.write.mode("overwrite")
    .option("header", "true")
    .option("quoteAll", "true")
    .csv(OUTPUT_PATH)
)

print(f"Input applications: {application_count}")
print(f"Curated applications: {curated_count}")
print(f"Curated output: {OUTPUT_PATH}")

job.commit()
