# Processing Layer

## 1. Purpose

The Processing Layer transforms data from the Data Lake into standardized, curated, and training-ready datasets.

Its primary responsibility is to apply controlled data transformations while maintaining:

* Reproducibility
* Data quality
* Dataset lineage
* Versioning
* Separation of responsibilities
* Training and inference consistency

The Processing Layer is divided into two main responsibilities:

```text
Data Engineering
        │
        ▼
     AWS Glue
        │
        ▼
Standardized / Curated Data
        │
        ▼
ML-Specific Processing
        │
        ▼
SageMaker Processing
        │
        ▼
Training-Ready Data
```

This separation prevents data engineering transformations from becoming tightly coupled to machine-learning training workflows.

---

## 2. Processing Layer Position

The Processing Layer sits between the S3 Data Lake and the ML Training Layer.

```text
Data Sources
      │
      ▼
Amazon S3 Data Lake
      │
      ▼
AWS Glue
      │
      ├── Standardization
      ├── Domain Processing
      └── Data Integration
      │
      ▼
Curated Dataset
      │
      ▼
Dataset Validation
      │
      ▼
SageMaker Processing
      │
      ├── ML Preprocessing
      ├── Feature Preparation
      └── Training Dataset Preparation
      │
      ▼
Training-Ready Dataset
      │
      ▼
SageMaker Training
```

The Processing Layer therefore provides the controlled transition from source-oriented data to ML-ready data.

---

## 3. Processing Responsibilities

The Processing Layer is responsible for transformations required before model training.

These responsibilities are divided between AWS Glue and SageMaker Processing.

### AWS Glue

AWS Glue is responsible primarily for data engineering activities:

* Schema standardization
* Data-type normalization
* Structural transformations
* Domain-level processing
* Domain dataset preparation
* Cross-domain integration
* Large-scale data transformations
* Data Catalog integration

### SageMaker Processing

SageMaker Processing is responsible primarily for ML-specific preparation:

* Missing-value strategies
* Categorical encoding
* Numerical transformations
* Feature preparation
* Train/validation/test dataset preparation
* ML-specific validation
* Training/inference preprocessing consistency
* Export of training-ready datasets

Model training itself is outside the Processing Layer.

---

## 4. AWS Glue Processing

AWS Glue represents the data engineering portion of the Processing Layer.

Its role is to transform source-oriented data into standardized and curated datasets.

The conceptual flow is:

```text
RAW
 │
 ▼
AWS Glue
 │
 ├── Standardization
 ├── Domain Processing
 └── Cross-Domain Integration
 │
 ▼
STANDARDIZED
 │
 ▼
CURATED
```

Typical transformations include:

* Schema normalization
* Data-type normalization
* Column standardization
* Structural cleaning
* Domain decomposition
* Domain-level transformations
* Cross-domain joins
* Dataset integration

These transformations should remain independent of any specific ML model.

---

## 5. SageMaker Processing

SageMaker Processing represents the ML-specific portion of the Processing Layer.

It consumes validated curated data and prepares datasets for model training.

The conceptual flow is:

```text
CURATED DATASET
       │
       ▼
Dataset Validation
       │
       ▼
SageMaker Processing
       │
       ├── Missing-Value Strategy
       ├── Encoding
       ├── Numerical Transformations
       ├── Feature Preparation
       └── Dataset Splitting
       │
       ▼
TRAINING-READY DATASET
```

SageMaker Processing should therefore not be treated as the general-purpose data engineering layer.

Its responsibility begins when the data has reached the ML-specific processing boundary.

---

## 6. Processing Workflow

The target Phase 2 processing workflow is:

```text
Source Data
    │
    ▼
Raw Data
    │
    ▼
Source / Ingestion Validation
    │
    ▼
AWS Glue
    │
    ▼
Standardized Domain Data
    │
    ▼
Cross-Domain Integration
    │
    ▼
Curated Dataset
    │
    ▼
Curated Dataset Validation
    │
    ▼
SageMaker Processing
    │
    ▼
Training-Ready Dataset
    │
    ▼
SageMaker Training
```

Each stage produces a controlled output rather than modifying an existing production dataset in place.

---

## 7. Input Data

The Processing Layer consumes datasets stored in Amazon S3.

Depending on the processing stage, inputs may include:

* Raw source datasets
* Standardized domain datasets
* Curated datasets
* Dataset metadata
* Validation results
* Processing configuration
* Dataset version information

For example:

```text
AWS Glue

Input:
    Raw Dataset

Output:
    Standardized Dataset
```

and:

```text
SageMaker Processing

Input:
    Curated Dataset

Output:
    Training-Ready Dataset
```

