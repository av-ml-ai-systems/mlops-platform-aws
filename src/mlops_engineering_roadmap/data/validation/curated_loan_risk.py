# Module: curated_loan_risk.py
# Path: src/mlops_engineering_roadmap/data/validation/curated_loan_risk.py
# Purpose: Validate the curated loan risk dataset.
# Description: Validates schema, types, identifiers, numeric values, categories, and target.

"""Validation rules for the curated loan risk dataset."""

from collections.abc import Sequence

import pandas as pd
from pandas.api.types import is_numeric_dtype

from mlops_engineering_roadmap.data.validation.models import ValidationResult
from mlops_engineering_roadmap.data.validation.validator import ValidationRule

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

EXPECTED_DTYPES = {
    "application_id": "str",
    "customer_id": "str",
    "loan_amount": "int64",
    "loan_purpose": "str",
    "risk_grade": "str",
    "loan_interest_rate": "float64",
    "loan_income_ratio": "float64",
    "loan_outcome": "int64",
    "age": "int64",
    "income": "int64",
    "home_ownership": "str",
    "employment_length": "float64",
    "default_history": "str",
    "credit_history_length": "int64",
}

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


def _result(
    rule: str,
    valid: bool,
    message: str,
    affected_rows: int = 0,
) -> ValidationResult:
    """Build a standardized validation result."""
    return ValidationResult(
        rule=rule,
        status="PASS" if valid else "FAIL",
        severity="ERROR",
        message=message,
        affected_rows=affected_rows,
    )


