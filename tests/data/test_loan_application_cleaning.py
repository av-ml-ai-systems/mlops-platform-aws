# Module: test_loan_application_cleaning
# Path: tests/data/test_loan_application_cleaning.py
# Purpose: Test Loan Application domain cleaning and standardization.

import pandas as pd
import pytest

from mlops_engineering_roadmap.data.cleaning.loan_application import (
    clean_loan_application_dataset,
)


@pytest.fixture
def loan_application_dataset() -> pd.DataFrame:
    """Provide a representative Loan Application dataset."""
    return pd.DataFrame(
        {
            "application_id": ["A001", "A002", "A003", "A004"],
            "customer_id": ["C001", "C002", "C003", "C004"],
            "loan_amount": [5000, 10000, 2500, 6000],
            "loan_purpose": [
                " medical ",
                "EDUCATION",
                "VENTURE",
                "PERSONAL",
            ],
            "risk_grade": [" a ", "B", "G", "F"],
            "loan_interest_rate": [10.5, None, 12.0, 8.5],
            "loan_income_ratio": [0.20, 0.35, 0.05, 0.10],
            "loan_outcome": [0, 1, 0, 1],
        }
    )


def test_cleaning_preserves_input_dataframe(
    loan_application_dataset: pd.DataFrame,
) -> None:
    original = loan_application_dataset.copy(deep=True)

    clean_loan_application_dataset(loan_application_dataset)

    pd.testing.assert_frame_equal(loan_application_dataset, original)


def test_cleaning_standardizes_categorical_values(
    loan_application_dataset: pd.DataFrame,
) -> None:
    result = clean_loan_application_dataset(loan_application_dataset)

    assert result.data["loan_purpose"].tolist() == [
        "MEDICAL",
        "EDUCATION",
        "VENTURE",
        "PERSONAL",
    ]
    assert result.data["risk_grade"].tolist() == ["A", "B", "G", "F"]
    assert result.report.categorical_values_standardized == 2


def test_cleaning_preserves_missing_interest_rates(
    loan_application_dataset: pd.DataFrame,
) -> None:
    result = clean_loan_application_dataset(loan_application_dataset)

    assert result.data["loan_interest_rate"].isna().sum() == 1
    assert any(issue.rule == "missing_loan_interest_rate" for issue in result.report.issues)


def test_cleaning_preserves_valid_rare_grades(
    loan_application_dataset: pd.DataFrame,
) -> None:
    result = clean_loan_application_dataset(loan_application_dataset)

    assert "F" in result.data["risk_grade"].values
    assert "G" in result.data["risk_grade"].values
    assert not any(issue.rule == "invalid_risk_grade" for issue in result.report.issues)


def test_cleaning_removes_exact_duplicate_rows(
    loan_application_dataset: pd.DataFrame,
) -> None:
    duplicated = pd.concat(
        [loan_application_dataset, loan_application_dataset.iloc[[0]]],
        ignore_index=True,
    )

    result = clean_loan_application_dataset(duplicated)

    assert len(result.data) == len(loan_application_dataset)
    assert result.report.input_rows == 5
    assert result.report.output_rows == 4
    assert result.report.duplicate_rows_removed == 1


def test_cleaning_reports_conflicting_application_ids() -> None:
    dataset = pd.DataFrame(
        {
            "application_id": ["A001", "A001"],
            "customer_id": ["C001", "C002"],
            "loan_amount": [5000, 8000],
            "loan_purpose": ["MEDICAL", "EDUCATION"],
            "risk_grade": ["A", "B"],
            "loan_interest_rate": [10.0, 11.0],
            "loan_income_ratio": [0.20, 0.30],
            "loan_outcome": [0, 1],
        }
    )

    result = clean_loan_application_dataset(dataset)

    assert len(result.data) == 2
    assert any(issue.rule == "duplicate_application_id" for issue in result.report.issues)


def test_cleaning_reports_invalid_domain_values() -> None:
    dataset = pd.DataFrame(
        {
            "application_id": ["A001", "A002", "A003", "A004", "A005"],
            "customer_id": ["C001", "C002", "C003", "C004", "C005"],
            "loan_amount": [0, 5000, 5000, 5000, 5000],
            "loan_purpose": [
                "MEDICAL",
                "EDUCATION",
                "UNKNOWN",
                "PERSONAL",
                "VENTURE",
            ],
            "risk_grade": ["A", "B", "C", "Z", "E"],
            "loan_interest_rate": [-1.0, 10.0, 10.0, 10.0, 10.0],
            "loan_income_ratio": [0.20, 1.2, 0.20, 0.20, 0.20],
            "loan_outcome": [0, 1, 0, 1, 2],
        }
    )

    result = clean_loan_application_dataset(dataset)
    issue_rules = {issue.rule for issue in result.report.issues}

    assert "nonpositive_loan_amount" in issue_rules
    assert "nonpositive_loan_interest_rate" in issue_rules
    assert "invalid_loan_income_ratio" in issue_rules
    assert "invalid_loan_purpose" in issue_rules
    assert "invalid_risk_grade" in issue_rules
    assert "invalid_loan_outcome" in issue_rules


def test_cleaning_reports_missing_identifiers() -> None:
    dataset = pd.DataFrame(
        {
            "application_id": [None],
            "customer_id": [None],
            "loan_amount": [5000],
            "loan_purpose": ["MEDICAL"],
            "risk_grade": ["A"],
            "loan_interest_rate": [10.0],
            "loan_income_ratio": [0.20],
            "loan_outcome": [0],
        }
    )

    result = clean_loan_application_dataset(dataset)
    issue_rules = {issue.rule for issue in result.report.issues}

    assert "missing_application_id" in issue_rules
    assert "missing_customer_id" in issue_rules


def test_cleaning_rejects_missing_required_columns() -> None:
    dataset = pd.DataFrame({"application_id": ["A001"]})

    with pytest.raises(ValueError, match="missing required columns"):
        clean_loan_application_dataset(dataset)