---

## 8. Output Data

Processing outputs are stored as new dataset artifacts.

Examples include:

* Standardized datasets
* Curated datasets
* Training-ready datasets
* Validation reports
* Processing metadata
* Lineage metadata

Controlled datasets should not be overwritten.

Instead:

```text
Input Dataset Version
        │
        ▼
Processing
        │
        ▼
New Dataset Version
```

This supports reproducibility and historical traceability.

---

## 9. Validation Boundaries

Validation occurs at multiple points in the processing lifecycle.

### 9.1 Source / Ingestion Validation

The first validation layer checks whether incoming data is structurally usable.

Examples include:

* Schema validation
* Required columns
* Data types
* Malformed records
* Duplicate identifiers
* Basic data-quality rules

```text
Raw Dataset
      │
      ▼
Source / Ingestion Validation
```

This validation does not perform ML-specific preprocessing.

---

### 9.2 Curated Dataset Validation

After domain processing and integration, the resulting curated dataset is validated before entering ML preprocessing.

Examples include:

* Cross-domain consistency
* Business rules
* Required relationships
* Data completeness
* Target-variable validity
* Curated dataset quality

```text
Curated Dataset
      │
      ▼
Curated Dataset Validation
```

The validation result acts as a quality gate:

```text
Validation
    │
 ┌──┴──┐
 ▼     ▼
PASS  FAIL
 │     │
 ▼     ▼
Continue   Reject /
           Quarantine /
           Investigate
```

Validation does not imply automatic correction.

---

## 10. ML Preprocessing Boundary

ML-specific preprocessing begins after the curated dataset has passed the appropriate validation gates.

Typical operations include:

* Missing-value treatment
* Categorical encoding
* Numerical transformations
* Scaling
* Feature preparation
* Train/validation/test splitting
* ML-specific transformations

The boundary is therefore:

```text
CURATED DATASET
       │
       ▼
CURATED VALIDATION
       │
       ▼
ML PREPROCESSING
       │
       ▼
TRAINING-READY DATA
```

This separation is important because data engineering and ML preprocessing have different responsibilities.

---

## 11. Reproducibility

Processing must be reproducible.

A processing result should be determined by controlled inputs and configuration.

Conceptually:

```text
Input Dataset Version
        +
Processing Code Version
        +
Processing Configuration
        │
        ▼
Processed Dataset Version
```

Processing metadata should capture information such as:

* Input dataset version
* Output dataset version
* Processing code version
* Configuration version
* Execution timestamp
* Processing environment
* Validation results

This allows previous processing results to be reconstructed.

---

## 12. Dataset Lineage

The Processing Layer contributes to end-to-end dataset lineage.

A simplified lineage example is:

```text
Source Data
    │
    ▼
Raw Dataset
    │
    ▼
AWS Glue
    │
    ▼
Standardized Domain Data
    │
    ▼
Curated Dataset
    │
    ▼
SageMaker Processing
    │
    ▼
Training-Ready Dataset
    │
    ▼
SageMaker Training
    │
    ▼
Model
```

Lineage should make it possible to determine:

* Where the data originated
* Which transformations were applied
* Which dataset version was produced
* Which processing code was used
* Which model ultimately consumed the data

---

## 13. Local-First Development

Processing logic should be developed and validated locally before being executed in AWS.

The preferred workflow is:

```text
Develop Processing Logic
          │
          ▼
Validate Locally
          │
          ▼
Run Tests
          │
          ▼
Provision AWS
          │
          ▼
Execute AWS Processing
          │
          ▼
Validate AWS Output
```

This approach reduces:

* AWS costs
* Debugging time
* Iteration time
* Dependence on cloud infrastructure during development

It also allows the same processing logic to be validated before cloud execution.

---

## 14. Ephemeral AWS Execution

AWS infrastructure is considered ephemeral by default within this roadmap.

The local project remains the primary reconstruction source.

The operating model is:

```text
Local Project
      │
      ▼
Terraform
      │
      ▼
Create AWS Resources
      │
      ▼
Execute / Verify
      │
      ▼
Console Inspection
      │
      ▼
Document Evidence
      │
      ▼
Destroy AWS Resources
      │
      ▼
Recreate Later
```

Destroying the AWS environment does not destroy the architecture.

The local project retains:

* Terraform configuration
* Processing code
* Tests
* Configuration
* SQL
* Documentation
* Infrastructure definitions

These components allow the AWS environment to be reconstructed when required.

---

## 15. Dataset Versioning

Processing outputs should be treated as immutable dataset artifacts.

For example:

```text
Curated Dataset v1
        │
        ▼
Processing Pipeline v1
        │
        ▼
Training-Ready Dataset v1
```

