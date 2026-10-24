# MLOps Engineering Roadmap

## Overview

This repository documents the progressive design and implementation of an enterprise-oriented Machine Learning Operations (MLOps) platform.

The project follows a local-first engineering approach that combines software engineering, data engineering, cloud infrastructure, automation, and MLOps principles to build a reproducible foundation for production-oriented machine learning systems.

The reference use case is a Credit Risk / Loan Approval Prediction platform. The objective is to demonstrate sound engineering practices throughout the machine learning lifecycle rather than to build a large-scale data processing system.

## Platform Vision

The long-term objective is to develop a modular ML platform supporting:

- Data ingestion and data quality.
- Data transformation and feature engineering.
- Dataset versioning and reproducibility.
- Cloud data infrastructure.
- Model training and experiment tracking.
- Model evaluation and management.
- Model deployment and inference.
- CI/CD and infrastructure automation.
- Monitoring, security, governance, and operational excellence.

Each roadmap phase introduces capabilities incrementally, with explicit validation and documentation.

## Engineering Principles

### Local-First Development

Development, testing, data validation, and most experimentation are performed locally whenever practical. Cloud resources are introduced when required to validate integrations, managed services, and production-like workflows.

### Infrastructure as Code

Terraform manages the lifecycle of supported cloud infrastructure. Infrastructure definitions are version-controlled and validated before deployment.

Cloud resources are treated as temporary when appropriate: provision, verify, document, and destroy.

### Reproducibility and Data Quality

Data processing follows explicit validation rules, metadata practices, and reproducibility conventions. Data quality is treated as an engineering requirement rather than an implicit assumption.

### Documentation-Driven Engineering

Architecture decisions, technical concepts, implementation details, validation results, and phase retrospectives document the reasoning behind engineering choices.

### Security and Resource Management

Cloud experiments follow appropriate security practices and resource lifecycle procedures. Infrastructure configuration and cleanup are treated as part of the engineering workflow.

## Current Status

| Phase | Name | Status |
|---|---|---|
| Phase 00 | Foundations and Cloud Fundamentals | Complete |
| Phase 01 | Data Engineering and Feature Platform | Complete |
| Phase 02 | AWS Data Foundation | Complete |

### Phase 00 — Foundations and Cloud Fundamentals

**Status: Complete**

Completed activities:

- Local development environment preparation.
- Repository structure creation and version control.
- AWS account and IAM configuration.
- AWS CLI authentication.
- Terraform installation and configuration.
- Terraform AWS provider setup.
- Amazon S3 infrastructure lifecycle exercises.
- Enterprise ML platform architecture foundations.
- Engineering quality tooling and pre-commit configuration.
- Technical documentation and interview preparation materials.
- Phase retrospective.

**Outcome:** Established the engineering environment, repository workflow, cloud access, infrastructure tooling, and documentation practices required for subsequent phases.

### Phase 01 — Data Engineering and Feature Platform

**Status: Complete**

Phase 01 established the data engineering and feature preparation foundation for the reference loan-risk use case.

Key activities included:

- Data ingestion and processing workflow development.
- Separation of customer, financial history, and loan application domains.
- Data validation and quality checks.
- Preprocessing and feature engineering.
- Organization of datasets and supporting metadata.
- Reproducibility and dataset management practices.
- Preparation of the data foundation for subsequent cloud integration.

**Outcome:** Established the data and feature preparation foundation used to support the AWS data engineering work in Phase 02.

### Phase 02 — AWS Data Foundation

**Status: Complete**

Phase 02 extended the data engineering foundation into AWS-managed data services. The work focused on publishing and cataloging a curated loan-risk dataset, validating its structure and relationships, documenting evidence, and managing the infrastructure lifecycle.

#### Amazon S3 — Data Lake and Storage

- Implemented the AWS S3 data lake foundation.
- Configured S3 Block Public Access.
- Configured default encryption.
- Published the curated dataset to S3.
- Documented the curated dataset publication and version `1.0.1`.
- Captured metadata and SHA-256 evidence for the curated dataset.

#### AWS Glue — Catalog and ETL

- Configured the Glue Data Catalog for the business-domain tables.
- Implemented the Glue crawler workflow and documented successful runs.
- Executed the Glue ETL workflow and captured evidence of a successful run.
- Cataloged the curated dataset alongside the business tables.

#### Amazon Athena — Analytical Validation

- Validated row counts for the business tables.
- Validated the curated dataset row count.
- Executed a JOIN-cardinality validation to check relationships between business datasets.

#### Terraform — Infrastructure Lifecycle

- Managed the relevant AWS infrastructure using Terraform.
- Validated Terraform formatting and configuration.
- Documented the infrastructure implementation and cleanup.
- Destroyed the temporary Phase 02 infrastructure and verified the removal of the principal project resources.
- Added `force_destroy = true` to the Athena workgroup resource to support workgroup cleanup when saved queries exist.

The `force_destroy` setting does not delete query-result objects stored separately in S3. Storage resources therefore require their own lifecycle management.

#### Evidence and Version Control

The repository includes a dedicated `phase-02-evidence/` directory containing 11 selected screenshots documenting:

