# Phase 02 — Data Platform Architecture

## 1. Purpose

This document defines the target architecture of the Phase 02 ML data platform.

The architecture extends the local-first data foundation developed in Phase 01 into an AWS-based data platform while preserving reproducibility, clear processing boundaries, dataset lineage, and cost-conscious infrastructure management.

The architecture distinguishes:

* logical data states;
* data storage;
* data engineering;
* metadata management;
* analytical querying;
* ML-specific preprocessing;
* training-ready data;
* and infrastructure lifecycle.

The architecture is designed so that AWS services can be provisioned, validated, inspected, documented, and destroyed without losing the ability to reconstruct the environment from the local project.

---

## 2. Architectural Principles

The Phase 02 platform follows these principles:

1. **S3 is the data storage layer.**
2. **Raw data preserves the original source.**
3. **Standardized data represents domain-level data engineering outputs.**
4. **Curated data represents integrated ML-oriented datasets.**
5. **Data engineering and ML preprocessing are separate responsibilities.**
6. **Validation is an explicit quality gate, not an automatic repair mechanism.**
7. **Glue is used primarily for data engineering and data integration.**
8. **SageMaker Processing is used primarily for ML-specific preprocessing and training-ready data preparation.**
9. **Glue Data Catalog provides metadata and schema discovery; it does not store the datasets themselves.**
10. **Athena provides SQL-based exploration and validation over data stored in S3.**
11. **The local project is the primary reconstruction source for the learning environment.**
12. **AWS infrastructure is ephemeral by default during development and learning.**
13. **Terraform defines infrastructure so that AWS resources can be recreated reproducibly.**
14. **Logical data architecture is independent from the temporary lifecycle of AWS infrastructure.**

---

## 3. High-Level Architecture

```text
                         DATA SOURCES
                              │
                              ▼
                    ┌──────────────────┐
                    │    S3 DATA LAKE  │
                    │                  │
                    │       RAW        │
                    │        │         │
                    │        ▼         │
                    │   STANDARDIZED   │
                    │        │         │
                    │        ▼         │
                    │     CURATED      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
           AWS Glue     Glue Data       Athena
                         Catalog
              │              │              │
              │              │              │
              └──────────────┴──────────────┘
                             │
                             ▼
                    CURATED VALIDATION
                             │
                             ▼
                  SAGEMAKER PROCESSING
                             │
                             ▼
                    TRAINING-READY DATA
                             │
                             ▼
                   SAGEMAKER TRAINING
```

Glue Data Catalog and Athena are cross-cutting platform services. They are not sequential data-processing stages.

The logical data lifecycle is:

```text
RAW
  ↓
STANDARDIZED
  ↓
CURATED
  ↓
TRAINING-READY
```

---

## 4. S3 Data Lake

S3 is the durable object-storage layer of the ML data platform.

It provides storage for datasets and data artifacts throughout the ML data lifecycle.

S3 is responsible for storing:

* source datasets;
* standardized datasets;
* curated datasets;
* training-ready datasets;
* validation artifacts;
* metadata artifacts;
* dataset versions;
* lineage-related artifacts;
* and other reproducibility-related data artifacts.

S3 does not perform:

* data transformations;
* validation logic;
* SQL queries;
* ML training;
* ML preprocessing;
* or workflow orchestration.

Those responsibilities belong to other components of the platform.

### 4.1 Logical Data Layers

The S3 data lake contains three primary logical data states:

```text
RAW
  ↓
STANDARDIZED
  ↓
CURATED
```

These are logical data states rather than separate AWS services.

---

## 5. Raw Layer

The Raw layer preserves the original source data as faithfully as possible.

It answers:

> What data did we receive?

The Raw layer should preserve the source representation and provide a reproducible starting point for downstream processing.

Permitted operations at ingestion include technical operations required to safely land the source, such as:

* file transfer;
* decompression;
* encoding handling;
* ingestion metadata;
* structural checks required for safe ingestion.

Raw data must not silently undergo:

* imputation;
* business-rule correction;
* feature engineering;
* categorical encoding;
* ML-specific transformations;
* arbitrary outlier removal;
* or business-driven filtering.

The original source dataset therefore remains available as the authoritative starting point for lineage.

---

## 6. Standardized Layer

The Standardized layer contains domain-level datasets produced from the Raw source through controlled data-engineering transformations.

