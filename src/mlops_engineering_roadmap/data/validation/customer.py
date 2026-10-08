# Module: customer.py
# Path: src/mlops_engineering_roadmap/data/validation/customer.py
# Purpose: Validate the Customer Profile domain dataset.
# Description: Implements schema, integrity, value, and employment consistency rules.

from collections.abc import Sequence

import pandas as pd

from mlops_engineering_roadmap.data.validation.models import ValidationResult
from mlops_engineering_roadmap.data.validation.validator import ValidationRule

REQUIRED_COLUMNS = (
    "customer_id",
    "age",
    "income",
    "home_ownership",
    "employment_length",
)

EXPECTED_DTYPES = {
    "customer_id": "str",
    "age": "int64",
    "income": "int64",
    "home_ownership": "str",
    "employment_length": "float64",
}

VALID_HOME_OWNERSHIP = {
    "RENT",
    "MORTGAGE",
    "OWN",
    "OTHER",
}


def validate_customer_schema(dataset: pd.DataFrame) -> ValidationResult:
    """Validate the required Customer Profile columns."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataset.columns]

    if missing_columns:
        return ValidationResult(
            rule="customer_schema",
            status="FAIL",
            severity="ERROR",
            message=f"Missing required columns: {missing_columns}.",
            affected_rows=len(dataset),
        )

    return ValidationResult(
        rule="customer_schema",
        status="PASS",
        severity="ERROR",
        message="All required Customer Profile columns are present.",
        affected_rows=0,
    )


def validate_customer_types(dataset: pd.DataFrame) -> ValidationResult:
    """Validate the expected Customer Profile data types."""
    mismatched_columns = []

    for column, expected_dtype in EXPECTED_DTYPES.items():
        if column not in dataset.columns:
            continue

        actual_dtype = str(dataset[column].dtype)

        if actual_dtype != expected_dtype:
            mismatched_columns.append(f"{column}: expected {expected_dtype}, found {actual_dtype}")

    if mismatched_columns:
        return ValidationResult(
            rule="customer_types",
            status="FAIL",
            severity="ERROR",
            message=f"Data type mismatches: {mismatched_columns}.",
            affected_rows=len(dataset),
        )

    return ValidationResult(
        rule="customer_types",
        status="PASS",
        severity="ERROR",
        message="Customer Profile data types are valid.",
        affected_rows=0,
    )


def validate_customer_ids(dataset: pd.DataFrame) -> ValidationResult:
    """Validate Customer Profile identifiers."""
    if "customer_id" not in dataset.columns:
        return ValidationResult(
            rule="customer_id_unique",
            status="FAIL",
            severity="ERROR",
            message="customer_id column is missing.",
            affected_rows=len(dataset),
        )

    missing_ids = dataset["customer_id"].isna()
    duplicate_ids = dataset["customer_id"].duplicated(keep=False)

    affected_rows = int((missing_ids | duplicate_ids).sum())

    if affected_rows:
        return ValidationResult(
            rule="customer_id_unique",
            status="FAIL",
            severity="ERROR",
            message="Customer IDs must be present and unique.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="customer_id_unique",
        status="PASS",
        severity="ERROR",
        message="All customer IDs are present and unique.",
        affected_rows=0,
    )


def validate_customer_values(dataset: pd.DataFrame) -> ValidationResult:
    """Validate basic Customer Profile value constraints."""
    invalid_age = dataset["age"].isna() | (dataset["age"] < 18)
    invalid_income = dataset["income"].isna() | (dataset["income"] < 0)
    invalid_home_ownership = dataset["home_ownership"].isna() | ~dataset["home_ownership"].isin(
        VALID_HOME_OWNERSHIP
    )

    invalid_rows = invalid_age | invalid_income | invalid_home_ownership
    affected_rows = int(invalid_rows.sum())

    if affected_rows:
        return ValidationResult(
            rule="customer_values",
            status="FAIL",
            severity="ERROR",
            message="Invalid Customer Profile values detected.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="customer_values",
        status="PASS",
        severity="ERROR",
        message="Customer Profile values satisfy basic constraints.",
        affected_rows=0,
    )


def validate_customer_employment_consistency(
    dataset: pd.DataFrame,
) -> ValidationResult:
    """Validate employment history against customer age."""
    if "employment_length" not in dataset.columns:
        return ValidationResult(
            rule="age_employment_consistency",
            status="FAIL",
            severity="ERROR",
            message="employment_length column is missing.",
            affected_rows=len(dataset),
        )

    valid_employment = dataset["employment_length"].notna()

    inconsistent = valid_employment & (dataset["employment_length"] > dataset["age"])

    affected_rows = int(inconsistent.sum())

    if affected_rows:
        return ValidationResult(
            rule="age_employment_consistency",
            status="FAIL",
            severity="ERROR",
            message="Employment history is inconsistent with customer age.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="age_employment_consistency",
        status="PASS",
        severity="ERROR",
        message="Employment history is consistent with customer age.",
        affected_rows=0,
    )


CUSTOMER_VALIDATION_RULES: Sequence[ValidationRule] = (
    validate_customer_schema,
    validate_customer_types,
    validate_customer_ids,
    validate_customer_values,
    validate_customer_employment_consistency,
)
