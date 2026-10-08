# Module: validator.py
# Path: src/mlops_engineering_roadmap/data/validation/validator.py
# Purpose: Execute validation rules and build validation reports.
# Description: Provides the shared validation workflow for domain datasets.


from collections.abc import Callable, Sequence

import pandas as pd

from mlops_engineering_roadmap.data.validation.models import (
    ValidationReport,
    ValidationResult,
)

ValidationRule = Callable[[pd.DataFrame], ValidationResult]


def validate_dataset(
    dataset: pd.DataFrame,
    dataset_name: str,
    rules: Sequence[ValidationRule],
) -> ValidationReport:
    """Execute validation rules against a dataset and return a report."""
    results = tuple(rule(dataset) for rule in rules)

    return ValidationReport(
        dataset=dataset_name,
        results=results,
    )
