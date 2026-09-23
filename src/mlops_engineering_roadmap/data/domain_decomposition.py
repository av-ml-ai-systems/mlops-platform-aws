"""
Module: domain_decomposition.py

Path: src/mlops_engineering_roadmap/data/domain_decomposition.py

Purpose: Decompose the standardized Credit Risk dataset into business-domain datasets.

Description: Separates the source dataset into three business domains:
    Customer Profile, Financial History, and Loan Application.
"""

from pathlib import Path

import pandas as pd

from mlops_engineering_roadmap.utils.logger import get_logger

logger = get_logger(__name__)


# These are the columns that the decomposition process expects
# to find in the standardized source dataset.
REQUIRED_COLUMNS = {
    "person_age",
    "person_income",
    "person_home_ownership",
    "person_emp_length",
    "cb_person_default_on_file",
    "cb_person_cred_hist_length",
    "loan_amnt",
    "loan_intent",
    "loan_grade",
    "loan_int_rate",
    "loan_percent_income",
    "loan_status",
}


def decompose_dataset(
    dataset: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Decompose the source dataset into three business-domain datasets.

    Args:
        dataset: Standardized Credit Risk source dataset.

    Returns:
        A tuple containing:
            1. Customer Profile dataset
            2. Financial History dataset
            3. Loan Application dataset

    Raises:
        ValueError: If the source dataset is empty or required columns
            are missing.
    """

    # Validate that the caller provided data to process.
    if dataset.empty:
        raise ValueError("The source dataset is empty.")

    # Validate the input schema before performing any transformation.
    missing_columns = REQUIRED_COLUMNS - set(dataset.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    logger.info(
        "Starting domain decomposition for %d source rows.",
        len(dataset),
    )

    # Work on a copy so that the caller's DataFrame is never modified.
    source = dataset.reset_index(drop=True).copy()

    # The original dataset has no native customer or application IDs.
    # Therefore, we create synthetic technical identifiers for this
    # architecture exercise.
    source["customer_id"] = [f"C{index:06d}" for index in range(1, len(source) + 1)]

    source["application_id"] = [f"A{index:06d}" for index in range(1, len(source) + 1)]

    # Build the Customer Profile domain.
    # Only attributes belonging to this business domain are included.
    customer_profile = source[
        [
            "customer_id",
            "person_age",
            "person_income",
            "person_home_ownership",
            "person_emp_length",
        ]
    ].rename(
        columns={
            "person_age": "age",
            "person_income": "income",
            "person_home_ownership": "home_ownership",
            "person_emp_length": "employment_length",
        }
    )

    # Build the Financial History domain.
    # The source provides only limited historical financial information.
    financial_history = source[
        [
            "customer_id",
            "cb_person_default_on_file",
            "cb_person_cred_hist_length",
        ]
    ].rename(
        columns={
            "cb_person_default_on_file": "default_history",
            "cb_person_cred_hist_length": "credit_history_length",
        }
    )

    # Build the Loan Application domain.
    # loan_status remains part of this domain because it represents
    # the application outcome and is our ML target.
    loan_application = source[
        [
            "application_id",
            "customer_id",
            "loan_amnt",
            "loan_intent",
            "loan_grade",
            "loan_int_rate",
            "loan_percent_income",
            "loan_status",
        ]
    ].rename(
        columns={
            "loan_amnt": "loan_amount",
            "loan_intent": "loan_purpose",
            "loan_grade": "risk_grade",
            "loan_int_rate": "loan_interest_rate",
            "loan_percent_income": "loan_income_ratio",
            "loan_status": "loan_outcome",
        }
    )

    # Log the resulting domain sizes for operational visibility.
    logger.info(
        "Domain decomposition completed: %d customer rows, "
        "%d financial-history rows, %d loan-application rows.",
        len(customer_profile),
        len(financial_history),
        len(loan_application),
    )

    return customer_profile, financial_history, loan_application


def save_domain_datasets(
    customer_profile: pd.DataFrame,
    financial_history: pd.DataFrame,
    loan_application: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Save decomposed domain datasets as CSV files.

    Args:
        customer_profile: Customer Profile dataset.
        financial_history: Financial History dataset.
        loan_application: Loan Application dataset.
        output_directory: Root directory for the domain datasets.
    """

    # Define the destination directory for each business domain.
    customer_directory = output_directory / "customer"
    financial_directory = output_directory / "financial_history"
    loan_directory = output_directory / "loan_application"

    # Create the destination directories when they do not exist.
    customer_directory.mkdir(parents=True, exist_ok=True)
    financial_directory.mkdir(parents=True, exist_ok=True)
    loan_directory.mkdir(parents=True, exist_ok=True)

    # Persist each domain dataset independently.
    customer_profile.to_csv(
        customer_directory / "customer.csv",
        index=False,
    )

    financial_history.to_csv(
        financial_directory / "financial_history.csv",
        index=False,
    )

    loan_application.to_csv(
        loan_directory / "loan_application.csv",
        index=False,
    )

    logger.info(
        "Domain datasets saved to %s.",
        output_directory,
    )
