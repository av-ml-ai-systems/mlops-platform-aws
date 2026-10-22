# Module: curate_loan_dataset.py
# Path: scripts/glue/curate_loan_dataset.py
# Purpose: Curate, validate, and version the loan risk dataset.
# Description: Publishes validated datasets with integrity hashes and traceable metadata.

"""Curate, validate, and version the loan risk dataset in AWS Glue."""

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.column import Column
from pyspark.sql.types import (
    DecimalType,
    DoubleType,
    FloatType,
    IntegralType,
    NumericType,
    StringType,
)

ValidationStatus = Literal["PASS", "FAIL"]

REQUIRED_COLUMNS = (
    "application_id",
    "customer_id",
    "loan_amount",
    "loan_purpose",
    "risk_grade",
    "loan_interest_rate",
    "loan_income_ratio",
    "loan_outcome",
    "age",
    "income",
    "home_ownership",
    "employment_length",
    "default_history",
    "credit_history_length",
)

NULLABLE_COLUMNS = {
    "loan_interest_rate",
    "employment_length",
}

STRING_COLUMNS = {
    "application_id",
    "customer_id",
    "loan_purpose",
    "risk_grade",
    "home_ownership",
    "default_history",
}

INTEGRAL_COLUMNS = {
    "loan_amount",
    "loan_outcome",
    "age",
    "income",
    "credit_history_length",
}

DECIMAL_COLUMNS = {
    "loan_interest_rate",
    "loan_income_ratio",
    "employment_length",
}

NUMERIC_COLUMNS = INTEGRAL_COLUMNS | DECIMAL_COLUMNS

VALID_LOAN_PURPOSES = {
    "EDUCATION",
    "MEDICAL",
    "VENTURE",
    "PERSONAL",
    "DEBTCONSOLIDATION",
    "HOMEIMPROVEMENT",
}

VALID_RISK_GRADES = {"A", "B", "C", "D", "E", "F", "G"}
VALID_HOME_OWNERSHIP = {"RENT", "OWN", "MORTGAGE", "OTHER"}
VALID_DEFAULT_HISTORY = {"Y", "N"}
VALID_LOAN_OUTCOMES = {0, 1}

DATASET_NAME = "loan_risk_dataset"
PIPELINE_NAME = "scripts/glue/curate_loan_dataset.py"
METADATA_PREFIX = "metadata/versions/loan_risk_dataset"


@dataclass(frozen=True)
class SparkValidationResult:
    """Represent one curated dataset validation result."""

    rule: str
    status: ValidationStatus
    message: str
    affected_rows: int


def _result(
    rule: str,
    valid: bool,
    message: str,
    affected_rows: int = 0,
) -> SparkValidationResult:
    """Create a standardized validation result."""
    return SparkValidationResult(
        rule=rule,
        status="PASS" if valid else "FAIL",
        message=message,
        affected_rows=affected_rows,
    )


def _count_invalid(dataframe: DataFrame, condition: Column) -> int:
    """Count rows for which a validation condition is true."""
    return int(dataframe.filter(F.coalesce(condition, F.lit(False))).count())


