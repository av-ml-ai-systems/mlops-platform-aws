# Module: test_cleaning_pipeline
# Path: tests/data/test_cleaning_pipeline.py
# Purpose: Test domain-cleaning orchestration and persistence.

import json
from pathlib import Path

import pandas as pd
import pytest

from mlops_engineering_roadmap.data.cleaning import pipeline
from mlops_engineering_roadmap.data.cleaning.pipeline import (
    CleaningPipelineError,
    run_cleaning_pipeline,
)


def create_raw_datasets(raw_data_dir: Path) -> None:
    """Create minimal raw datasets for pipeline tests."""
    customer_dir = raw_data_dir / "customer"
    financial_dir = raw_data_dir / "financial_history"
    application_dir = raw_data_dir / "loan_application"

    customer_dir.mkdir(parents=True)
    financial_dir.mkdir(parents=True)
    application_dir.mkdir(parents=True)

    pd.DataFrame(
        {
            "customer_id": ["C000001", "C000002"],
            "age": [25, 35],
            "income": [50000, 65000],
            "home_ownership": ["RENT", "OWN"],
            "employment_length": [3, 10],
        }
    ).to_csv(customer_dir / "customer.csv", index=False)

    pd.DataFrame(
        {
            "customer_id": ["C000001", "C000002"],
            "default_history": ["N", "Y"],
            "credit_history_length": [3, 8],
        }
    ).to_csv(
        financial_dir / "financial_history.csv",
        index=False,
    )

    pd.DataFrame(
        {
            "application_id": ["A000001", "A000002"],
            "customer_id": ["C000001", "C000002"],
            "loan_amount": [5000, 10000],
            "loan_purpose": ["PERSONAL", "EDUCATION"],
            "risk_grade": ["A", "B"],
            "loan_interest_rate": [10.5, None],
            "loan_income_ratio": [0.10, 0.20],
            "loan_outcome": [0, 1],
        }
    ).to_csv(
        application_dir / "loan_application.csv",
        index=False,
    )


def test_pipeline_persists_datasets_and_reports(tmp_path: Path) -> None:
    raw_data_dir = tmp_path / "raw"
    processed_data_dir = tmp_path / "processed"
    create_raw_datasets(raw_data_dir)

    report = run_cleaning_pipeline(
        raw_data_dir=raw_data_dir,
        processed_data_dir=processed_data_dir,
    )

    expected_domains = {
        "customer",
        "financial_history",
        "loan_application",
    }

    assert set(report.domains) == expected_domains
    assert set(report.output_paths) == expected_domains
    assert set(report.report_paths) == expected_domains

    for domain in expected_domains:
        output_path = Path(report.output_paths[domain])
        report_path = Path(report.report_paths[domain])

        assert output_path.is_file()
        assert report_path.is_file()

        saved_report = json.loads(report_path.read_text(encoding="utf-8"))
        assert saved_report == report.domains[domain]

        cleaned_data = pd.read_csv(output_path)
        assert len(cleaned_data) == 2

    # The missing interest rate is preserved for downstream handling.
    applications = pd.read_csv(report.output_paths["loan_application"])
    assert applications["loan_interest_rate"].isna().sum() == 1


def test_pipeline_does_not_modify_raw_inputs(tmp_path: Path) -> None:
    raw_data_dir = tmp_path / "raw"
    processed_data_dir = tmp_path / "processed"
    create_raw_datasets(raw_data_dir)

    raw_paths = [
        raw_data_dir / "customer" / "customer.csv",
        raw_data_dir / "financial_history" / "financial_history.csv",
        raw_data_dir / "loan_application" / "loan_application.csv",
    ]
    original_contents = {path: path.read_bytes() for path in raw_paths}

    run_cleaning_pipeline(raw_data_dir, processed_data_dir)

    for path, original_content in original_contents.items():
        assert path.read_bytes() == original_content


def test_pipeline_fails_when_an_input_is_missing(
    tmp_path: Path,
) -> None:
    raw_data_dir = tmp_path / "raw"
    processed_data_dir = tmp_path / "processed"
    create_raw_datasets(raw_data_dir)

    (raw_data_dir / "financial_history" / "financial_history.csv").unlink()

    with pytest.raises(CleaningPipelineError):
        run_cleaning_pipeline(raw_data_dir, processed_data_dir)

    assert not processed_data_dir.exists()


def test_pipeline_does_not_publish_when_cleaning_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_data_dir = tmp_path / "raw"
    processed_data_dir = tmp_path / "processed"
    create_raw_datasets(raw_data_dir)

    def fail_cleaning(dataset: pd.DataFrame) -> None:
        raise ValueError("Simulated cleaning failure")

    monkeypatch.setattr(
        pipeline,
        "clean_financial_history_dataset",
        fail_cleaning,
    )

    with pytest.raises(CleaningPipelineError):
        run_cleaning_pipeline(raw_data_dir, processed_data_dir)

    assert not processed_data_dir.exists()
