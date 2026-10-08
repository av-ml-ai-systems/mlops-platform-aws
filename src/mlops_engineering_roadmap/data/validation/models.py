# Module: models.py
# Path: src/mlops_engineering_roadmap/data/validation/models.py
# Purpose: Define the data models used by the validation component.
# Description: Provides structured validation results and dataset validation reports.


from dataclasses import dataclass
from typing import Literal

ValidationStatus = Literal["PASS", "WARNING", "FAIL"]
ValidationSeverity = Literal["INFO", "WARNING", "ERROR"]


@dataclass(frozen=True)
class ValidationResult:
    """Represent the result of a single validation rule."""

    rule: str
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    affected_rows: int


@dataclass(frozen=True)
class ValidationReport:
    """Represent the complete validation result for a dataset."""

    dataset: str
    results: tuple[ValidationResult, ...]

    @property
    def overall_status(self) -> ValidationStatus:
        """Return the overall validation status for the dataset."""
        if any(result.status == "FAIL" for result in self.results):
            return "FAIL"

        if any(result.status == "WARNING" for result in self.results):
            return "WARNING"

        return "PASS"