def validate_curated_schema(dataframe: DataFrame) -> SparkValidationResult:
    """Require the expected curated columns and reject unexpected columns."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(dataframe.columns))
    unexpected = sorted(set(dataframe.columns) - set(REQUIRED_COLUMNS))
    valid = not missing and not unexpected

    return _result(
        "curated_schema",
        valid,
        f"Missing columns: {missing}; unexpected columns: {unexpected}.",
        dataframe.count() if not valid else 0,
    )


def validate_curated_types(dataframe: DataFrame) -> SparkValidationResult:
    """Validate string, integral, and decimal-compatible Spark data types."""
    fields = {field.name: field.dataType for field in dataframe.schema.fields}
    mismatches: list[str] = []

    for column in sorted(STRING_COLUMNS):
        if column not in fields:
            mismatches.append(f"{column}: missing")
        elif not isinstance(fields[column], StringType):
            mismatches.append(f"{column}: expected string, found {fields[column].simpleString()}")

    for column in sorted(INTEGRAL_COLUMNS):
        if column not in fields:
            mismatches.append(f"{column}: missing")
        elif not isinstance(fields[column], IntegralType):
            mismatches.append(f"{column}: expected integral, found {fields[column].simpleString()}")

    decimal_types = (FloatType, DoubleType, DecimalType)
    for column in sorted(DECIMAL_COLUMNS):
        if column not in fields:
            mismatches.append(f"{column}: missing")
        elif not isinstance(fields[column], decimal_types):
            mismatches.append(
                f"{column}: expected decimal-compatible, found {fields[column].simpleString()}"
            )

    valid = not mismatches
    return _result(
        "curated_types",
        valid,
        f"Type mismatches: {mismatches}.",
        dataframe.count() if not valid else 0,
    )


def validate_curated_required_values(
    dataframe: DataFrame,
) -> SparkValidationResult:
    """Reject nulls in required fields while permitting approved nullable fields."""
    required_non_null = [column for column in REQUIRED_COLUMNS if column not in NULLABLE_COLUMNS]
    missing = sorted(set(required_non_null) - set(dataframe.columns))

    available = [column for column in required_non_null if column in dataframe.columns]
    if missing:
        return _result(
            "curated_required_values",
            False,
            f"Missing required non-null columns: {missing}.",
            dataframe.count(),
        )

    if not available:
        return _result(
            "curated_required_values",
            False,
            "No non-nullable required columns are available.",
            dataframe.count(),
        )

    condition = F.lit(False)
    for column in available:
        condition = condition | F.col(column).isNull()

    affected = _count_invalid(dataframe, condition)
    return _result(
        "curated_required_values",
        affected == 0,
        (
            "Non-nullable required fields must not contain null values. "
            f"Nullable columns: {sorted(NULLABLE_COLUMNS)}."
        ),
        affected,
    )


def validate_curated_identifiers(
    dataframe: DataFrame,
) -> SparkValidationResult:
    """Require present customer IDs and unique, non-null application IDs."""
    required = {"application_id", "customer_id"}
    missing = sorted(required - set(dataframe.columns))

    if missing:
        return _result(
            "curated_identifiers",
            False,
            f"Missing identifier columns: {missing}.",
            dataframe.count(),
        )

    duplicate_ids = (
        dataframe.groupBy("application_id")
        .count()
        .filter(F.col("application_id").isNotNull() & (F.col("count") > 1))
        .select("application_id")
    )

    duplicate_marker = duplicate_ids.withColumn(
        "_duplicate_application_id",
        F.lit(True),
    )

    checked = dataframe.join(
        duplicate_marker,
        on="application_id",
        how="left",
    )

    condition = (
        F.col("application_id").isNull()
        | F.col("customer_id").isNull()
        | F.col("_duplicate_application_id").isNotNull()
    )
    affected = _count_invalid(checked, condition)

    return _result(
        "curated_identifiers",
        affected == 0,
        "Application IDs must be present and unique; customer IDs must be present.",
        affected,
    )


def validate_curated_numeric_values(
    dataframe: DataFrame,
) -> SparkValidationResult:
    """Validate numeric types, finite values, nullability, and domain constraints."""
    missing = sorted(NUMERIC_COLUMNS - set(dataframe.columns))
    if missing:
        return _result(
            "curated_numeric_values",
            False,
            f"Missing numeric columns: {missing}.",
            dataframe.count(),
        )

    fields = {field.name: field.dataType for field in dataframe.schema.fields}
    non_numeric = sorted(
        column for column in NUMERIC_COLUMNS if not isinstance(fields[column], NumericType)
    )
    if non_numeric:
        return _result(
            "curated_numeric_values",
            False,
            f"Non-numeric columns detected: {non_numeric}.",
            dataframe.count(),
        )

    invalid = F.lit(False)

    for column in NUMERIC_COLUMNS:
        value = F.col(column).cast("double")

        if column not in NULLABLE_COLUMNS:
            invalid = invalid | F.col(column).isNull()

        invalid = invalid | F.isnan(value)
        invalid = invalid | value.isin(float("inf"), float("-inf"))

    invalid = invalid | (F.col("loan_amount") <= 0)
    invalid = invalid | (F.col("loan_interest_rate") < 0)
    invalid = invalid | (F.col("loan_income_ratio") < 0)
    invalid = invalid | (F.col("loan_income_ratio") > 1)
    invalid = invalid | (F.col("age") < 18)
    invalid = invalid | (F.col("income") < 0)
    invalid = invalid | (F.col("employment_length") < 0)
    invalid = invalid | (F.col("credit_history_length") < 0)
    invalid = invalid | (F.col("employment_length") > F.col("age"))

    affected = _count_invalid(dataframe, invalid)

    return _result(
        "curated_numeric_values",
        affected == 0,
        (
            "Invalid numeric values or domain constraints detected. "
            f"Nullable numeric columns: {sorted(NULLABLE_COLUMNS)}."
        ),
        affected,
    )


def _validate_categories(
    dataframe: DataFrame,
    column: str,
    valid_values: set[str] | set[int],
    rule: str,
) -> SparkValidationResult:
    """Reject null and out-of-domain values in a categorical column."""
    if column not in dataframe.columns:
        return _result(
            rule,
            False,
            f"Required column {column!r} is missing.",
            dataframe.count(),
        )

    condition = F.col(column).isNull() | ~F.col(column).isin(*sorted(valid_values))
    affected = _count_invalid(dataframe, condition)

    return _result(
        rule,
        affected == 0,
        f"Invalid or null values found in {column}.",
        affected,
    )


def validate_curated_loan_purpose(dataframe: DataFrame) -> SparkValidationResult:
    """Validate loan purpose categories."""
    return _validate_categories(
        dataframe,
        "loan_purpose",
        VALID_LOAN_PURPOSES,
        "curated_loan_purpose",
    )


def validate_curated_risk_grade(dataframe: DataFrame) -> SparkValidationResult:
    """Validate risk grade categories."""
    return _validate_categories(
        dataframe,
        "risk_grade",
        VALID_RISK_GRADES,
        "curated_risk_grade",
    )


def validate_curated_home_ownership(
    dataframe: DataFrame,
) -> SparkValidationResult:
    """Validate home ownership categories."""
    return _validate_categories(
        dataframe,
        "home_ownership",
        VALID_HOME_OWNERSHIP,
        "curated_home_ownership",
    )


def validate_curated_default_history(
    dataframe: DataFrame,
) -> SparkValidationResult:
    """Validate default history categories."""
    return _validate_categories(
        dataframe,
        "default_history",
        VALID_DEFAULT_HISTORY,
        "curated_default_history",
    )


def validate_curated_target(dataframe: DataFrame) -> SparkValidationResult:
    """Require binary, non-null loan outcomes."""
    return _validate_categories(
        dataframe,
        "loan_outcome",
        VALID_LOAN_OUTCOMES,
        "curated_loan_target",
    )


CURATED_LOAN_RISK_VALIDATION_RULES = (
    validate_curated_schema,
    validate_curated_types,
    validate_curated_required_values,
    validate_curated_identifiers,
    validate_curated_numeric_values,
    validate_curated_loan_purpose,
    validate_curated_risk_grade,
    validate_curated_home_ownership,
    validate_curated_default_history,
    validate_curated_target,
)


def validate_curated_dataset(
    dataframe: DataFrame,
) -> tuple[SparkValidationResult, ...]:
    """Run every quality rule and return the complete validation report."""
    return tuple(rule(dataframe) for rule in CURATED_LOAN_RISK_VALIDATION_RULES)


def assert_curated_dataset_valid(
    dataframe: DataFrame,
) -> tuple[SparkValidationResult, ...]:
    """Reject a curated dataset when any quality rule fails."""
    results = validate_curated_dataset(dataframe)
    failures = [result for result in results if result.status == "FAIL"]

    if failures:
        details = "; ".join(
            f"{result.rule}: {result.message} (affected_rows={result.affected_rows})"
            for result in failures
        )
        raise ValueError(f"Curated dataset quality gate failed: {details}")

    return results


def _validate_dataset_version(version: str) -> str:
    """Require a safe version identifier for use in S3 object keys."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", version):
        raise ValueError(
            "Dataset version must be 1-64 characters using letters, digits, "
            "periods, underscores, or hyphens."
        )

    if version in {".", ".."}:
        raise ValueError("Dataset version cannot be a relative path.")

    return version


