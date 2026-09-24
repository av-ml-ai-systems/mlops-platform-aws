# Phase 01 — Evolution

## Purpose

This document records the significant architectural and engineering changes that shaped Phase 01 of the MLOps Engineer / AWS Roadmap.

It complements the Phase 01 Summary by documenting how the project evolved during implementation rather than listing every completed component.

---

## Initial Direction

Phase 01 began as the practical ML foundation following the MLOps and AWS infrastructure concepts established in Phase 00.

The objective was to move from MLOps theory toward a concrete machine learning system using a consistent Credit Risk / Loan Approval use case.

The initial workflow was centered around:

```text
Raw Data
    ↓
Data Preparation
    ↓
Feature Engineering
    ↓
Model Development
```

During implementation, this evolved into a more structured data engineering and feature engineering platform.

---

## Evolution Toward a Data Engineering Platform

Rather than treating preprocessing and feature engineering as notebook-level activities, the project moved these responsibilities into reusable Python modules.

The resulting architecture became:

```text
Raw Data
    ↓
Data Ingestion
    ↓
Data Validation
    ↓
Data Preprocessing
    ↓
Processed Dataset
    ↓
Feature Engineering
    ↓
Feature Dataset
```

This was a significant shift from an analysis-oriented workflow toward a reproducible engineering pipeline.

Data ingestion, validation, preprocessing, and feature engineering were separated into distinct responsibilities rather than being implemented as one monolithic transformation process.

---

## Modular Architecture and Software Engineering

As implementation progressed, software engineering became a central part of the ML platform.

The project adopted:

* separation of concerns
* modular architecture
* Single Responsibility Principle where appropriate
* object-oriented design where it provided value
* type hints
* logging
* exception handling
* automated testing
* static type checking
* code formatting and linting
* pre-commit validation

This established the principle that ML data pipelines should be treated as software systems rather than collections of exploratory scripts.

---

## Evolution of Data Quality Handling

Data validation became an explicit stage of the pipeline rather than an informal part of preprocessing.

The project introduced dedicated validation logic and established the separation:

```text
Data Validation
        ↓
Data Preprocessing
        ↓
Feature Engineering
```

This separation made it possible to distinguish:

* whether source data is acceptable,
* how missing or problematic data should be handled,
* and how ML features should subsequently be generated.

The project also established that unusual statistical observations should not automatically be treated as errors.

This principle became increasingly important for the more formal data-quality architecture developed in Phase 02.

---

## Raw Data and Reproducibility

The project established a reproducible workflow in which raw data remained identifiable as the source input while downstream processing generated derived datasets.

Dataset versioning utilities were introduced so that processed and feature datasets could be associated with identifiable versions.

This established a foundation for later dataset lineage and reproducibility requirements.

The principle evolved into:

```text
Immutable Source
      ↓
Reproducible Processing
      ↓
Versioned Dataset
      ↓
Versioned Features
```

---

## Feature Engineering Platform

Feature engineering was separated into domain-oriented modules:

```text
features/
├── customer_features.py
├── financial_features.py
└── loan_features.py
```

This introduced a domain-oriented organization of feature logic rather than maintaining one large feature-generation implementation.

An automated feature-generation workflow was also implemented.

The result was a reusable feature engineering layer that could later be integrated into a larger cloud-based ML lifecycle.

---

## Testing and Automated Quality

Testing evolved from validating individual pieces of functionality into a consistent engineering validation process.

The project established:

```text
Implementation
    ↓
Ruff
    ↓
Ruff Format
    ↓
MyPy
    ↓
Pytest
    ↓
Pre-Commit
```

Unit tests were implemented across data, feature, and utility components.

This established automated quality gates as part of normal development rather than as a final verification step.

---

## Documentation-Driven Architecture

The project progressively formalized its architecture through documentation.

This included:

* architecture documentation
* data engineering diagrams
* feature engineering diagrams
* Architecture Decision Records
* engineering notes
* interview preparation
* engineering retrospective

The use of ADRs established a mechanism for preserving significant architectural decisions and their trade-offs.

This documentation practice became particularly important as the architecture became more complex in Phase 02.

---

## Evolution Toward Cloud Integration

By the end of Phase 01, the local platform had become sufficiently structured to serve as the foundation for cloud integration.

The project therefore moved from:

```text
Local ML Engineering Platform
```

toward:

```text
Local Engineering Foundation
            ↓
AWS Data Platform
            ↓
AWS MLOps Platform
```

The important architectural principle was that the local implementation should provide reusable engineering logic rather than being discarded when AWS services were introduced.

This led to the Phase 02 strategy of developing reusable processing logic locally while executing appropriate workloads through AWS-managed services.

---

## Transition From a Monolithic Dataset Toward Domain-Oriented Data

The next major architectural evolution was identified at the end of Phase 01.

The original Credit Risk dataset was a single monolithic source containing attributes belonging to different business domains.

Phase 02 would therefore introduce a domain-oriented representation:

```text
Monolithic Credit Risk Dataset
            ↓
     Business Domains
            ↓
┌───────────┼────────────┐
│           │            │
Customer   Financial    Loan
Profile    History      Application
```

The purpose was not to claim that the source system actually provides these exact three datasets.

Instead, the decomposition would simulate realistic business-domain datasets and create a foundation for learning cloud data-platform architecture.

---

## Resulting Phase 01 Architecture

By the end of Phase 01, the project had evolved into a complete local-first data engineering and feature engineering platform:

```text
Raw Data
    ↓
Data Ingestion
    ↓
Data Validation
    ↓
Data Preprocessing
    ↓
Processed Dataset
    ↓
Feature Engineering
    ↓
Feature Dataset
```

The platform was modular, reproducible, tested, documented, and ready to evolve into an enterprise AWS MLOps architecture.

---

## Transition Into Phase 02

The limitations of a local-only data platform became the motivation for the next phase.

Phase 02 therefore expanded the architecture from local data processing toward an AWS-native ML data foundation.

The planned direction became:

```text
Local Engineering Foundation
            ↓
Amazon S3
            ↓
AWS Glue
            ↓
Glue Data Catalog
            ↓
Amazon Athena
            ↓
Curated ML Data
            ↓
SageMaker
```

The objective was no longer simply to process a dataset locally.

The objective became to understand how data can be:

* stored in a cloud data lake,
* processed through managed data services,
* cataloged through metadata,
* explored and validated through SQL,
* integrated into curated ML datasets,
* versioned and traced,
* and ultimately consumed by downstream ML training and inference systems.

This transition established the starting point for Phase 02.

---

## Key Evolution Principles

The most important principles established during Phase 01 were:

* Treat ML data pipelines as software systems.
* Separate ingestion, validation, preprocessing, and feature engineering.
* Keep responsibilities modular and independently testable.
* Preserve reproducibility throughout the data workflow.
* Introduce dataset versioning and traceability early.
* Use automated quality checks as part of normal development.
* Apply software engineering principles where they provide real value.
* Maintain a consistent business use case across the MLOps roadmap.
* Build a local engineering foundation that can evolve into cloud architecture.
* Move from a monolithic dataset toward domain-oriented data architecture.
* Treat cloud integration as an evolution of the existing engineering platform rather than a replacement for it.
