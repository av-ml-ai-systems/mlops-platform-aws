# Module: test_curated_loan_risk.py
# Path: tests/data/test_curated_loan_risk.py
# Purpose: Test validation rules for the curated loan risk dataset.
# Description: Tests schema, types, required values, identifiers, numeric constraints,
# categories, nullable fields, and aggregate validation.

"""Unit tests for curated loan risk dataset validation."""

import pandas as pd
import pytest

from mlops_engineering_roadmap.data.validation.curated_loan_risk import (
    CURATED_LOAN_RISK_VALIDATION_RULES,
    validate_curated_identifiers,
    validate_curated_loan_purpose,
    validate_curated_numeric_values,
    validate_curated_required_values,
    validate_curated_schema,
    validate_curated_target,
    validate_curated_types,
)
from mlops_engineering_roadmap.data.validation.validator import validate_dataset


@pytest.fixture
def valid_dataset() -> pd.DataFrame:
    """Build a valid dataset with the expected column types and values."""
    return pd.DataFrame(
        {
            "application_id": pd.Series(["APP001", "APP002"], dtype="str"),
            "customer_id": pd.Series(["CUST001", "CUST002"], dtype="str"),
            "loan_amount": pd.Series([10000, 20000], dtype="int64"),
            "loan_purpose": pd.Series(["EDUCATION", "MEDICAL"], dtype="str"),
            "risk_grade": pd.Series(["A", "B"], dtype="str"),
            "loan_interest_rate": pd.Series([5.5, 7.0], dtype="float64"),
            "loan_income_ratio": pd.Series([0.2, 0.4], dtype="float64"),
            "loan_outcome": pd.Series([0, 1], dtype="int64"),
            "age": pd.Series([30, 40], dtype="int64"),
            "income": pd.Series([50000, 65000], dtype="int64"),
            "home_ownership": pd.Series(["RENT", "MORTGAGE"], dtype="str"),
            "employment_length": pd.Series([5.0, 10.0], dtype="float64"),
            "default_history": pd.Series(["N", "Y"], dtype="str"),
            "credit_history_length": pd.Series([8, 15], dtype="int64"),
        }
    )


def test_valid_dataset_passes_all_rules(valid_dataset: pd.DataFrame) -> None:
    """A valid dataset should pass every validation rule."""
    report = validate_dataset(
        valid_dataset,
        "loan_risk_dataset",
        CURATED_LOAN_RISK_VALIDATION_RULES,
    )

    assert report.overall_status == "PASS"
    assert all(result.status == "PASS" for result in report.results)


def test_schema_rejects_missing_columns(valid_dataset: pd.DataFrame) -> None:
    """The schema rule should reject missing columns."""
    dataset = valid_dataset.drop(columns=["customer_id"])

    result = validate_curated_schema(dataset)

    assert result.status == "FAIL"
    assert result.affected_rows == len(dataset)
    assert "customer_id" in result.message


def test_schema_rejects_unexpected_columns(
    valid_dataset: pd.DataFrame,
) -> None:
    """The schema rule should reject unexpected columns."""
    dataset = valid_dataset.assign(unexpected_column=[1, 2])

    result = validate_curated_schema(dataset)

    assert result.status == "FAIL"
    assert "unexpected_column" in result.message


def test_types_reject_incorrect_column_type(
    valid_dataset: pd.DataFrame,
) -> None:
    """The type rule should reject an incorrect numeric dtype."""
    dataset = valid_dataset.copy()
    dataset["loan_amount"] = dataset["loan_amount"].astype("float64")

    result = validate_curated_types(dataset)

    assert result.status == "FAIL"
    assert "loan_amount" in result.message


def test_required_values_reject_nulls(
    valid_dataset: pd.DataFrame,
) -> None:
    """Non-nullable required fields should reject null values."""
    dataset = valid_dataset.copy()
    dataset.loc[0, "income"] = float("nan")

    result = validate_curated_required_values(dataset)

    assert result.status == "FAIL"
    assert result.affected_rows == 1


def test_required_values_allow_approved_nullable_fields(
    valid_dataset: pd.DataFrame,
) -> None:
    """Approved nullable fields may contain missing values."""
    dataset = valid_dataset.copy()
    dataset.loc[0, "loan_interest_rate"] = float("nan")
    dataset.loc[1, "employment_length"] = float("nan")

    result = validate_curated_required_values(dataset)

    assert result.status == "PASS"
    assert result.affected_rows == 0