- S3 security settings.
- Curated dataset publication and metadata.
- Glue catalog configuration and successful execution.
- Athena row-count and JOIN-cardinality validations.

The Phase 02 evidence and Terraform configuration change were committed and pushed to `main`.

**Outcome:** The AWS data foundation was implemented and validated, its key results were documented, and the temporary project infrastructure was destroyed.

## Technology Stack

### Development and Version Control

- Python
- Conda
- uv
- VS Code
- Git
- GitHub

### Software Engineering and Quality

- Ruff
- MyPy
- Pytest
- Pre-commit

### Cloud and Infrastructure

- Amazon Web Services (AWS)
- AWS IAM
- AWS CLI
- Amazon S3
- AWS Glue
- AWS Glue Data Catalog
- Amazon Athena
- Terraform

### Technologies for Future Phases

The broader roadmap may introduce:

- Docker
- Kubernetes
- MLflow
- DVC
- FastAPI
- Amazon SageMaker
- CI/CD systems
- Model and data monitoring tools

These technologies are part of the future roadmap and should not be interpreted as already implemented in the completed phases.

## Repository Organization

The repository contains infrastructure definitions, project code, tests, documentation, and phase-specific evidence.

```text
mlops-engineering-roadmap/
├── infrastructure/
│   └── terraform/
├── phase-02-evidence/
├── src/
├── tests/
├── README.md
└── pyproject.toml
```

This is a high-level overview of the principal project areas. Additional documentation and supporting files are maintained in the repository as the roadmap evolves.

## Data Platform Architecture

The AWS data foundation separates source preservation, standardized business data, and curated analytical data.

```text
Source Data
    |
    v
Amazon S3 — Raw
    |
    v
AWS Glue — Standardization
    |
    v
Amazon S3 — Standardized
    |
    v
AWS Glue — Curated Transformation
    |
    v
Amazon S3 — Curated
    |
    v
Glue Data Catalog
    |
    v
Amazon Athena — Analytical Validation
    |
    v
Downstream ML Data Preparation
    |
    v
Model Training and Evaluation
```

The Raw layer preserves source data. The Standardized layer organizes business-domain data, including customer, financial history, and loan application information. The Curated layer integrates the relevant domains into a dataset suitable for downstream analytical and ML preparation.

The Glue Data Catalog provides metadata discovery, while Athena enables SQL-based validation.

The architecture describes the intended data flow. It does not imply that every downstream capability, such as model training, deployment, or monitoring, has already been implemented.

Security, infrastructure automation, data quality, and metadata practices support the platform across its layers.

## Reference ML Use Case

The project uses a Credit Risk / Loan Approval Prediction scenario to connect data engineering activities with future ML workflows.

The intended lifecycle includes:

1. Source data ingestion.
2. Domain-level standardization and validation.
3. Curated dataset construction.
4. Feature engineering and ML-specific preprocessing.
5. Model training and evaluation.
6. Model management and deployment.
7. Monitoring and continuous improvement.

Each capability is introduced and validated in its corresponding roadmap phase.

## Resource Lifecycle Management

The project follows a controlled cloud resource lifecycle:

- Prefer local development when cloud services are unnecessary.
- Use small, controlled datasets and temporary resources.
- Validate infrastructure before relying on it.
- Capture evidence while resources are available.
- Destroy temporary infrastructure after experiments.
- Verify resource removal after destruction.
- Keep infrastructure definitions and implementation evidence under version control.

The Phase 02 cleanup included verification of the principal resources used by the project, including S3, AWS Glue, Athena, and the relevant Glue-related CloudWatch log groups.

An empty Terraform state or an empty service resource list does not independently prove that every resource in an AWS account has been removed. Resource verification should remain scoped to the services and resources used by each phase.

## Roadmap

### Phase 00 — Foundations and Cloud Fundamentals

**Status: Complete**

Established the local engineering environment, repository workflow, initial AWS configuration, Terraform foundations, and engineering documentation practices.

### Phase 01 — Data Engineering and Feature Platform

**Status: Complete**

Established the data processing, domain separation, validation, feature preparation, and reproducibility foundation for the reference ML use case.

### Phase 02 — AWS Data Foundation

**Status: Complete**

Integrated the data foundation with Amazon S3, AWS Glue, the Glue Data Catalog, Amazon Athena, and Terraform. Documented successful executions and analytical validations, captured evidence, and completed the temporary infrastructure lifecycle.

### Future Phases

The next roadmap stages will progressively extend the platform toward:

- ML-specific processing and training-data quality gates.
- Model training and experiment tracking.
- Model evaluation and model management.
- Inference and deployment services.
- CI/CD automation.
- Containers and Kubernetes where justified.
- Monitoring, operational excellence, and governance.

The detailed scope and completion criteria for future phases will be maintained in the corresponding roadmap documentation.

## Learning Objective

This repository represents a progressive engineering journey toward building production-oriented machine learning systems.

The emphasis is on reproducibility, maintainable software, data quality, infrastructure automation, security, evidence-based validation, and responsible cloud resource management throughout the ML lifecycle.