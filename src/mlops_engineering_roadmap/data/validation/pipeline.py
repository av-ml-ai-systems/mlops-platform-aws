# Module: pipeline.py
# Path: src/mlops_engineering_roadmap/data/validation/pipeline.py
# Purpose: Orchestrate domain validation and persist validation reports.
# Description: Reuse existing domain validation rules without modifying data.

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from mlops_engineering_roadmap.data.validation.customer import (
    CUSTOMER_VALIDATION_RULES,
)
from mlops_engineering_roadmap.data.validation.financial_history import (
    FINANCIAL_HISTORY_VALIDATION_RULES,
)
from mlops_engineering_roadmap.data.validation.loan_application import (
    LOAN_APPLICATION_VALIDATION_RULES,
)
from mlops_engineering_roadmap.data.validation.validator import (
    ValidationReport,
    validate_dataset,
)


class ValidationPipelineError(RuntimeError):
    """Raised when the validation pipeline cannot complete successfully."""


@dataclass(frozen=True)
class ValidationPipelineReport:
    """Summary of a successful validation pipeline execution."""

    reports: dict[str, dict[str, Any]]
    report_paths: dict[str, str]


def run_validation_pipeline(
    processed_data_dir: Path,
) -> ValidationPipelineReport:
    """Validate cleaned datasets and persist domain validation reports."""
    processed_data_dir = Path(processed_data_dir)

    domain_configs = {
        "customer": (
            processed_data_dir / "customer" / "customer.csv",
            CUSTOMER_VALIDATION_RULES,
        ),
        "financial_history": (
            processed_data_dir / "financial_history" / "financial_history.csv",
            FINANCIAL_HISTORY_VALIDATION_RULES,
        ),
        "loan_application": (
            processed_data_dir / "loan_application" / "loan_application.csv",
            LOAN_APPLICATION_VALIDATION_RULES,
        ),
    }

    validation_reports: dict[str, ValidationReport] = {}

    # Read and validate every domain before publishing reports.
    try:
        for domain, (dataset_path, rules) in domain_configs.items():
            if not dataset_path.is_file():
                raise FileNotFoundError(
                    f"Cleaned dataset for '{domain}' was not found: {dataset_path}"
                )

            dataset = pd.read_csv(dataset_path)

            validation_reports[domain] = validate_dataset(
                dataset=dataset,
                dataset_name=domain,
                rules=rules,
            )

    except Exception as exc:
        raise ValidationPipelineError(
            "Validation failed. No new validation reports were published."
        ) from exc

    reports_root = processed_data_dir / "validation_reports"
    serialized_reports: dict[str, dict[str, Any]] = {}
    report_paths: dict[str, str] = {}

    for domain, report in validation_reports.items():
        report_data = asdict(report)
        report_data["overall_status"] = report.overall_status

        serialized_reports[domain] = json.loads(
            json.dumps(
                report_data,
                indent=2,
                ensure_ascii=False,
            )
        )
        report_paths[domain] = str(reports_root / f"{domain}.json")

    # Stage every report before publishing any of them.
    try:
        with tempfile.TemporaryDirectory(
            prefix=".validation-stage-",
            dir=processed_data_dir,
        ) as temporary_directory:
            staging_root = Path(temporary_directory)

            for domain, report_data in serialized_reports.items():
                staged_path = staging_root / f"{domain}.json"
                staged_path.write_text(
                    json.dumps(
                        report_data,
                        indent=2,
                        ensure_ascii=False,
                    )
                    + "\n",
                    encoding="utf-8",
                )

            reports_root.mkdir(parents=True, exist_ok=True)

            for domain in serialized_reports:
                staged_path = staging_root / f"{domain}.json"
                final_path = reports_root / f"{domain}.json"
                os.replace(staged_path, final_path)

    except Exception as exc:
        raise ValidationPipelineError(
            "Validation reports could not be staged or published."
        ) from exc

    return ValidationPipelineReport(
        reports=serialized_reports,
        report_paths=report_paths,
    )
