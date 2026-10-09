# Module: pipeline
# Path: src/mlops_engineering_roadmap/data/cleaning/pipeline.py
# Purpose: Orchestrate domain cleaning and persist cleaned datasets.
# Description: Coordinate existing domain cleaners without modifying raw inputs.

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from mlops_engineering_roadmap.data.cleaning.customer import (
    clean_customer_dataset,
)
from mlops_engineering_roadmap.data.cleaning.financial_history import (
    clean_financial_history_dataset,
)
from mlops_engineering_roadmap.data.cleaning.loan_application import (
    clean_loan_application_dataset,
)


class CleaningPipelineError(RuntimeError):
    """Raised when the cleaning pipeline cannot complete successfully."""


@dataclass(frozen=True)
class CleaningPipelineReport:
    """Summary of a successful domain-cleaning pipeline run."""

    domains: dict[str, dict[str, Any]]
    output_paths: dict[str, str]
    report_paths: dict[str, str]


def run_cleaning_pipeline(
    raw_data_dir: Path,
    processed_data_dir: Path,
) -> CleaningPipelineReport:
    """Clean all three domain datasets and persist the results."""
    raw_data_dir = Path(raw_data_dir)
    processed_data_dir = Path(processed_data_dir)

    domain_files = {
        "customer": (
            raw_data_dir / "customer" / "customer.csv",
            processed_data_dir / "customer" / "customer.csv",
            clean_customer_dataset,
        ),
        "financial_history": (
            raw_data_dir / "financial_history" / "financial_history.csv",
            processed_data_dir / "financial_history" / "financial_history.csv",
            clean_financial_history_dataset,
        ),
        "loan_application": (
            raw_data_dir / "loan_application" / "loan_application.csv",
            processed_data_dir / "loan_application" / "loan_application.csv",
            clean_loan_application_dataset,
        ),
    }

    # Read and clean every domain before publishing outputs.
    results: dict[str, Any] = {}

    try:
        for domain, (input_path, _, cleaner) in domain_files.items():
            if not input_path.is_file():
                raise FileNotFoundError(f"Raw input for '{domain}' was not found: {input_path}")

            dataset = pd.read_csv(input_path)
            results[domain] = cleaner(dataset)

    except Exception as exc:
        raise CleaningPipelineError(
            "Cleaning failed. No new pipeline outputs were published."
        ) from exc

    output_root = processed_data_dir
    reports_root = output_root / "cleaning_reports"
    output_paths: dict[str, str] = {}
    report_paths: dict[str, str] = {}
    domain_reports: dict[str, dict[str, Any]] = {}

    output_root.parent.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.TemporaryDirectory(
            prefix=".cleaning-stage-",
            dir=output_root.parent,
        ) as temporary_directory:
            staging_root = Path(temporary_directory)

            # Prepare all datasets and reports before publishing.
            for domain, (_, final_data_path, _) in domain_files.items():
                result = results[domain]

                staged_data_path = staging_root / final_data_path.relative_to(output_root)
                staged_report_path = staging_root / "cleaning_reports" / f"{domain}.json"

                staged_data_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                staged_report_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                result.data.to_csv(staged_data_path, index=False)

                # Normalize the report to its JSON-compatible representation.
                report_json = json.dumps(
                    asdict(result.report),
                    indent=2,
                    ensure_ascii=False,
                )

                staged_report_path.write_text(
                    report_json + "\n",
                    encoding="utf-8",
                )

                domain_reports[domain] = json.loads(report_json)
                output_paths[domain] = str(final_data_path)
                report_paths[domain] = str(reports_root / f"{domain}.json")

            # Publish prepared outputs only after preparation succeeds.
            for domain, (_, final_data_path, _) in domain_files.items():
                staged_data_path = staging_root / final_data_path.relative_to(output_root)
                staged_report_path = staging_root / "cleaning_reports" / f"{domain}.json"
                final_report_path = reports_root / f"{domain}.json"

                final_data_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                final_report_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                os.replace(staged_data_path, final_data_path)
                os.replace(staged_report_path, final_report_path)

    except Exception as exc:
        raise CleaningPipelineError(
            "Cleaning outputs could not be staged or published successfully."
        ) from exc

    return CleaningPipelineReport(
        domains=domain_reports,
        output_paths=output_paths,
        report_paths=report_paths,
    )