It answers:

> What does the source data look like after structural and domain-level standardization?

Typical operations include:

* schema normalization;
* column-name normalization;
* data-type normalization;
* domain decomposition;
* structural cleaning;
* domain-level standardization;
* controlled categorical normalization;
* technical identifier generation;
* domain-level transformations;
* domain-level validation.

For the current loan-risk project, the Standardized layer contains domain datasets such as:

```text
Customer
Financial History
Loan Application
```

These datasets are derived from the original source and therefore are not considered Raw data in the logical S3 architecture.

---

## 7. Curated Layer

The Curated layer contains integrated, ML-oriented datasets produced from standardized domain data.

It answers:

> What data have we deliberately assembled for ML use?

Typical operations include:

* cross-domain joins;
* relationship construction;
* business-level consistency rules;
* selection of ML-relevant fields;
* construction of analytical datasets;
* curated dataset validation;
* lineage metadata.

For the current project:

```text
Customer
      +
Financial History
      +
Loan Application
      │
      ▼
Curated Loan-Risk Dataset
```

The Curated layer is not automatically training-ready.

Model-specific preprocessing such as encoding, scaling, training-derived imputation, or train/validation/test preparation occurs downstream.

---

## 8. Glue Data Catalog

The AWS Glue Data Catalog provides the metadata layer for datasets stored in S3.

It describes data rather than storing the data itself.

The Catalog may contain:

* databases;
* table definitions;
* schemas;
* column names;
* data types;
* S3 locations;
* partition metadata;
* and metadata required by downstream AWS services.

Conceptually:

```text
S3
→ actual data objects

Glue Data Catalog
→ metadata describing those objects
```

The Catalog provides a common metadata layer for the Raw, Standardized, and Curated datasets that are registered for AWS analytical and processing workflows.

---

## 9. Amazon Athena

Athena provides SQL-based analytical access to datasets stored in S3.

Athena is used for:

* exploratory SQL;
* dataset inspection;
* validation queries;
* data profiling;
* join verification;
* anomaly investigation;
* schema inspection;
* and verification of processing outputs.

Athena is not the primary data-transformation engine.

Substantial data-engineering transformations belong in the processing layer.

---

## 10. AWS Glue Processing

AWS Glue is the primary data-engineering processing environment in Phase 02.

Its responsibilities include:

* domain-level standardization;
* structural transformations;
* domain processing;
* cross-domain integration;
* preparation of curated datasets;
* and associated data-engineering validation.

The primary conceptual boundary is:

```text
Raw
  ↓
AWS Glue
  ↓
Standardized
  ↓
AWS Glue
  ↓
Curated
```

Glue processing should remain independent of ML-model-specific preprocessing.

---

## 11. Data Validation

Validation is an architectural quality gate rather than an automatic repair mechanism.

Two principal validation boundaries exist.

### 11.1 Source / Ingestion Validation

Source validation determines whether the incoming data can safely enter the data-engineering workflow.

Typical checks include:

* required columns;
* compatible data types;
* malformed records;
* valid categorical values;
* identifier integrity;
* duplicate detection;
* required fields;
* basic range and format checks.

A validation failure should produce an explicit validation result and, where appropriate, reject, quarantine, or require investigation of the affected data.

### 11.2 Curated Dataset Validation

Curated validation determines whether the integrated dataset is valid for ML use.

Typical checks include:

* cross-domain consistency;
* referential integrity;
* business rules;
* impossible combinations;
* duplicate entities;
* target validity;
* completeness;
* acceptable ranges;
* and dataset-level consistency.

The conceptual gate is:

```text
                 CURATED DATASET
                        │
                        ▼
                CURATED VALIDATION
                   /          \
                PASS           FAIL
                 │               │
                 ▼               ▼
          ML PREPROCESSING   Reject /
                             Quarantine /
                             Investigate
```

Validation does not imply automatic correction.

---

## 12. SageMaker Processing

SageMaker Processing is the primary ML-specific data-preparation environment.

Its responsibilities begin after the curated dataset has passed the relevant validation gates.

Typical operations include:

* missing-value strategy;
* categorical encoding;
* numerical transformations;
* feature preparation;
* training/validation/test preparation;
* ML-specific transformations;
* and training/inference consistency.

The boundary is:

```text
CURATED
   ↓
SageMaker Processing
   ↓
TRAINING-READY
```

This separation prevents model-specific preprocessing from contaminating the general-purpose curated dataset.

---

## 13. Training-Ready Dataset

The Training-Ready dataset is the downstream output of ML-specific preprocessing.

It is designed to be consumed by training workflows while preserving reproducibility and lineage.

It may include:

* transformed features;
* encoded variables;
* model-specific preprocessing outputs;
* training/validation/test datasets;
* preprocessing metadata;
* and references to the source curated dataset.

The Training-Ready dataset is therefore a downstream ML artifact rather than a fourth primary S3 data-lake layer.

---

## 14. Data Lineage

The intended lineage is:

```text
Original Source
      │
      ▼
S3 Raw
      │
      │ domain/data engineering
      ▼
S3 Standardized
      │
      │ integration / curation
      ▼
S3 Curated
      │
      │ ML preprocessing
      ▼
Training-Ready
      │
      ▼
Model Training
```

Each downstream dataset should be traceable to the dataset and processing configuration from which it was produced.

Dataset versioning and lineage conventions are defined separately as the implementation evolves.

---

## 15. Local-First Development Model

The Phase 02 architecture remains local-first.

The local project is the primary reconstruction source for the learning environment.

It contains the definitions necessary to reconstruct the AWS environment, including:

* application and processing code;
* tests;
* Terraform configuration;
* SQL;
* configuration;
* documentation;
* and version-controlled architectural decisions.

Git provides local version history.

GitHub provides remote repository storage, backup, and portfolio visibility.

AWS provides the execution and validation environment.

The architecture therefore does not depend on AWS resources remaining permanently deployed.

---

## 16. Ephemeral AWS Infrastructure

AWS infrastructure is ephemeral by default during Phase 02 development and validation.

The operating model is:

```text
Local Project
     │
     ▼
Terraform
     │
     ▼
Create AWS
     │
     ▼
Verify
     │
     ▼
Console Inspection
     │
     ▼
Capture Evidence
     │
     ▼
Document
     │
     ▼
Destroy AWS
     │
     ▼
Recreate Later
```

This applies to the learning/development deployment strategy.

It does not change the logical role of S3 as the data-storage layer in the target platform architecture.

The distinction is therefore:

```text
Logical architecture
→ S3 is the data-storage layer.

Development deployment
→ AWS resources are provisioned temporarily and reconstructed when required.
```

Infrastructure destruction must be deliberate and controlled.

---

## 17. Infrastructure as Code

Terraform is the infrastructure-definition mechanism for AWS resources in Phase 02.

Terraform configuration remains inside the local project and is version-controlled together with the rest of the platform.

Terraform provides:

* reproducible infrastructure definitions;
* explicit resource configuration;
* controlled provisioning;
* controlled destruction;
* and environment reconstruction.

The project repository, rather than an already-running AWS environment, remains the primary reconstruction source.

---

## 18. Architectural Boundaries

The principal Phase 02 boundaries are:

```text
S3
→ storage

Glue Data Catalog
→ metadata and schema discovery

Athena
→ SQL exploration and validation queries

AWS Glue
→ data engineering and integration

Validation
→ explicit data-quality gates

SageMaker Processing
→ ML-specific preprocessing

SageMaker Training
→ model training
```

These boundaries are intentionally explicit to prevent responsibilities from becoming duplicated or mixed across services.

---

## 19. Current Target Architecture

```text
                         DATA SOURCES
                              │
                              ▼
                    ┌──────────────────┐
                    │    S3 DATA LAKE  │
                    │                  │
                    │       RAW        │
                    │        │         │
                    │        ▼         │
                    │   STANDARDIZED   │
                    │        │         │
                    │        ▼         │
                    │     CURATED      │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
        AWS Glue       Glue Data Catalog   Athena
            │                │                │
            │                │                │
            └────────────────┼────────────────┘
                             │
                             ▼
                    CURATED VALIDATION
                             │
                             ▼
                  SAGEMAKER PROCESSING
                             │
                             ▼
                    TRAINING-READY DATA
                             │
                             ▼
                   SAGEMAKER TRAINING
```

This architecture establishes the Phase 02 data-platform foundation. Detailed processing, training, governance, orchestration, and implementation decisions are documented in their respective architecture documents and ADRs as those areas become sufficiently defined.
