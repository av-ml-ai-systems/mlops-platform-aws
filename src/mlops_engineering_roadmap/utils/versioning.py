# Module: versioning.py
# Path: src/mlops_engineering_roadmap/utils/versioning.py
# Purpose: Manage dataset versions, metadata, and artifact integrity.
# Description: Creates metadata, calculates SHA-256 hashes, and registers immutable dataset versions

"""Manage dataset version metadata and artifact integrity."""

import hashlib
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from mlops_engineering_roadmap.utils.logger import get_logger

logger = get_logger(__name__)


def calculate_file_sha256(file_path: Path) -> str:
    """Calculate the SHA-256 digest of a file without loading it entirely."""
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def create_dataset_metadata(
    dataset_name: str,
    version: str,
    source_file: str,
    pipeline: str,
) -> dict[str, Any]:
    """Create dataset metadata with a UTC creation timestamp."""
    return {
        "dataset_name": dataset_name,
        "version": version,
        "source_file": source_file,
        "pipeline": pipeline,
        "created_at": datetime.now(UTC).isoformat(),
    }


def save_dataset_metadata(
    metadata: dict[str, Any],
    output_path: Path,
) -> None:
    """Save dataset metadata as YAML using an atomic file replacement."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            yaml.safe_dump(metadata, file, sort_keys=False)

        os.replace(temporary_path, output_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    logger.info("Dataset metadata saved: %s", output_path)


def load_dataset_metadata(input_path: Path) -> dict[str, Any]:
    """Load dataset metadata from YAML and validate its top-level type."""
    with input_path.open(mode="r", encoding="utf-8") as file:
        metadata = yaml.safe_load(file)

    if not isinstance(metadata, dict):
        raise ValueError(f"Dataset metadata must contain a YAML mapping: {input_path}")

    return metadata


def register_dataset_version(
    registry_path: Path,
    dataset_name: str,
    version: str,
    metadata: dict[str, Any],
) -> None:
    """Register a dataset version without replacing an existing version."""
    if not dataset_name.strip():
        raise ValueError("Dataset name must not be empty.")

    if not version.strip():
        raise ValueError("Dataset version must not be empty.")

    if registry_path.exists():
        registry = load_dataset_metadata(registry_path)
    else:
        registry = {}

    datasets = registry.setdefault("datasets", {})
    if not isinstance(datasets, dict):
        raise ValueError("The dataset registry must contain a 'datasets' mapping.")

    dataset_record = datasets.get(dataset_name, {})
    if not isinstance(dataset_record, dict):
        raise ValueError(f"Invalid registry entry for dataset: {dataset_name}")

    versions = dataset_record.get("versions")
    if versions is None:
        versions = {}
        legacy_version = dataset_record.get("version")

        if legacy_version is not None:
            legacy_entry = dict(dataset_record)
            legacy_entry.pop("version", None)
            legacy_entry["version"] = str(legacy_version)
            versions[str(legacy_version)] = legacy_entry
    elif not isinstance(versions, dict):
        raise ValueError(f"Invalid versions mapping for dataset: {dataset_name}")

    if version in versions:
        raise FileExistsError(f"Dataset version already exists: {dataset_name} {version}")

    version_metadata = dict(metadata)
    version_metadata["version"] = version
    version_metadata.setdefault("created_at", datetime.now(UTC).isoformat())

    versions[version] = version_metadata
    dataset_record["versions"] = versions
    dataset_record["latest_version"] = version
    dataset_record.setdefault("status", "curated")
    datasets[dataset_name] = dataset_record
    registry["datasets"] = datasets

    save_dataset_metadata(registry, registry_path)
