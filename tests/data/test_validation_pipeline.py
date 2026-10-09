# Module: test_validation_pipeline.py
# Path: tests/data/test_validation_pipeline.py
# Purpose: Test domain-validation orchestration and report persistence.

import json
from pathlib import Path

import pandas as pd
import pytest

from mlops_engineering_roadmap.data.validation.pipeline import (
    ValidationPipelineError,
    run_validation_pipeline,
)


def create_processed_datasets(processed_data_dir: Path) -> None:
    """Create valid cleaned datasets for validation pipeline tests."""
    customer_dir = processed_data_dir / "customer"
    financial_dir = processed_data_dir / "financial_history"
    application_dir = processed_data_dir / "loan_application"

    customer_dir.mkdir(parents=True)
    financial_dir.mkdir(parents=True)
    application_dir.mkdir(parents=True)

    pd.DataFrame(
        {
            "customer_id": ["C000001", "C000002"],
            "age": pd.Series([25, 35], dtype="int64"),
            "income": pd.Series([50000, 65000], dtype="int64"),
            "home_ownership": ["RENT", "OWN"],
            "employment_length": pd.Series([3.0, 10.0], dtype="float64"),
        }
    ).to_csv(customer_dir / "customer.csv", index=False)

    pd.DataFrame(
        {
            "customer_id": ["C000001", "C000002"],
            "default_history": ["N", "Y"],
            "credit_history_length": pd.Series([3, 8], dtype="int64"),
        }
    ).to_csv(
        financial_dir / "financial_history.csv",
        index=False,
    )

    pd.DataFrame(
        {
            "application_id": ["A000001", "A000002"],
            "customer_id": ["C000001", "C000002"],
            "loan_amount": pd.Series([5000, 10000], dtype="int64"),
            "loan_purpose": ["PERSONAL", "EDUCATION"],
            "risk_grade": ["A", "B"],
            "loan_interest_rate": pd.Series(
                [10.5, float("nan")],
                dtype="float64",
            ),
            "loan_income_ratio": pd.Series(
                [0.10, 0.20],
                dtype="float64",
            ),
            "loan_outcome": pd.Series([0, 1], dtype="int64"),
        }
    ).to_csv(
        application_dir / "loan_application.csv",
        index=False,
    )


def test_validation_pipeline_persists_reports(
    tmp_path: Path,
) -> None:
    processed_data_dir = tmp_path / "processed"
    create_processed_datasets(processed_data_dir)

    report = run_validation_pipeline(processed_data_dir)

    expected_domains = {
        "customer",
        "financial_history",
        "loan_application",
    }

    assert set(report.reports) == expected_domains
    assert set(report.report_paths) == expected_domains

    for domain in expected_domains:
        report_path = Path(report.report_paths[domain])

        assert report_path.is_file()

        saved_report = json.loads(report_path.read_text(encoding="utf-8"))

        assert saved_report == report.reports[domain]
        assert saved_report["overall_status"] == "PASS"


def test_validation_pipeline_reports_validation_failures(
    tmp_path: Path,
) -> None:
    processed_data_dir = tmp_path / "processed"
    create_processed_datasets(processed_data_dir)

    customer_path = processed_data_dir / "customer" / "customer.csv"
    customer_data = pd.read_csv(customer_path)
    customer_data.loc[0, "age"] = 15
    customer_data.to_csv(customer_path, index=False)

    report = run_validation_pipeline(processed_data_dir)

    customer_report = report.reports["customer"]

    assert customer_report["overall_status"] == "FAIL"
    assert any(
        result["rule"] == "customer_values" and result["status"] == "FAIL"
        for result in customer_report["results"]
    )


def test_validation_pipeline_fails_when_an_input_is_missing(
    tmp_path: Path,
) -> None:
    processed_data_dir = tmp_path / "processed"
    create_processed_datasets(processed_data_dir)

    (processed_data_dir / "financial_history" / "financial_history.csv").unlink()

    with pytest.raises(ValidationPipelineError):
        run_validation_pipeline(processed_data_dir)

    assert not (processed_data_dir / "validation_reports").exists()


def test_validation_pipeline_does_not_modify_datasets(
    tmp_path: Path,
) -> None:
    processed_data_dir = tmp_path / "processed"
    create_processed_datasets(processed_data_dir)

    dataset_paths = [
        processed_data_dir / "customer" / "customer.csv",
        (processed_data_dir / "financial_history" / "financial_history.csv"),
        (processed_data_dir / "loan_application" / "loan_application.csv"),
    ]

    original_contents = {path: path.read_bytes() for path in dataset_paths}

    run_validation_pipeline(processed_data_dir)

    for path, original_content in original_contents.items():
        assert path.read_bytes() == original_content
