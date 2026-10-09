# Module: financial_history
# Path: src/mlops_engineering_roadmap/data/cleaning/financial_history.py
# Purpose: Clean and standardize Financial History data.
# Description: Remove exact duplicates and report unresolved domain quality issues.

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
class FinancialHistoryCleaningReport:
    input_rows: int
    output_rows: int
    duplicate_rows_removed: int
    issues: tuple[CleaningIssue, ...]


@dataclass(frozen=True)
class FinancialHistoryCleaningResult:
    data: pd.DataFrame
    report: FinancialHistoryCleaningReport


REQUIRED_COLUMNS = {
    "customer_id",
    "default_history",
    "credit_history_length",
}

ALLOWED_DEFAULT_HISTORY = {"Y", "N"}


def clean_financial_history_dataset(
    dataset: pd.DataFrame,
) -> FinancialHistoryCleaningResult:
    """Clean Financial History data without modifying the input DataFrame."""
    missing_columns = REQUIRED_COLUMNS - set(dataset.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Financial History is missing required columns: {missing}")

    cleaned = dataset.copy(deep=True)
    input_rows = len(cleaned)
    issues: list[CleaningIssue] = []

    # Remove exact duplicate rows and record the number removed.
    duplicate_mask = cleaned.duplicated()
    duplicate_rows_removed = int(duplicate_mask.sum())
    cleaned = cleaned.loc[~duplicate_mask].copy()

    # Standardize unambiguous representations of default history.
    cleaned["default_history"] = cleaned["default_history"].astype("string").str.strip().str.upper()

    # Report duplicate customer identifiers without discarding records.
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

    # Report missing customer identifiers.
    missing_customer_id = cleaned["customer_id"].isna()

    if missing_customer_id.any():
        issues.append(
            CleaningIssue(
                rule="customer_id_presence",
                severity="ERROR",
                message="Missing customer IDs require investigation.",
                affected_rows=int(missing_customer_id.sum()),
            )
        )

    # Report invalid default-history categories.
    invalid_default_history = cleaned["default_history"].notna() & ~cleaned["default_history"].isin(
        ALLOWED_DEFAULT_HISTORY
    )

    if invalid_default_history.any():
        issues.append(
            CleaningIssue(
                rule="allowed_default_history",
                severity="ERROR",
                message="Unrecognized default-history values remain.",
                affected_rows=int(invalid_default_history.sum()),
            )
        )

    # Report negative credit-history lengths without changing them.
    negative_credit_history_length = cleaned["credit_history_length"].notna() & (
        cleaned["credit_history_length"] < 0
    )

    if negative_credit_history_length.any():
        issues.append(
            CleaningIssue(
                rule="nonnegative_credit_history_length",
                severity="ERROR",
                message=("Negative credit-history lengths require investigation."),
                affected_rows=int(negative_credit_history_length.sum()),
            )
        )

    report = FinancialHistoryCleaningReport(
        input_rows=input_rows,
        output_rows=len(cleaned),
        duplicate_rows_removed=duplicate_rows_removed,
        issues=tuple(issues),
    )

    return FinancialHistoryCleaningResult(data=cleaned, report=report)
