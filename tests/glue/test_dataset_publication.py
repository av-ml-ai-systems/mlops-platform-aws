# Module: test_dataset_publication.py
# Path: tests/glue/test_dataset_publication.py
# Purpose: Test versioned dataset publication and S3 artifact metadata.
# Description: Tests version validation, collision protection, hashes, and metadata writes.

"""Test versioned dataset publication helpers without accessing AWS."""

import hashlib
import importlib.util
import json
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "glue" / "curate_loan_dataset.py"

SPEC = importlib.util.spec_from_file_location(
    "curate_loan_dataset",
    MODULE_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load ETL module from {MODULE_PATH}")

ETL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ETL
SPEC.loader.exec_module(ETL)


@pytest.mark.parametrize(
    "version",
    ["1.0.0", "1.0.1", "phase-2_release", "v2"],
)
def test_validate_dataset_version_accepts_safe_versions(version: str) -> None:
    assert ETL._validate_dataset_version(version) == version


@pytest.mark.parametrize(
    "version",
    ["", "../1.0.0", "/tmp", "version with spaces", "-invalid", "a" * 65],
)
def test_validate_dataset_version_rejects_unsafe_versions(
    version: str,
) -> None:
    with pytest.raises(ValueError):
        ETL._validate_dataset_version(version)


def test_assert_version_available_accepts_unused_version() -> None:
    s3_client = MagicMock()
    s3_client.list_objects_v2.return_value = {}

    ETL._assert_version_available(
        s3_client,
        "test-bucket",
        "curated/loan_risk_dataset/versions/1.0.0/",
        "metadata/versions/loan_risk_dataset/1.0.0.json",
    )

    assert s3_client.list_objects_v2.call_count == 2


def test_assert_version_available_rejects_existing_output() -> None:
    s3_client = MagicMock()
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "curated/loan_risk_dataset/versions/1.0.0/part.csv"}]
    }

    with pytest.raises(FileExistsError, match="output version already exists"):
        ETL._assert_version_available(
            s3_client,
            "test-bucket",
            "curated/loan_risk_dataset/versions/1.0.0/",
            "metadata/versions/loan_risk_dataset/1.0.0.json",
        )


def test_assert_version_available_rejects_existing_metadata() -> None:
    s3_client = MagicMock()
    s3_client.list_objects_v2.side_effect = [
        {},
        {"Contents": [{"Key": "metadata/versions/loan_risk_dataset/1.0.0.json"}]},
    ]

    with pytest.raises(FileExistsError, match="metadata version already exists"):
        ETL._assert_version_available(
            s3_client,
            "test-bucket",
            "curated/loan_risk_dataset/versions/1.0.0/",
            "metadata/versions/loan_risk_dataset/1.0.0.json",
        )


def test_calculate_s3_artifact_manifest_hashes_sorted_csv_objects() -> None:
    s3_client = MagicMock()
    first_content = b"application_id,loan_outcome\n1,0\n"
    second_content = b"application_id,loan_outcome\n2,1\n"

    s3_client.get_paginator.return_value.paginate.return_value = [
        {
            "Contents": [
                {
                    "Key": "dataset/part-00002.csv",
                    "Size": len(second_content),
                },
                {
                    "Key": "dataset/part-00001.csv",
                    "Size": len(first_content),
                },
                {
                    "Key": "dataset/_SUCCESS",
                    "Size": 0,
                },
            ]
        }
    ]

    contents = {
        "dataset/part-00001.csv": first_content,
        "dataset/part-00002.csv": second_content,
    }

    def get_object(*, Bucket: str, Key: str) -> dict[str, object]:
        del Bucket
        return {"Body": BytesIO(contents[Key])}

    s3_client.get_object.side_effect = get_object

    aggregate_hash, files = ETL._calculate_s3_artifact_manifest(
        s3_client,
        "test-bucket",
        "dataset/",
    )

    expected_files = [
        {
            "key": "dataset/part-00001.csv",
            "sha256": hashlib.sha256(first_content).hexdigest(),
        },
        {
            "key": "dataset/part-00002.csv",
            "sha256": hashlib.sha256(second_content).hexdigest(),
        },
    ]

    expected_manifest = hashlib.sha256()
    for item in expected_files:
        expected_manifest.update(item["key"].encode("utf-8"))
        expected_manifest.update(b"\0")
        expected_manifest.update(item["sha256"].encode("ascii"))
        expected_manifest.update(b"\n")

    assert files == expected_files
    assert aggregate_hash == expected_manifest.hexdigest()
    assert s3_client.get_object.call_count == 2


def test_calculate_s3_artifact_manifest_fails_without_csv_files() -> None:
    s3_client = MagicMock()
    s3_client.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": "dataset/_SUCCESS", "Size": 0}]}
    ]

    with pytest.raises(RuntimeError, match="No CSV artifact files found"):
        ETL._calculate_s3_artifact_manifest(
            s3_client,
            "test-bucket",
            "dataset/",
        )


def test_write_dataset_metadata_uses_json() -> None:
    s3_client = MagicMock()
    metadata = {
        "dataset_name": "loan_risk_dataset",
        "version": "1.0.0",
        "artifact": {"rows": 32581},
    }

    ETL._write_dataset_metadata(
        s3_client,
        "test-bucket",
        "metadata/versions/loan_risk_dataset/1.0.0.json",
        metadata,
    )

    kwargs = s3_client.put_object.call_args.kwargs

    assert kwargs["Bucket"] == "test-bucket"
    assert kwargs["Key"] == "metadata/versions/loan_risk_dataset/1.0.0.json"
    assert kwargs["ContentType"] == "application/json"
    assert json.loads(kwargs["Body"].decode("utf-8")) == metadata
