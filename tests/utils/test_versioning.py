# Module: test_versioning.py
# Path: tests/utils/test_versioning.py
# Purpose: Test dataset metadata, SHA-256 integrity, and version registration.
# Description: Tests metadata, SHA-256 integrity, and version registration.

"""Tests for dataset versioning and metadata utilities."""

import hashlib
from pathlib import Path

import pytest
import yaml

from mlops_engineering_roadmap.utils.versioning import (
    calculate_file_sha256,
    create_dataset_metadata,
    load_dataset_metadata,
    register_dataset_version,
    save_dataset_metadata,
)


def test_create_dataset_metadata() -> None:
    """Test dataset metadata creation."""
    metadata = create_dataset_metadata(
        dataset_name="credit_risk_dataset",
        version="v1.0.0",
        source_file="credit_risk_dataset.csv",
        pipeline="preprocessing.py",
    )

    assert metadata["dataset_name"] == "credit_risk_dataset"
    assert metadata["version"] == "v1.0.0"
    assert metadata["source_file"] == "credit_risk_dataset.csv"
    assert metadata["pipeline"] == "preprocessing.py"
    assert "created_at" in metadata


def test_save_dataset_metadata(tmp_path: Path) -> None:
    """Test saving dataset metadata to a YAML file."""
    metadata = create_dataset_metadata(
        dataset_name="credit_risk_dataset",
        version="v1.0.0",
        source_file="credit_risk_dataset.csv",
        pipeline="preprocessing.py",
    )
    output_path = tmp_path / "metadata" / "dataset.yaml"

    save_dataset_metadata(metadata, output_path)

    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        saved_metadata = yaml.safe_load(file)

    assert saved_metadata["dataset_name"] == "credit_risk_dataset"
    assert saved_metadata["version"] == "v1.0.0"


def test_load_dataset_metadata(tmp_path: Path) -> None:
    """Test loading dataset metadata from a YAML file."""
    metadata = {
        "dataset_name": "credit_risk_dataset",
        "version": "v1.0.0",
        "source_file": "credit_risk_dataset.csv",
        "pipeline": "preprocessing.py",
    }
    input_path = tmp_path / "dataset.yaml"

    with input_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(metadata, file)

    loaded_metadata = load_dataset_metadata(input_path)

    assert loaded_metadata["dataset_name"] == "credit_risk_dataset"
    assert loaded_metadata["version"] == "v1.0.0"


def test_calculate_file_sha256(tmp_path: Path) -> None:
    """Test SHA-256 calculation against the expected digest."""
    file_path = tmp_path / "dataset.csv"
    content = b"application_id,loan_status\n1,0\n2,1\n"
    file_path.write_bytes(content)

    expected_digest = hashlib.sha256(content).hexdigest()

    assert calculate_file_sha256(file_path) == expected_digest


def test_register_dataset_version_in_new_registry(
    tmp_path: Path,
) -> None:
    """Test registering a version in a new registry."""
    registry_path = tmp_path / "dataset_versions.yaml"
    metadata = {
        "status": "curated",
        "artifact": {
            "format": "csv",
            "rows": 100,
            "sha256": "abc123",
        },
    }

    register_dataset_version(
        registry_path=registry_path,
        dataset_name="loan_risk_dataset",
        version="1.0.0",
        metadata=metadata,
    )

    registry = load_dataset_metadata(registry_path)
    dataset = registry["datasets"]["loan_risk_dataset"]

    assert dataset["latest_version"] == "1.0.0"
    assert dataset["versions"]["1.0.0"]["version"] == "1.0.0"
    assert dataset["versions"]["1.0.0"]["status"] == "curated"
    assert dataset["versions"]["1.0.0"]["artifact"]["rows"] == 100
    assert dataset["versions"]["1.0.0"]["artifact"]["sha256"] == "abc123"


def test_register_dataset_version_preserves_legacy_metadata(
    tmp_path: Path,
) -> None:
    """Test migration preserves metadata from the existing registry format."""
    registry_path = tmp_path / "dataset_versions.yaml"
    legacy_registry = {
        "datasets": {
            "loan_risk_dataset": {
                "version": "1.0.0",
                "status": "curated",
                "created_at": "2026-10-16",
                "artifact": {
                    "format": "csv",
                    "rows": 32581,
                },
            }
        }
    }

    save_dataset_metadata(legacy_registry, registry_path)

    register_dataset_version(
        registry_path=registry_path,
        dataset_name="loan_risk_dataset",
        version="1.0.1",
        metadata={
            "status": "curated",
            "artifact": {
                "format": "csv",
                "rows": 32581,
                "sha256": "new-digest",
            },
        },
    )

    registry = load_dataset_metadata(registry_path)
    dataset = registry["datasets"]["loan_risk_dataset"]
    versions = dataset["versions"]

    assert dataset["latest_version"] == "1.0.1"
    assert versions["1.0.0"]["status"] == "curated"
    assert versions["1.0.0"]["created_at"] == "2026-10-16"
    assert versions["1.0.0"]["artifact"]["rows"] == 32581
    assert versions["1.0.1"]["artifact"]["sha256"] == "new-digest"


def test_register_dataset_version_rejects_duplicate(
    tmp_path: Path,
) -> None:
    """Test that an existing version cannot be registered again."""
    registry_path = tmp_path / "dataset_versions.yaml"
    metadata = {
        "status": "curated",
        "artifact": {"format": "csv", "rows": 100},
    }

    register_dataset_version(
        registry_path,
        "loan_risk_dataset",
        "1.0.0",
        metadata,
    )
    original_registry = load_dataset_metadata(registry_path)

    with pytest.raises(FileExistsError, match="already exists"):
        register_dataset_version(
            registry_path,
            "loan_risk_dataset",
            "1.0.0",
            metadata,
        )

    assert load_dataset_metadata(registry_path) == original_registry
