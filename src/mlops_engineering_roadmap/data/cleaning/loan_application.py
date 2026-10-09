# Module: loan_application
# Path: src/mlops_engineering_roadmap/data/cleaning/loan_application.py
# Purpose: Clean and standardize Loan Application data.
# Description: Apply authorized standardization and report unresolved domain quality issues.

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CleaningIssue:
    rule: str
    severity: str
    message: str
    affected_rows: int


@dataclass(frozen=True)
class LoanApplicationCleaningReport:
    input_rows: int
    output_rows: int
    duplicate_rows_removed: int
    categorical_values_standardized: int
    issues: tuple[CleaningIssue, ...]


@dataclass(frozen=True)
class LoanApplicationCleaningResult:
    data: pd.DataFrame
    report: LoanApplicationCleaningReport


_REQUIRED_COLUMNS = {
    "application_id",
    "customer_id",
    "loan_amount",
    "loan_purpose",
    "risk_grade",
    "loan_interest_rate",
    "loan_income_ratio",
    "loan_outcome",
}

_VALID_PURPOSES = {
    "EDUCATION",
    "MEDICAL",
    "VENTURE",
    "PERSONAL",
    "DEBTCONSOLIDATION",
    "HOMEIMPROVEMENT",
}

_VALID_GRADES = {"A", "B", "C", "D", "E", "F", "G"}
_VALID_OUTCOMES = {0, 1}


def clean_loan_application_dataset(
    dataset: pd.DataFrame,
) -> LoanApplicationCleaningResult:
    """Clean a Loan Application DataFrame without modifying the input."""
    if not isinstance(dataset, pd.DataFrame):
        raise TypeError("dataset must be a pandas DataFrame.")

    missing_columns = _REQUIRED_COLUMNS - set(dataset.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Loan Application is missing required columns: {missing}")

    input_rows = len(dataset)
    cleaned = dataset.copy(deep=True)

    # Remove exact duplicate rows only; conflicting business records are reported.
    duplicate_mask = cleaned.duplicated(keep="first")
    duplicate_rows_removed = int(duplicate_mask.sum())
    cleaned = cleaned.loc[~duplicate_mask].copy()

    issues: list[CleaningIssue] = []

    # Standardize unambiguous categorical formatting.
    categorical_values_standardized = 0

    for column in ("loan_purpose", "risk_grade"):
        original = cleaned[column].copy()
        normalized = original.astype("string").str.strip().str.upper()
        normalized = normalized.mask(original.isna(), pd.NA)

        changed = original.ne(normalized).fillna(False)
        categorical_values_standardized += int(changed.sum())
        cleaned[column] = normalized

    # Report missing and duplicate identifiers without arbitrarily removing records.
    missing_application_ids = int(cleaned["application_id"].isna().sum())
    if missing_application_ids:
        issues.append(
            CleaningIssue(
                rule="missing_application_id",
                severity="ERROR",
                message="Application identifiers are missing.",
                affected_rows=missing_application_ids,
            )
        )

    duplicate_application_ids = int(cleaned["application_id"].duplicated(keep=False).sum())
    if duplicate_application_ids:
        issues.append(
            CleaningIssue(
                rule="duplicate_application_id",
                severity="ERROR",
                message=(
                    "Application identifiers occur in multiple records; "
                    "records were preserved for investigation."
                ),
                affected_rows=duplicate_application_ids,
            )
        )

    missing_customer_ids = int(cleaned["customer_id"].isna().sum())
    if missing_customer_ids:
        issues.append(
            CleaningIssue(
                rule="missing_customer_id",
                severity="ERROR",
                message="Customer identifiers are missing.",
                affected_rows=missing_customer_ids,
            )
        )

    # Validate numeric fields without silently correcting business values.
    loan_amount = pd.to_numeric(cleaned["loan_amount"], errors="coerce")
    invalid_loan_amount = int((loan_amount.notna() & (loan_amount <= 0)).sum())
    if invalid_loan_amount:
        issues.append(
            CleaningIssue(
                rule="nonpositive_loan_amount",
                severity="ERROR",
                message="Loan amounts must be greater than zero.",
                affected_rows=invalid_loan_amount,
            )
        )

    interest_rate = pd.to_numeric(cleaned["loan_interest_rate"], errors="coerce")
    invalid_interest_rate = int((interest_rate.notna() & (interest_rate <= 0)).sum())
    if invalid_interest_rate:
        issues.append(
            CleaningIssue(
                rule="nonpositive_loan_interest_rate",
                severity="ERROR",
                message=("Non-missing interest rates must be greater than zero."),
                affected_rows=invalid_interest_rate,
            )
        )

    income_ratio = pd.to_numeric(cleaned["loan_income_ratio"], errors="coerce")
    invalid_income_ratio = int(
        (income_ratio.notna() & ((income_ratio < 0) | (income_ratio > 1))).sum()
    )
    if invalid_income_ratio:
        issues.append(
            CleaningIssue(
                rule="invalid_loan_income_ratio",
                severity="ERROR",
                message="Loan-income ratios must be between zero and one.",
                affected_rows=invalid_income_ratio,
            )
        )

    # Missing interest rates are preserved and reported, not imputed here.
    missing_interest_rates = int(cleaned["loan_interest_rate"].isna().sum())
    if missing_interest_rates:
        issues.append(
            CleaningIssue(
                rule="missing_loan_interest_rate",
                severity="WARNING",
                message=("Missing interest rates were preserved for downstream handling."),
                affected_rows=missing_interest_rates,
            )
        )

    # Validate standardized categorical values.
    invalid_purpose = int(
        (cleaned["loan_purpose"].notna() & ~cleaned["loan_purpose"].isin(_VALID_PURPOSES)).sum()
    )
    if invalid_purpose:
        issues.append(
            CleaningIssue(
                rule="invalid_loan_purpose",
                severity="WARNING",
                message="Loan purposes contain unrecognized values.",
                affected_rows=invalid_purpose,
            )
        )

    invalid_grade = int(
        (cleaned["risk_grade"].notna() & ~cleaned["risk_grade"].isin(_VALID_GRADES)).sum()
    )
    if invalid_grade:
        issues.append(
            CleaningIssue(
                rule="invalid_risk_grade",
                severity="WARNING",
                message="Risk grades contain unrecognized values.",
                affected_rows=invalid_grade,
            )
        )

    outcome = pd.to_numeric(cleaned["loan_outcome"], errors="coerce")
    invalid_outcome = int(
        (cleaned["loan_outcome"].notna() & (outcome.isna() | ~outcome.isin(_VALID_OUTCOMES))).sum()
    )
    if invalid_outcome:
        issues.append(
            CleaningIssue(
                rule="invalid_loan_outcome",
                severity="ERROR",
                message="Loan outcomes must be either 0 or 1.",
                affected_rows=invalid_outcome,
            )
        )

    report = LoanApplicationCleaningReport(
        input_rows=input_rows,
        output_rows=len(cleaned),
        duplicate_rows_removed=duplicate_rows_removed,
        categorical_values_standardized=categorical_values_standardized,
        issues=tuple(issues),
    )

    return LoanApplicationCleaningResult(data=cleaned, report=report)