def test_identifiers_reject_duplicate_application_ids(
    valid_dataset: pd.DataFrame,
) -> None:
    """Application IDs must be unique."""
    dataset = valid_dataset.copy()
    dataset.loc[1, "application_id"] = dataset.loc[0, "application_id"]

    result = validate_curated_identifiers(dataset)

    assert result.status == "FAIL"
    assert result.affected_rows == 2


def test_identifiers_reject_null_customer_ids(
    valid_dataset: pd.DataFrame,
) -> None:
    """Customer IDs must be present."""
    dataset = valid_dataset.copy()
    dataset.loc[0, "customer_id"] = None

    result = validate_curated_identifiers(dataset)

    assert result.status == "FAIL"
    assert result.affected_rows == 1


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("loan_amount", 0),
        ("loan_interest_rate", -1.0),
        ("loan_income_ratio", 1.1),
        ("age", 17),
        ("income", -1),
        ("employment_length", -1.0),
        ("credit_history_length", -1),
    ],
)
def test_numeric_rules_reject_invalid_values(
    valid_dataset: pd.DataFrame,
    column: str,
    value: int | float,
) -> None:
    """Numeric rules should reject values outside their permitted domain."""
    dataset = valid_dataset.copy()
    dataset.loc[0, column] = value

    result = validate_curated_numeric_values(dataset)

    assert result.status == "FAIL"
    assert result.affected_rows >= 1


def test_numeric_rules_allow_nulls_in_approved_nullable_fields(
    valid_dataset: pd.DataFrame,
) -> None:
    """Numeric validation should allow nulls in approved nullable fields."""
    dataset = valid_dataset.copy()
    dataset.loc[0, "loan_interest_rate"] = float("nan")
    dataset.loc[1, "employment_length"] = float("nan")

    result = validate_curated_numeric_values(dataset)

    assert result.status == "PASS"
    assert result.affected_rows == 0


def test_numeric_rules_reject_nulls_in_non_nullable_fields(
    valid_dataset: pd.DataFrame,
) -> None:
    """Numeric validation must reject nulls in non-nullable fields."""
    dataset = valid_dataset.copy()
    dataset.loc[0, "income"] = float("nan")

    result = validate_curated_numeric_values(dataset)

    assert result.status == "FAIL"
    assert result.affected_rows == 1


def test_numeric_rules_reject_missing_columns(
    valid_dataset: pd.DataFrame,
) -> None:
    """The numeric rule should report missing numeric columns."""
    dataset = valid_dataset.drop(columns=["income"])

    result = validate_curated_numeric_values(dataset)

    assert result.status == "FAIL"
    assert "income" in result.message


def test_loan_purpose_rejects_invalid_category(
    valid_dataset: pd.DataFrame,
) -> None:
    """Loan purposes must belong to the permitted category set."""
    dataset = valid_dataset.copy()
    dataset.loc[0, "loan_purpose"] = "INVALID_PURPOSE"

    result = validate_curated_loan_purpose(dataset)

    assert result.status == "FAIL"
    assert result.affected_rows == 1


def test_target_rejects_values_outside_binary_domain(
    valid_dataset: pd.DataFrame,
) -> None:
    """The target must contain only 0 and 1."""
    dataset = valid_dataset.copy()
    dataset.loc[0, "loan_outcome"] = 2

    result = validate_curated_target(dataset)

    assert result.status == "FAIL"
    assert result.affected_rows == 1


def test_all_rules_handle_missing_columns_without_exceptions(
    valid_dataset: pd.DataFrame,
) -> None:
    """The complete rule set should handle missing columns safely."""
    dataset = valid_dataset.drop(
        columns=[
            "application_id",
            "loan_amount",
            "loan_purpose",
            "loan_outcome",
        ]
    )

    report = validate_dataset(
        dataset,
        "loan_risk_dataset",
        CURATED_LOAN_RISK_VALIDATION_RULES,
    )

    assert report.overall_status == "FAIL"
    assert any(result.status == "FAIL" for result in report.results)


def test_all_rules_handle_non_numeric_values_without_exceptions(
    valid_dataset: pd.DataFrame,
) -> None:
    """The complete rule set should report invalid numeric types safely."""
    dataset = valid_dataset.copy()
    dataset["loan_amount"] = pd.Series(
        ["not-a-number", "20000"],
        index=dataset.index,
        dtype="object",
    )

    report = validate_dataset(
        dataset,
        "loan_risk_dataset",
        CURATED_LOAN_RISK_VALIDATION_RULES,
    )

    assert report.overall_status == "FAIL"
    numeric_result = next(
        result for result in report.results if result.rule == "curated_numeric_values"
    )
    assert numeric_result.status == "FAIL"
    assert "loan_amount" in numeric_result.message