If processing logic changes:

```text
Curated Dataset v1
        │
        ▼
Processing Pipeline v2
        │
        ▼
Training-Ready Dataset v2
```

The previous dataset remains unchanged.

This allows engineers to determine which processing logic produced a particular training dataset.

---

## 16. Separation from Training

The Processing Layer prepares data but does not train models.

The architectural boundary is:

```text
Processing Layer
      │
      ▼
Training-Ready Dataset
      │
      │
      ▼
Training Layer
      │
      ▼
SageMaker Training Job
      │
      ▼
Model Artifact
```

This separation allows processing and training to evolve independently.

For example:

* Processing code can change without changing the training algorithm.
* Training configuration can change without modifying the source data.
* Different models can consume the same validated training-ready dataset.

---

## 17. Design Principles

The Processing Layer follows these principles:

### Separation of Responsibilities

Data engineering and ML preprocessing are separate concerns.

```text
AWS Glue
    │
    ▼
Data Engineering
```

```text
SageMaker Processing
    │
    ▼
ML Preprocessing
```

### Reproducibility

Processing must be reproducible from controlled inputs, code, and configuration.

### Immutability

Existing controlled dataset versions should not be overwritten.

### Traceability

Every processed dataset should have identifiable inputs and processing history.

### Local-First Development

Processing logic should be validated locally before cloud execution.

### Ephemeral Infrastructure

AWS compute and supporting infrastructure should be created only when required and destroyed after validation when persistence is unnecessary.

### Separation from Training

Data preparation should remain independent from model training.

---

## 18. Architectural Summary

The Phase 2 Processing Layer can be summarized as:

```text
                         S3 DATA LAKE
                              │
                              ▼
                             RAW
                              │
                              ▼
                         AWS GLUE
                              │
                  ┌───────────┴───────────┐
                  │                       │
           Standardization          Domain Processing
                  │                       │
                  └───────────┬───────────┘
                              ▼
                         STANDARDIZED
                              │
                              ▼
                    Cross-Domain Integration
                              │
                              ▼
                           CURATED
                              │
                              ▼
                    Curated Validation
                              │
                              ▼
                    SAGEMAKER PROCESSING
                              │
                  ┌───────────┴───────────┐
                  │                       │
             ML Preprocessing      Feature Preparation
                  │                       │
                  └───────────┬───────────┘
                              ▼
                     TRAINING-READY
                              │
                              ▼
                    SAGEMAKER TRAINING
```

The key architectural boundary is:

> **AWS Glue prepares and integrates data as part of the data engineering layer. SageMaker Processing prepares validated curated data for machine learning.**

This separation keeps the Phase 2 data foundation modular, reproducible, and independent from model training.

---

## 19. Interview Preparation

### Why would you use AWS Glue instead of SageMaker Processing?

AWS Glue is primarily a data engineering service designed for data integration, transformation, cataloging, and large-scale data preparation.

SageMaker Processing is designed for machine-learning-specific processing and preparation of datasets for ML workflows.

The choice therefore depends on the responsibility of the transformation.

---

### Where does ML preprocessing happen?

ML-specific preprocessing happens after the curated dataset has passed the required validation gates.

In this architecture, SageMaker Processing is responsible for producing the training-ready dataset.

---

### Why separate Glue from SageMaker Processing?

The separation prevents general data engineering logic from becoming tightly coupled to ML workflows.

It also allows:

* Independent evolution
* Reusability
* Clear ownership
* Better testing
* Better lineage
* Easier operational reasoning

---

### Why should processing outputs be immutable?

Immutable outputs allow previous datasets to remain reproducible.

If processing logic changes, a new dataset version is created rather than modifying the previous artifact.

---

### How would you reproduce a previous processing result?

I would recover:

* Input dataset version
* Processing code version
* Processing configuration
* Processing environment
* Validation results

Then execute the same processing logic against the same input version.

---

## 20. Key Takeaways

* AWS Glue is responsible primarily for data engineering transformations.
* SageMaker Processing is responsible primarily for ML-specific preprocessing.
* Raw, Standardized, and Curated represent logical data states in the S3 Data Lake.
* Training-Ready data is produced downstream of the curated dataset.
* Validation acts as a quality gate between processing stages.
* Processing outputs should be treated as immutable artifacts.
* Processing must maintain dataset lineage.
* Processing logic should be validated locally before AWS execution.
* AWS infrastructure is ephemeral by default in this roadmap.
* The local project is the primary reconstruction source.
* Processing remains separate from model training.
* Dataset versioning, lineage, and reproducibility are core Processing Layer concerns.
