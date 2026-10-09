# Module: test_customer_cleaning
# Path: tests/data/test_customer_cleaning.py
# Purpose: Test Customer Profile cleaning behavior.
# Description: Verify cleaning rules, issue reporting, and input preservation.

import pandas as pd
import pytest

from mlops_engineering_roadmap.data.cleaning.customer import (
    clean_customer_dataset,
)


@pytest.fixture
def customer_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["C001", "C002", "C003", "C004"],
            "age": [25, 30, 17, 40],
            "income": [50000, 60000, 45000, -100],
            "home_ownership": [" rent ", "OWN", "MORTGAGE", "UNKNOWN"],
            "employment_length": [5, 35, None, 10],
        }
    )


def test_cleaning_preserves_input_dataframe(
    customer_dataset: pd.DataFrame,
) -> None:
    original = customer_dataset.copy(deep=True)

    clean_customer_dataset(customer_dataset)

    pd.testing.assert_frame_equal(customer_dataset, original)


def test_cleaning_corrects_inconsistent_employment_length(
    customer_dataset: pd.DataFrame,
) -> None:
    result = clean_customer_dataset(customer_dataset)

    assert pd.isna(result.data.loc[1, "employment_length"])
    assert result.report.employment_lengths_corrected == 1


def test_cleaning_preserves_legitimate_missing_employment_length(
    customer_dataset: pd.DataFrame,
) -> None:
    result = clean_customer_dataset(customer_dataset)

    assert pd.isna(result.data.loc[2, "employment_length"])
    assert result.report.employment_lengths_corrected == 1


def test_cleaning_standardizes_home_ownership(
    customer_dataset: pd.DataFrame,
) -> None:
    result = clean_customer_dataset(customer_dataset)

    assert result.data.loc[0, "home_ownership"] == "RENT"
    assert result.report.categorical_values_standardized == 1


def test_cleaning_reports_invalid_age_income_and_category(
    customer_dataset: pd.DataFrame,
) -> None:
    result = clean_customer_dataset(customer_dataset)

    issue_rules = {issue.rule for issue in result.report.issues}

    assert "minimum_customer_age" in issue_rules
    assert "nonnegative_income" in issue_rules
    assert "allowed_home_ownership" in issue_rules


def test_cleaning_removes_exact_duplicate_rows(
    customer_dataset: pd.DataFrame,
) -> None:
    duplicated = pd.concat(
        [customer_dataset, customer_dataset.iloc[[0]]],
        ignore_index=True,
    )

    result = clean_customer_dataset(duplicated)

    assert len(result.data) == len(customer_dataset)
    assert result.report.duplicate_rows_removed == 1


def test_cleaning_reports_conflicting_duplicate_customer_ids() -> None:
    dataset = pd.DataFrame(
        {
            "customer_id": ["C001", "C001"],
            "age": [25, 26],
            "income": [50000, 51000],
            "home_ownership": ["RENT", "OWN"],
            "employment_length": [5, 6],
        }
    )

    result = clean_customer_dataset(dataset)

    assert len(result.data) == 2
    assert any(issue.rule == "customer_id_uniqueness" for issue in result.report.issues)


def test_cleaning_rejects_missing_required_columns() -> None:
    dataset = pd.DataFrame({"customer_id": ["C001"]})

    with pytest.raises(ValueError, match="missing required columns"):
        clean_customer_dataset(dataset)
