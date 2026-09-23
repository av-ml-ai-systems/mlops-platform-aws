"""
Module: run_domain_decomposition.py

Path: scripts/run_domain_decomposition.py

Purpose: Run the local domain decomposition process.

Description: Reads the original Credit Risk dataset, creates the three
    domain datasets, and saves them under data/raw/.
"""

from pathlib import Path

import pandas as pd

from mlops_engineering_roadmap.data.domain_decomposition import (
    decompose_dataset,
    save_domain_datasets,
)

# Define the project root and the locations of the source and output data.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = PROJECT_ROOT / "data" / "raw" / "original" / "credit_risk_dataset.csv"
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "raw"


def main() -> None:
    """Run the domain decomposition process."""

    # Read the immutable original dataset.
    dataset = pd.read_csv(SOURCE_PATH)

    # Separate the source dataset into the three business domains.
    customer_profile, financial_history, loan_application = decompose_dataset(dataset)

    # Save the resulting domain datasets under data/raw/.
    save_domain_datasets(
        customer_profile,
        financial_history,
        loan_application,
        OUTPUT_DIRECTORY,
    )

    print("Domain decomposition completed.")
    print(f"Customer Profile: {len(customer_profile)} rows")
    print(f"Financial History: {len(financial_history)} rows")
    print(f"Loan Application: {len(loan_application)} rows")
    print(f"Output directory: {OUTPUT_DIRECTORY}")


if __name__ == "__main__":
    main()
