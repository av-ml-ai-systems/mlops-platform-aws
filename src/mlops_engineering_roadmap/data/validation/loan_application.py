# Module: loan_application.py
# Path: src/mlops_engineering_roadmap/data/validation/loan_application.py
# Purpose: Validate the Loan Application domain dataset.
# Description: Implements schema, integrity, categorical, target, and value validation rules.


from collections.abc import Sequence

import pandas as pd

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
)

EXPECTED_DTYPES = {
    "application_id": "str",
    "customer_id": "str",
    "loan_amount": "int64",
    "loan_purpose": "str",
    "risk_grade": "str",
    "loan_interest_rate": "float64",
    "loan_income_ratio": "float64",
    "loan_outcome": "int64",
}

VALID_LOAN_PURPOSES = {
    "EDUCATION",
    "MEDICAL",
    "VENTURE",
    "PERSONAL",
    "DEBTCONSOLIDATION",
    "HOMEIMPROVEMENT",
}

VALID_RISK_GRADES = {
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
}

VALID_LOAN_OUTCOMES = {
    0,
    1,
}


def validate_loan_schema(dataset: pd.DataFrame) -> ValidationResult:
    """Validate the required Loan Application columns."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataset.columns]

    if missing_columns:
        return ValidationResult(
            rule="loan_schema",
            status="FAIL",
            severity="ERROR",
            message=f"Missing required columns: {missing_columns}.",
            affected_rows=len(dataset),
        )

    return ValidationResult(
        rule="loan_schema",
        status="PASS",
        severity="ERROR",
        message="All required Loan Application columns are present.",
        affected_rows=0,
    )


def validate_loan_types(dataset: pd.DataFrame) -> ValidationResult:
    """Validate the expected Loan Application data types."""
    mismatched_columns = []

    for column, expected_dtype in EXPECTED_DTYPES.items():
        if column not in dataset.columns:
            continue

        actual_dtype = str(dataset[column].dtype)

        if actual_dtype != expected_dtype:
            mismatched_columns.append(f"{column}: expected {expected_dtype}, found {actual_dtype}")

    if mismatched_columns:
        return ValidationResult(
            rule="loan_types",
            status="FAIL",
            severity="ERROR",
            message=f"Data type mismatches: {mismatched_columns}.",
            affected_rows=len(dataset),
        )

    return ValidationResult(
        rule="loan_types",
        status="PASS",
        severity="ERROR",
        message="Loan Application data types are valid.",
        affected_rows=0,
    )


def validate_application_ids(dataset: pd.DataFrame) -> ValidationResult:
    """Validate Loan Application identifiers."""
    if "application_id" not in dataset.columns:
        return ValidationResult(
            rule="application_id_unique",
            status="FAIL",
            severity="ERROR",
            message="application_id column is missing.",
            affected_rows=len(dataset),
        )

    missing_ids = dataset["application_id"].isna()
    duplicate_ids = dataset["application_id"].duplicated(keep=False)

    affected_rows = int((missing_ids | duplicate_ids).sum())

    if affected_rows:
        return ValidationResult(
            rule="application_id_unique",
            status="FAIL",
            severity="ERROR",
            message="Application IDs must be present and unique.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="application_id_unique",
        status="PASS",
        severity="ERROR",
        message="All application IDs are present and unique.",
        affected_rows=0,
    )


def validate_loan_customer_ids(dataset: pd.DataFrame) -> ValidationResult:
    """Validate that Loan Application customer IDs are present."""
    if "customer_id" not in dataset.columns:
        return ValidationResult(
            rule="loan_customer_id_present",
            status="FAIL",
            severity="ERROR",
            message="customer_id column is missing.",
            affected_rows=len(dataset),
        )

    missing_ids = dataset["customer_id"].isna()
    affected_rows = int(missing_ids.sum())

    if affected_rows:
        return ValidationResult(
            rule="loan_customer_id_present",
            status="FAIL",
            severity="ERROR",
            message="Loan Application customer IDs must be present.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="loan_customer_id_present",
        status="PASS",
        severity="ERROR",
        message="All Loan Application customer IDs are present.",
        affected_rows=0,
    )


def validate_loan_values(dataset: pd.DataFrame) -> ValidationResult:
    """Validate basic Loan Application numeric constraints."""
    invalid_amount = dataset["loan_amount"].isna() | (dataset["loan_amount"] <= 0)

    invalid_ratio = dataset["loan_income_ratio"].isna() | (
        (dataset["loan_income_ratio"] < 0) | (dataset["loan_income_ratio"] > 1)
    )

    invalid_rows = invalid_amount | invalid_ratio
    affected_rows = int(invalid_rows.sum())

    if affected_rows:
        return ValidationResult(
            rule="loan_values",
            status="FAIL",
            severity="ERROR",
            message="Invalid loan amount or loan income ratio detected.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="loan_values",
        status="PASS",
        severity="ERROR",
        message="Loan amount and loan income ratio values are valid.",
        affected_rows=0,
    )


def validate_loan_purpose(dataset: pd.DataFrame) -> ValidationResult:
    """Validate Loan Application purpose categories."""
    invalid_values = dataset["loan_purpose"].isna() | ~dataset["loan_purpose"].isin(
        VALID_LOAN_PURPOSES
    )

    affected_rows = int(invalid_values.sum())

    if affected_rows:
        return ValidationResult(
            rule="loan_purpose_values",
            status="FAIL",
            severity="ERROR",
            message="Invalid loan purpose categories detected.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="loan_purpose_values",
        status="PASS",
        severity="ERROR",
        message="All loan purpose categories are valid.",
        affected_rows=0,
    )


def validate_risk_grade(dataset: pd.DataFrame) -> ValidationResult:
    """Validate Loan Application risk grade categories."""
    invalid_values = dataset["risk_grade"].isna() | ~dataset["risk_grade"].isin(VALID_RISK_GRADES)

    affected_rows = int(invalid_values.sum())

    if affected_rows:
        return ValidationResult(
            rule="risk_grade_values",
            status="FAIL",
            severity="ERROR",
            message="Invalid risk grade categories detected.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="risk_grade_values",
        status="PASS",
        severity="ERROR",
        message="All risk grade categories are valid.",
        affected_rows=0,
    )


def validate_loan_target(dataset: pd.DataFrame) -> ValidationResult:
    """Validate Loan Application target values."""
    invalid_values = dataset["loan_outcome"].isna() | ~dataset["loan_outcome"].isin(
        VALID_LOAN_OUTCOMES
    )

    affected_rows = int(invalid_values.sum())

    if affected_rows:
        return ValidationResult(
            rule="loan_outcome_values",
            status="FAIL",
            severity="ERROR",
            message="loan_outcome must contain only 0 or 1.",
            affected_rows=affected_rows,
        )

    return ValidationResult(
        rule="loan_outcome_values",
        status="PASS",
        severity="ERROR",
        message="All loan outcome values are valid.",
        affected_rows=0,
    )


LOAN_APPLICATION_VALIDATION_RULES: Sequence[ValidationRule] = (
    validate_loan_schema,
    validate_loan_types,
    validate_application_ids,
    validate_loan_customer_ids,
    validate_loan_values,
    validate_loan_purpose,
    validate_risk_grade,
    validate_loan_target,
)
