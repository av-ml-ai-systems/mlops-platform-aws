# Module: financial_history.py
# Path: src/mlops_engineering_roadmap/data/validation/financial_history.py
# Purpose: Validate the Financial History domain dataset.
# Description: Implements schema, integrity, categorical, and value validation rules.


from collections.abc import Sequence

import pandas as pd

from mlops_engineering_roadmap.data.validation.models import ValidationResult
from mlops_engineering_roadmap.data.validation.validator import ValidationRule

REQUIRED_COLUMNS = (
    "customer_id",
    "default_history",
    "credit_history_length",
)

EXPECTED_DTYPES = {
    "customer_id": "str",
    "default_history": "str",
    "credit_history_length": "int64",
}

VALID_DEFAULT_HISTORY = {
    "Y",
    "N",
}


def validate_financial_schema(dataset: pd.DataFrame) -> ValidationResult:
    """Validate the required Financial History columns."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataset.columns]

    if missing_columns:
        return ValidationResult(
            rule="financial_schema",
            status="FAIL",
            severity="ERROR",
            message=f"Missing required columns: {missing_columns}.",
            affected_rows=len(dataset),
        )

    return ValidationResult(
        rule="financial_schema",
        status="PASS",
        severity="ERROR",
        message="All required Financial History columns are present.",
        affected_rows=0,
    )


def validate_financial_types(dataset: pd.DataFrame) -> ValidationResult:
    """Validate the expected Financial History data types."""
    mismatched_columns = []

    for column, expected_dtype in EXPECTED_DTYPES.items():
        if column not in dataset.columns:
            continue

        actual_dtype = str(dataset[column].dtype)

        if actual_dtype != expected_dtype:
            mismatched_columns.append(f"{column}: expected {expected_dtype}, found {actual_dtype}")

    if mismatched_columns:
        return ValidationResult(
            rule="financial_types",
            status="FAIL",
            severity="ERROR",
            message=f"Data type mismatches: {mismatched_columns}.",
            affected_rows=len(dataset),
        )

    return ValidationResult(
        rule="financial_types",
        status="PASS",
        severity="ERROR",
        message="Financial History data types are valid.",
        affected_rows=0,
    )


def validate_financial_customer_ids(
    dataset: pd.DataFrame,
) -> ValidationResult:
    """Validate Financial History customer identifiers."""
    if "customer_id" not in dataset.columns:
        return ValidationResult(
            rule="financial_customer_id_unique",
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
            rule="financial_customer_id_unique",
            status="FAIL",
            severity="ERROR",
            message="Financial History customer IDs must be present and unique.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="financial_customer_id_unique",
        status="PASS",
        severity="ERROR",
        message="All Financial History customer IDs are present and unique.",
        affected_rows=0,
    )


def validate_default_history(dataset: pd.DataFrame) -> ValidationResult:
    """Validate default history category values."""
    invalid_values = dataset["default_history"].isna() | ~dataset["default_history"].isin(
        VALID_DEFAULT_HISTORY
    )

    affected_rows = int(invalid_values.sum())

    if affected_rows:
        return ValidationResult(
            rule="default_history_values",
            status="FAIL",
            severity="ERROR",
            message="default_history must contain only Y or N.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="default_history_values",
        status="PASS",
        severity="ERROR",
        message="All default_history values are valid.",
        affected_rows=0,
    )


def validate_credit_history_length(
    dataset: pd.DataFrame,
) -> ValidationResult:
    """Validate credit history length values."""
    invalid_values = dataset["credit_history_length"].isna() | (
        dataset["credit_history_length"] < 0
    )

    affected_rows = int(invalid_values.sum())

    if affected_rows:
        return ValidationResult(
            rule="credit_history_length_values",
            status="FAIL",
            severity="ERROR",
            message="credit_history_length must be present and non-negative.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="credit_history_length_values",
        status="PASS",
        severity="ERROR",
        message="All credit_history_length values are valid.",
        affected_rows=0,
    )


FINANCIAL_HISTORY_VALIDATION_RULES: Sequence[ValidationRule] = (
    validate_financial_schema,
    validate_financial_types,
    validate_financial_customer_ids,
    validate_default_history,
    validate_credit_history_length,
)
