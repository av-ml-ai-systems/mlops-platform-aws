# Module: test_financial_history_cleaning
# Path: tests/data/test_financial_history_cleaning.py
# Purpose: Test Financial History cleaning behavior.
# Description: Verify duplicate handling, standardization, issue reporting, and input preservation.

import pandas as pd
import pytest

from mlops_engineering_roadmap.data.cleaning.financial_history import (
    clean_financial_history_dataset,
)


@pytest.fixture
def financial_history_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["C001", "C002", "C003", "C004"],
            "default_history": ["Y", " N ", "n", "Y"],
            "credit_history_length": [5, 10, 3, 7],
        }
    )


def test_cleaning_preserves_input_dataframe(
    financial_history_dataset: pd.DataFrame,
) -> None:
    original = financial_history_dataset.copy(deep=True)

    clean_financial_history_dataset(financial_history_dataset)

    pd.testing.assert_frame_equal(financial_history_dataset, original)


def test_cleaning_standardizes_default_history(
    financial_history_dataset: pd.DataFrame,
) -> None:
    result = clean_financial_history_dataset(financial_history_dataset)

    assert result.data["default_history"].tolist() == ["Y", "N", "N", "Y"]


def test_cleaning_removes_exact_duplicate_rows(
    financial_history_dataset: pd.DataFrame,
) -> None:
    duplicated = pd.concat(
        [financial_history_dataset, financial_history_dataset.iloc[[0]]],
        ignore_index=True,
    )

    result = clean_financial_history_dataset(duplicated)

    assert len(result.data) == len(financial_history_dataset)
    assert result.report.duplicate_rows_removed == 1


def test_cleaning_reports_conflicting_duplicate_customer_ids() -> None:
    dataset = pd.DataFrame(
        {
            "customer_id": ["C001", "C001"],
            "default_history": ["Y", "N"],
            "credit_history_length": [5, 7],
        }
    )

    result = clean_financial_history_dataset(dataset)

    assert len(result.data) == 2
    assert any(issue.rule == "customer_id_uniqueness" for issue in result.report.issues)


def test_cleaning_reports_missing_customer_ids() -> None:
    dataset = pd.DataFrame(
        {
            "customer_id": ["C001", None],
            "default_history": ["Y", "N"],
            "credit_history_length": [5, 7],
        }
    )

    result = clean_financial_history_dataset(dataset)

    assert any(issue.rule == "customer_id_presence" for issue in result.report.issues)


def test_cleaning_reports_invalid_default_history() -> None:
    dataset = pd.DataFrame(
        {
            "customer_id": ["C001", "C002"],
            "default_history": ["Y", "UNKNOWN"],
            "credit_history_length": [5, 7],
        }
    )

    result = clean_financial_history_dataset(dataset)

    assert any(issue.rule == "allowed_default_history" for issue in result.report.issues)


def test_cleaning_reports_negative_credit_history_length() -> None:
    dataset = pd.DataFrame(
        {
            "customer_id": ["C001", "C002"],
            "default_history": ["Y", "N"],
            "credit_history_length": [5, -1],
        }
    )

    result = clean_financial_history_dataset(dataset)

    assert any(issue.rule == "nonnegative_credit_history_length" for issue in result.report.issues)


def test_cleaning_rejects_missing_required_columns() -> None:
    dataset = pd.DataFrame({"customer_id": ["C001"]})

    with pytest.raises(ValueError, match="missing required columns"):
        clean_financial_history_dataset(dataset)
