# Module: test_validation.py
# Path: tests/data/test_validation.py
# Purpose: Test the Phase 2 dataset validation component.
# Description: Verifies domain validation rules and validation report behavior.


import pandas as pd

from mlops_engineering_roadmap.data.validation.customer import (
    CUSTOMER_VALIDATION_RULES,
)
from mlops_engineering_roadmap.data.validation.financial_history import (
    FINANCIAL_HISTORY_VALIDATION_RULES,
)
from mlops_engineering_roadmap.data.validation.loan_application import (
    LOAN_APPLICATION_VALIDATION_RULES,
)
from mlops_engineering_roadmap.data.validation.validator import validate_dataset


def test_valid_customer_dataset_passes() -> None:
    """Verify that a valid Customer Profile dataset passes validation."""
    dataset = pd.DataFrame(
        {
            "customer_id": ["C000001", "C000002"],
            "age": [30, 40],
            "income": [50000, 70000],
            "home_ownership": ["RENT", "OWN"],
            "employment_length": [5.0, 10.0],
        }
    )

    report = validate_dataset(
        dataset,
        "customer",
        CUSTOMER_VALIDATION_RULES,
    )

    assert report.overall_status == "PASS"


def test_invalid_customer_employment_fails() -> None:
    """Verify that inconsistent employment history causes validation failure."""
    dataset = pd.DataFrame(
        {
            "customer_id": ["C000001"],
            "age": [22],
            "income": [50000],
            "home_ownership": ["RENT"],
            "employment_length": [123.0],
        }
    )

    report = validate_dataset(
        dataset,
        "customer",
        CUSTOMER_VALIDATION_RULES,
    )

    assert report.overall_status == "FAIL"

    failed_rules = {result.rule for result in report.results if result.status == "FAIL"}

    assert "age_employment_consistency" in failed_rules


def test_valid_financial_history_passes() -> None:
    """Verify that a valid Financial History dataset passes validation."""
    dataset = pd.DataFrame(
        {
            "customer_id": ["C000001", "C000002"],
            "default_history": ["N", "Y"],
            "credit_history_length": [3, 8],
        }
    )

    report = validate_dataset(
        dataset,
        "financial_history",
        FINANCIAL_HISTORY_VALIDATION_RULES,
    )

    assert report.overall_status == "PASS"


def test_invalid_default_history_fails() -> None:
    """Verify that an invalid default history value causes failure."""
    dataset = pd.DataFrame(
        {
            "customer_id": ["C000001"],
            "default_history": ["UNKNOWN"],
            "credit_history_length": [3],
        }
    )

    report = validate_dataset(
        dataset,
        "financial_history",
        FINANCIAL_HISTORY_VALIDATION_RULES,
    )

    assert report.overall_status == "FAIL"


def test_valid_loan_application_passes() -> None:
    """Verify that a valid Loan Application dataset passes validation."""
    dataset = pd.DataFrame(
        {
            "application_id": ["A000001"],
            "customer_id": ["C000001"],
            "loan_amount": [10000],
            "loan_purpose": ["PERSONAL"],
            "risk_grade": ["B"],
            "loan_interest_rate": [10.5],
            "loan_income_ratio": [0.2],
            "loan_outcome": [1],
        }
    )

    report = validate_dataset(
        dataset,
        "loan_application",
        LOAN_APPLICATION_VALIDATION_RULES,
    )

    assert report.overall_status == "PASS"


def test_invalid_loan_risk_grade_fails() -> None:
    """Verify that an invalid risk grade causes validation failure."""
    dataset = pd.DataFrame(
        {
            "application_id": ["A000001"],
            "customer_id": ["C000001"],
            "loan_amount": [10000],
            "loan_purpose": ["PERSONAL"],
            "risk_grade": ["Z"],
            "loan_interest_rate": [10.5],
            "loan_income_ratio": [0.2],
            "loan_outcome": [1],
        }
    )

    report = validate_dataset(
        dataset,
        "loan_application",
        LOAN_APPLICATION_VALIDATION_RULES,
    )

    assert report.overall_status == "FAIL"
