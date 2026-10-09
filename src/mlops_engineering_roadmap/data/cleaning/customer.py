# Module: customer
# Path: src/mlops_engineering_roadmap/data/cleaning/customer.py
# Purpose: Clean and standardize Customer Profile data.
# Description: Apply authorized corrections and report unresolved data quality issues.

from dataclasses import dataclass
from typing import Literal

import pandas as pd

IssueSeverity = Literal["WARNING", "ERROR"]


@dataclass(frozen=True)
class CleaningIssue:
    rule: str
    severity: IssueSeverity
    message: str
    affected_rows: int


@dataclass(frozen=True)
class CustomerCleaningReport:
    input_rows: int
    output_rows: int
    duplicate_rows_removed: int
    employment_lengths_corrected: int
    categorical_values_standardized: int
    issues: tuple[CleaningIssue, ...]


@dataclass(frozen=True)
class CustomerCleaningResult:
    data: pd.DataFrame
    report: CustomerCleaningReport


REQUIRED_COLUMNS = {
    "customer_id",
    "age",
    "income",
    "home_ownership",
    "employment_length",
}

ALLOWED_HOME_OWNERSHIP = {
    "RENT",
    "OWN",
    "MORTGAGE",
    "OTHER",
}


def clean_customer_dataset(
    dataset: pd.DataFrame,
) -> CustomerCleaningResult:
    """Clean Customer Profile data without modifying the input DataFrame."""
    missing_columns = REQUIRED_COLUMNS - set(dataset.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Customer Profile is missing required columns: {missing}")

    cleaned = dataset.copy(deep=True)
    input_rows = len(cleaned)
    issues: list[CleaningIssue] = []

    # Remove exact duplicate rows and record the number removed.
    duplicate_mask = cleaned.duplicated()
    duplicate_rows_removed = int(duplicate_mask.sum())
    cleaned = cleaned.loc[~duplicate_mask].copy()

    # Normalize unambiguous categorical representations.
    original_home_ownership = cleaned["home_ownership"].copy()

    cleaned["home_ownership"] = cleaned["home_ownership"].astype("string").str.strip().str.upper()

    categorical_values_standardized = int(
        (original_home_ownership.astype("string") != cleaned["home_ownership"]).fillna(False).sum()
    )

    # Correct employment lengths that exceed customer age.
    employment_inconsistent = (
        cleaned["employment_length"].notna()
        & cleaned["age"].notna()
        & (cleaned["employment_length"] > cleaned["age"])
    )

    employment_lengths_corrected = int(employment_inconsistent.sum())

    cleaned.loc[employment_inconsistent, "employment_length"] = pd.NA

    # Report unresolved duplicate customer identifiers.
    duplicate_customer_id = cleaned["customer_id"].notna() & cleaned["customer_id"].duplicated(
        keep=False
    )

    if duplicate_customer_id.any():
        issues.append(
            CleaningIssue(
                rule="customer_id_uniqueness",
                severity="ERROR",
                message=(
                    "Duplicate customer IDs remain after exact duplicate "
                    "rows were removed. Conflicting records were preserved."
                ),
                affected_rows=int(duplicate_customer_id.sum()),
            )
        )

    # Report invalid ages without inventing replacement values.
    invalid_age = cleaned["age"].notna() & (cleaned["age"] < 18)

    if invalid_age.any():
        issues.append(
            CleaningIssue(
                rule="minimum_customer_age",
                severity="ERROR",
                message="Customer ages below 18 require investigation.",
                affected_rows=int(invalid_age.sum()),
            )
        )

    # Report negative income without changing it.
    negative_income = cleaned["income"].notna() & (cleaned["income"] < 0)

    if negative_income.any():
        issues.append(
            CleaningIssue(
                rule="nonnegative_income",
                severity="ERROR",
                message="Negative income values require investigation.",
                affected_rows=int(negative_income.sum()),
            )
        )

    # Report unrecognized categories without remapping them.
    invalid_home_ownership = cleaned["home_ownership"].notna() & ~cleaned["home_ownership"].isin(
        ALLOWED_HOME_OWNERSHIP
    )

    if invalid_home_ownership.any():
        issues.append(
            CleaningIssue(
                rule="allowed_home_ownership",
                severity="ERROR",
                message="Unrecognized home ownership categories remain.",
                affected_rows=int(invalid_home_ownership.sum()),
            )
        )

    report = CustomerCleaningReport(
        input_rows=input_rows,
        output_rows=len(cleaned),
        duplicate_rows_removed=duplicate_rows_removed,
        employment_lengths_corrected=employment_lengths_corrected,
        categorical_values_standardized=categorical_values_standardized,
        issues=tuple(issues),
    )

    return CustomerCleaningResult(data=cleaned, report=report)
