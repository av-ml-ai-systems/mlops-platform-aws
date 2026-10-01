# ADR-002 — S3 Data Lake Layering

## Status

Accepted

## Context

The initial Phase 02 architecture treated S3 primarily as a generic storage location for raw, processed, feature, and model artifacts.

As the data lifecycle became more clearly defined, that structure was insufficient to distinguish source preservation, domain-level data engineering, ML dataset curation, and model-specific preprocessing.

The project therefore requires explicit logical data states.

## Decision

The S3 data lake will use three primary logical data layers:

```text
RAW
  ↓
STANDARDIZED
  ↓
CURATED
```

### Raw

Raw preserves the original source data as faithfully as possible.

It is the reproducible starting point for downstream processing.

### Standardized

Standardized contains domain-level data-engineering outputs derived from Raw.

For the current project, this includes:

* Customer
* Financial History
* Loan Application

Domain decomposition is considered a transformation and therefore belongs conceptually in Standardized rather than Raw.

### Curated

Curated contains integrated ML-oriented datasets produced from standardized domain data.

The current project will combine the standardized domains into a curated loan-risk dataset.

## Processing Boundary

The resulting lifecycle is:

```text
Original Source
      ↓
Raw
      ↓
Domain Processing
      ↓
Standardized
      ↓
Cross-Domain Integration
      ↓
Curated
      ↓
ML Preprocessing
      ↓
Training-Ready
```

Training-ready data is a downstream ML artifact and is not considered a fourth primary data-lake layer.

## Consequences

### Positive

* Preserves original source data.
* Provides explicit data lineage.
* Separates data engineering from ML preprocessing.
* Makes dataset state understandable to downstream consumers.
* Supports reproducibility.
* Prevents model-specific transformations from contaminating curated datasets.

### Negative

* Requires additional storage states.
* Requires explicit movement and lineage between states.
* Requires clear naming and versioning conventions.
* Existing local Phase 1 paths do not necessarily correspond one-to-one with the logical S3 architecture.

## Result

The S3 architecture is based on data state rather than on individual AWS services.

The three layers are logical states:

```text
Raw → Standardized → Curated
```

AWS services operate on these states but do not define the states themselves.