def _assert_version_available(
    s3_client: Any,
    bucket: str,
    output_prefix: str,
    metadata_key: str,
) -> None:
    """Reject versions whose output prefix or metadata object already exists."""
    output_objects = s3_client.list_objects_v2(
        Bucket=bucket,
        Prefix=output_prefix,
        MaxKeys=1,
    )

    if output_objects.get("Contents"):
        raise FileExistsError(
            f"Dataset output version already exists: s3://{bucket}/{output_prefix}"
        )

    metadata_objects = s3_client.list_objects_v2(
        Bucket=bucket,
        Prefix=metadata_key,
        MaxKeys=1,
    )

    if metadata_objects.get("Contents"):
        raise FileExistsError(
            f"Dataset metadata version already exists: s3://{bucket}/{metadata_key}"
        )


def _calculate_s3_artifact_manifest(
    s3_client: Any,
    bucket: str,
    output_prefix: str,
) -> tuple[str, list[dict[str, str]]]:
    """Hash published CSV objects and create a deterministic manifest digest."""
    paginator = s3_client.get_paginator("list_objects_v2")
    objects: list[dict[str, str]] = []

    for page in paginator.paginate(Bucket=bucket, Prefix=output_prefix):
        for item in page.get("Contents", []):
            key = item["Key"]
            if key.endswith(".csv"):
                objects.append({"key": key, "sha256": ""})

    objects.sort(key=lambda item: item["key"])

    if not objects:
        raise RuntimeError(f"No CSV artifact files found under s3://{bucket}/{output_prefix}")

    manifest_digest = hashlib.sha256()

    for item in objects:
        response = s3_client.get_object(Bucket=bucket, Key=item["key"])
        file_digest = hashlib.sha256()
        body = response["Body"]

        try:
            for chunk in iter(lambda: body.read(1024 * 1024), b""):
                file_digest.update(chunk)
        finally:
            body.close()

        item["sha256"] = file_digest.hexdigest()
        manifest_digest.update(item["key"].encode("utf-8"))
        manifest_digest.update(b"\0")
        manifest_digest.update(item["sha256"].encode("ascii"))
        manifest_digest.update(b"\n")

    return manifest_digest.hexdigest(), objects


