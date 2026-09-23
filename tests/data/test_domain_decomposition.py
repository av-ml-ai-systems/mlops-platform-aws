"""
Module: test_domain_decomposition.py

Path: tests/data/test_domain_decomposition.py

Purpose: Test the Credit Risk domain decomposition module.

Description: Verifies domain creation, identifiers, data integrity, validation, and file saving.
"""

from pathlib import Path

import pandas as pd
import pytest

from mlops_engineering_roadmap.data.domain_decomposition import (
    decompose_dataset,
    save_domain_datasets,
)


@pytest.fixture
def source_dataset() -> pd.DataFrame:
    """Create a small dataset representing the source Credit Risk data."""
    return pd.DataFrame(
        {
            "person_age": [22, 35, 41],
            "person_income": [50000, 80000, 95000],
            "person_home_ownership": ["RENT", "OWN", "MORTGAGE"],
            "person_emp_length": [2.0, 8.0, 12.0],
            "cb_person_default_on_file": ["N", "Y", "N"],
            "cb_person_cred_hist_length": [4, 10, 15],
            "loan_amnt": [10000, 20000, 15000],
            "loan_intent": ["EDUCATION", "PERSONAL", "MEDICAL"],
            "loan_grade": ["A", "C", "B"],
            "loan_int_rate": [7.5, 12.0, 9.5],
            "loan_percent_income": [0.20, 0.25, 0.16],
            "loan_status": [0, 1, 0],
        }
    )


def test_decompose_dataset_creates_three_domains(source_dataset: pd.DataFrame) -> None:
    """Verify that the source dataset is divided into three datasets."""
    customer_profile, financial_history, loan_application = decompose_dataset(source_dataset)

    assert isinstance(customer_profile, pd.DataFrame)
    assert isinstance(financial_history, pd.DataFrame)
    assert isinstance(loan_application, pd.DataFrame)


def test_decompose_dataset_creates_expected_columns(
    source_dataset: pd.DataFrame,
) -> None:
    """Verify that each domain contains the expected columns."""
    customer_profile, financial_history, loan_application = decompose_dataset(source_dataset)

    assert list(customer_profile.columns) == [
        "customer_id",
        "age",
        "income",
        "home_ownership",
        "employment_length",
    ]

    assert list(financial_history.columns) == [
        "customer_id",
        "default_history",
        "credit_history_length",
    ]

    assert list(loan_application.columns) == [
        "application_id",
        "customer_id",
        "loan_amount",
        "loan_purpose",
        "risk_grade",
        "loan_interest_rate",
        "loan_income_ratio",
        "loan_outcome",
    ]


def test_decompose_dataset_preserves_row_count(
    source_dataset: pd.DataFrame,
) -> None:
    """Verify that decomposition does not remove or add rows."""
    customer_profile, financial_history, loan_application = decompose_dataset(source_dataset)

    assert len(customer_profile) == len(source_dataset)
    assert len(financial_history) == len(source_dataset)
    assert len(loan_application) == len(source_dataset)


def test_decompose_dataset_creates_unique_identifiers(
    source_dataset: pd.DataFrame,
) -> None:
    """Verify that generated customer and application IDs are unique."""
    customer_profile, _, loan_application = decompose_dataset(source_dataset)

    assert customer_profile["customer_id"].is_unique
    assert loan_application["application_id"].is_unique


def test_decompose_dataset_preserves_customer_relationship(
    source_dataset: pd.DataFrame,
) -> None:
    """Verify that customer IDs connect the three domain datasets."""
    customer_profile, financial_history, loan_application = decompose_dataset(source_dataset)

    assert customer_profile["customer_id"].tolist() == financial_history["customer_id"].tolist()

    assert customer_profile["customer_id"].tolist() == loan_application["customer_id"].tolist()


def test_decompose_dataset_creates_expected_id_format(
    source_dataset: pd.DataFrame,
) -> None:
    """Verify the format of the generated technical identifiers."""
    customer_profile, _, loan_application = decompose_dataset(source_dataset)

    assert customer_profile["customer_id"].tolist() == [
        "C000001",
        "C000002",
        "C000003",
    ]

    assert loan_application["application_id"].tolist() == [
        "A000001",
        "A000002",
        "A000003",
    ]


def test_decompose_dataset_does_not_modify_source(
    source_dataset: pd.DataFrame,
) -> None:
    """Verify that the original DataFrame remains unchanged."""
    original_dataset = source_dataset.copy(deep=True)

    decompose_dataset(source_dataset)

    pd.testing.assert_frame_equal(source_dataset, original_dataset)


def test_decompose_dataset_rejects_empty_dataset() -> None:
    """Verify that an empty source dataset is rejected."""
    empty_dataset = pd.DataFrame()

    with pytest.raises(ValueError, match="source dataset is empty"):
        decompose_dataset(empty_dataset)


def test_decompose_dataset_rejects_missing_columns(
    source_dataset: pd.DataFrame,
) -> None:
    """Verify that missing required columns are reported."""
    incomplete_dataset = source_dataset.drop(columns=["loan_status"])

    with pytest.raises(ValueError, match="Missing required columns: loan_status"):
        decompose_dataset(incomplete_dataset)


def test_save_domain_datasets_creates_expected_files(
    source_dataset: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Verify that the three domain datasets are saved in the expected locations."""
    customer_profile, financial_history, loan_application = decompose_dataset(source_dataset)

    save_domain_datasets(
        customer_profile,
        financial_history,
        loan_application,
        tmp_path,
    )

    assert (tmp_path / "customer" / "customer.csv").exists()
    assert (tmp_path / "financial_history" / "financial_history.csv").exists()
    assert (tmp_path / "loan_application" / "loan_application.csv").exists()
