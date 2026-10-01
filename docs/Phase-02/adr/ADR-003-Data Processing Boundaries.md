# ADR-003 — Data Processing Boundaries

## Status

Accepted

## Context

The Phase 02 platform uses both AWS Glue and SageMaker Processing.

Without an explicit boundary, responsibilities could become duplicated or mixed between data engineering and ML preprocessing.

The architecture must distinguish general-purpose data preparation from model-specific preparation.

## Decision

AWS Glue and SageMaker Processing have separate primary responsibilities.

### AWS Glue

AWS Glue is the primary data-engineering processing environment.

It is responsible for:

* structural data transformations;
* domain-level standardization;
* domain processing;
* cross-domain integration;
* and construction of curated datasets.

Conceptually:

```text
Raw
  ↓
Glue
  ↓
Standardized
  ↓
Glue
  ↓
Curated
```

### SageMaker Processing

SageMaker Processing is the primary ML-specific data-preparation environment.

It is responsible for:

* ML-specific missing-value strategies;
* categorical encoding;
* numerical transformations;
* feature preparation;
* train/validation/test preparation;
* and training/inference preprocessing consistency.

Conceptually:

```text
Curated
  ↓
SageMaker Processing
  ↓
Training-Ready
```

### Validation

Validation is treated as an architectural quality gate rather than as a property of one specific AWS service.

Validation can execute within an appropriate processing environment, but its architectural role remains distinct from transformation.

Two principal validation boundaries exist:

```text
Source / Ingestion Validation
        ↓
Standardized

Curated Dataset Validation
        ↓
Training Preparation
```

Validation failures must produce explicit outcomes such as rejection, quarantine, or investigation rather than being silently repaired.

## Consequences

### Positive

* Clear separation of responsibilities.
* Reduced risk of mixing data engineering and ML preprocessing.
* Easier local testing.
* Easier service substitution.
* Better training/inference consistency.
* Clearer architecture for future orchestration.

### Negative

* Creates additional processing boundaries.
* Some transformations require deliberate classification.
* Validation logic may need to be shared across environments.

## Result

The Phase 02 processing architecture follows this boundary:

```text
AWS Glue
→ Data Engineering

SageMaker Processing
→ ML-Specific Data Preparation
```

Validation remains a separate architectural concern that acts as a quality gate around the data lifecycle.