def validate_curated_schema(dataset: pd.DataFrame) -> ValidationResult:
    """Validate required columns and reject unexpected columns."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(dataset.columns))
    unexpected = sorted(set(dataset.columns) - set(REQUIRED_COLUMNS))
    valid = not missing and not unexpected

    return _result(
        "curated_schema",
        valid,
        f"Missing columns: {missing}; unexpected columns: {unexpected}.",
        len(dataset) if not valid else 0,
    )


def validate_curated_types(dataset: pd.DataFrame) -> ValidationResult:
    """Validate expected column data types without raising on missing columns."""
    mismatches = [
        f"{column}: expected {expected}, found {dataset[column].dtype}"
        for column, expected in EXPECTED_DTYPES.items()
        if column in dataset.columns and str(dataset[column].dtype) != expected
    ]
    missing = sorted(set(EXPECTED_DTYPES) - set(dataset.columns))
    valid = not mismatches and not missing

    return _result(
        "curated_types",
        valid,
        f"Type mismatches: {mismatches}; missing columns: {missing}.",
        len(dataset) if not valid else 0,
    )


def validate_curated_required_values(dataset: pd.DataFrame) -> ValidationResult:
    """Reject nulls except in explicitly nullable curated dataset columns."""
    required_non_null = [column for column in REQUIRED_COLUMNS if column not in NULLABLE_COLUMNS]
    columns = [column for column in required_non_null if column in dataset.columns]

    if not columns:
        return _result(
            "curated_required_values",
            False,
            "No non-nullable required columns are available for validation.",
            len(dataset),
        )

    invalid_rows = dataset[columns].isna().any(axis=1)
    affected = int(invalid_rows.sum())

    return _result(
        "curated_required_values",
        affected == 0,
        (
            "Non-nullable required fields must not contain null values. "
            f"Nullable columns: {sorted(NULLABLE_COLUMNS)}."
        ),
        affected,
    )


def validate_curated_identifiers(dataset: pd.DataFrame) -> ValidationResult:
    """Require present, unique application IDs and present customer IDs."""
    required = {"application_id", "customer_id"}
    missing = sorted(required - set(dataset.columns))
    if missing:
        return _result(
            "curated_identifiers",
            False,
            f"Missing identifier columns: {missing}.",
            len(dataset),
        )

    invalid_rows = (
        dataset["application_id"].isna()
        | dataset["application_id"].duplicated(keep=False)
        | dataset["customer_id"].isna()
    )
    affected = int(invalid_rows.sum())

    return _result(
        "curated_identifiers",
        affected == 0,
        "Application IDs must be present and unique; customer IDs must be present.",
        affected,
    )


def validate_curated_numeric_values(dataset: pd.DataFrame) -> ValidationResult:
    """Validate numeric constraints while permitting approved null values."""
    required = {
        "loan_amount",
        "loan_interest_rate",
        "loan_income_ratio",
        "age",
        "income",
        "employment_length",
        "credit_history_length",
    }
    missing = sorted(required - set(dataset.columns))
    if missing:
        return _result(
            "curated_numeric_values",
            False,
            f"Missing numeric columns: {missing}.",
            len(dataset),
        )

    non_numeric = sorted(column for column in required if not is_numeric_dtype(dataset[column]))
    if non_numeric:
        return _result(
            "curated_numeric_values",
            False,
            f"Non-numeric columns detected: {non_numeric}.",
            len(dataset),
        )

    invalid = pd.Series(False, index=dataset.index)

    for column in required:
        values = dataset[column]
        null_values = values.isna()

        if column not in NULLABLE_COLUMNS:
            invalid |= null_values

        non_finite = values.map(
            lambda value: pd.notna(value) and value in (float("inf"), float("-inf"))
        )
        invalid |= non_finite

    invalid |= (
        (dataset["loan_amount"] <= 0)
        | (dataset["loan_interest_rate"] < 0)
        | (dataset["loan_income_ratio"] < 0)
        | (dataset["loan_income_ratio"] > 1)
        | (dataset["age"] < 18)
        | (dataset["income"] < 0)
        | (dataset["employment_length"] < 0)
        | (dataset["credit_history_length"] < 0)
        | (dataset["employment_length"] > dataset["age"])
    )

    affected = int(invalid.sum())

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
    dataset: pd.DataFrame,
    column: str,
    valid_values: set[str] | set[int],
    rule: str,
) -> ValidationResult:
    """Validate a categorical column, handling missing columns safely."""
    if column not in dataset.columns:
        return _result(
            rule,
            False,
            f"Required column {column!r} is missing.",
            len(dataset),
        )

    invalid = dataset[column].isna() | ~dataset[column].isin(valid_values)
    affected = int(invalid.sum())

    return _result(
        rule,
        affected == 0,
        f"Invalid or null values found in {column}.",
        affected,
    )


def validate_curated_loan_purpose(dataset: pd.DataFrame) -> ValidationResult:
    """Validate loan purpose categories."""
    return _validate_categories(
        dataset, "loan_purpose", VALID_LOAN_PURPOSES, "curated_loan_purpose"
    )


def validate_curated_risk_grade(dataset: pd.DataFrame) -> ValidationResult:
    """Validate risk grade categories."""
    return _validate_categories(dataset, "risk_grade", VALID_RISK_GRADES, "curated_risk_grade")


def validate_curated_home_ownership(dataset: pd.DataFrame) -> ValidationResult:
    """Validate home ownership categories."""
    return _validate_categories(
        dataset,
        "home_ownership",
        VALID_HOME_OWNERSHIP,
        "curated_home_ownership",
    )


def validate_curated_default_history(dataset: pd.DataFrame) -> ValidationResult:
    """Validate default history categories."""
    return _validate_categories(
        dataset,
        "default_history",
        VALID_DEFAULT_HISTORY,
        "curated_default_history",
    )


def validate_curated_target(dataset: pd.DataFrame) -> ValidationResult:
    """Require the target to contain only binary outcomes."""
    return _validate_categories(
        dataset,
        "loan_outcome",
        VALID_LOAN_OUTCOMES,
        "curated_loan_target",
    )


CURATED_LOAN_RISK_VALIDATION_RULES: Sequence[ValidationRule] = (
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