def _write_dataset_metadata(
    s3_client: Any,
    bucket: str,
    metadata_key: str,
    metadata: dict[str, Any],
) -> None:
    """Write the completed dataset metadata as a JSON S3 object."""
    body = json.dumps(
        metadata,
        indent=2,
        sort_keys=True,
    ).encode("utf-8")

    s3_client.put_object(
        Bucket=bucket,
        Key=metadata_key,
        Body=body,
        ContentType="application/json",
    )


def main() -> None:
    """Execute the AWS Glue curation and versioned publication job."""
    import boto3
    from awsglue.context import GlueContext
    from awsglue.job import Job
    from awsglue.utils import getResolvedOptions
    from pyspark import SparkContext

    args = getResolvedOptions(sys.argv, ["JOB_NAME", "dataset_version"])
    version = _validate_dataset_version(args["dataset_version"])

    sc = SparkContext.getOrCreate()
    glue_context = GlueContext(sc)
    spark = glue_context.spark_session

    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)

    bucket = "mlops-engineering-data-lake-882507341805"

    customer_path = f"s3://{bucket}/standardized/customer/"
    financial_path = f"s3://{bucket}/standardized/financial_history/"
    application_path = f"s3://{bucket}/standardized/loan_application/"

    output_prefix = f"curated/loan_risk_dataset/versions/{version}/"
    output_path = f"s3://{bucket}/{output_prefix}"
    metadata_key = f"{METADATA_PREFIX}/{version}.json"

    s3_client = boto3.client("s3")
    _assert_version_available(
        s3_client,
        bucket,
        output_prefix,
        metadata_key,
    )

    customer = spark.read.option("header", "true").option("inferSchema", "true").csv(customer_path)
    financial = (
        spark.read.option("header", "true").option("inferSchema", "true").csv(financial_path)
    )
    applications = (
        spark.read.option("header", "true").option("inferSchema", "true").csv(application_path)
    )

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

    validation_results = assert_curated_dataset_valid(curated)

    for result in validation_results:
        print(
            f"Validation {result.rule}: {result.status}; "
            f"affected_rows={result.affected_rows}; {result.message}"
        )

    (
        curated.write.mode("errorifexists")
        .option("header", "true")
        .option("quoteAll", "true")
        .csv(output_path)
    )

    artifact_sha256, artifact_files = _calculate_s3_artifact_manifest(
        s3_client,
        bucket,
        output_prefix,
    )

    metadata = {
        "dataset_name": DATASET_NAME,
        "version": version,
        "status": "curated",
        "created_at": datetime.now(UTC).isoformat(),
        "source": {
            "customer": customer_path,
            "financial_history": financial_path,
            "loan_application": application_path,
        },
        "pipeline": PIPELINE_NAME,
        "artifact": {
            "format": "csv",
            "rows": curated_count,
            "columns": list(curated.columns),
            "s3_uri": output_path,
            "sha256": artifact_sha256,
            "sha256_method": "SHA-256 manifest of sorted CSV object keys and hashes",
            "files": artifact_files,
        },
        "validation": {
            "status": "PASS",
            "rules_passed": len(validation_results),
            "rules_failed": 0,
        },
    }

    _write_dataset_metadata(
        s3_client,
        bucket,
        metadata_key,
        metadata,
    )

    print(f"Input applications: {application_count}")
    print(f"Curated applications: {curated_count}")
    print(f"Dataset version: {version}")
    print(f"Curated output: {output_path}")
    print(f"Artifact SHA-256 manifest: {artifact_sha256}")
    print(f"Metadata: s3://{bucket}/{metadata_key}")

    job.commit()


if __name__ == "__main__":
    main()
