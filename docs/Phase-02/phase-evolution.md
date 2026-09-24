# Phase 02 — Evolution

## Purpose

This document records the significant architectural and engineering changes that have shaped Phase 02 of the MLOps Engineer / AWS Roadmap.

It is maintained incrementally at important milestones to preserve the evolution of the project without turning the document into a detailed implementation log.

---

## Initial Direction

Phase 02 initially focused on extending the local-first ML engineering platform from Phase 01 into an AWS-oriented ML data foundation.

The initial objective was to establish a data platform capable of supporting:

* cloud-based data storage
* data processing
* data validation
* dataset versioning
* lineage and provenance
* reproducible ML datasets
* future model training and inference

The initial high-level direction was:

```text
Data Sources
    ↓
S3 Data Lake
    ↓
Glue Data Catalog
    ↓
Athena
    ↓
SageMaker Processing
    ↓
Training-Ready Dataset
```

During implementation, this architecture was refined substantially.

---

## Evolution Toward Business-Domain Data

The original Credit Risk dataset was a single monolithic dataset.

Rather than immediately treating this dataset as a final ML dataset, Phase 02 introduced a business-domain representation to simulate a more realistic enterprise data environment.

The monolithic dataset was decomposed into three technical business domains:

```text
Monolithic Credit Risk Dataset
            ↓
     Domain Decomposition
            ↓
┌───────────┼────────────┐
│           │            │
Customer   Financial    Loan
Profile    History      Application
```

The purpose of this decomposition was twofold:

1. Simulate separate datasets that could realistically originate from different business domains or source systems.
2. Create a realistic structure for learning AWS data-platform services such as S3, Glue, Glue Data Catalog, and Athena.

The decomposition does not claim that the original source system actually provides these three independent datasets.

---

## Synthetic Technical Identifiers

The source dataset did not contain native customer or application identifiers.

To model relationships between the business domains, technical identifiers were introduced during domain decomposition:

* `customer_id`
* `application_id`

These identifiers are synthetic and exist for architectural purposes.

The current dataset represents one technical customer and one technical loan application per source record.

Therefore, the current one-to-one relationships should not be interpreted as real customer reuse, customer history, or multiple applications belonging to the same real customer.

This distinction was made explicit to prevent the architecture exercise from implying business information that does not exist in the source data.

---

## Domain-Level EDA Added to the Architecture

After domain decomposition, the project introduced a dedicated domain-level EDA stage.

The objective was to understand each business-domain dataset independently before implementing further data-platform processing.

The workflow was standardized as:

```text
For each domain:

1. Schema
2. Missing Values
3. Duplicates / Identifiers
4. Numerical Analysis
5. Categorical Analysis
6. Anomaly Investigation
7. Findings
8. Conclusion
```

This replaced an open-ended exploratory workflow with a finite, repeatable process.

The three domains were analyzed independently, followed by a limited cross-domain analysis.

---

## Customer Profile Findings

Customer Profile EDA identified:

* unique technical customer identifiers
* no duplicate rows
* missing `employment_length`
* a strong concentration of customers between approximately 20 and 30 years of age
* extreme age observations, including five values above 100
* extreme income values requiring domain validation rather than automatic removal
* two observations with `employment_length = 123` associated with customers aged 21 and 22

The relationship between age and employment length revealed impossible implied starting ages for the two records with an employment length of 123 years.

This reinforced the principle that business-domain relationships can be more informative than arbitrary numerical thresholds.

No records were modified or removed during EDA.

---

## Financial History Findings

Financial History EDA identified a structurally consistent domain:

* 32,581 observations
* unique technical customer identifiers
* no duplicate rows
* no missing values
* `credit_history_length` ranging from 2 to 30 years
* expected `default_history` categories
* no clear anomalies requiring additional investigation

The minimum and maximum credit-history values were observed across multiple records and did not, by themselves, indicate data-quality problems.

No corrective cleaning was performed during EDA.

---

## Loan Application Findings

Loan Application EDA identified:

* unique `application_id` values
* unique `customer_id` values within the current technical dataset
* no duplicate rows
* 3,116 missing `loan_interest_rate` values (9.56%)
* expected loan-purpose categories
* expected risk grades from A through G
* a binary and imbalanced `loan_outcome` target
* no obvious invalid numerical boundary values

Rare risk grades `F` and `G` were investigated and did not reveal an obvious data-quality problem.

A cross-domain consistency investigation also identified 388 observations where `loan_income_ratio` differs from the simple `loan_amount / income` calculation by more than 0.01.

The source value was preserved because the authoritative definition of `loan_income_ratio` is not currently known.

This established an important rule:

> A discrepancy with an independently calculated value should not automatically result in overwriting the source value.

---

## EDA vs. Cleaning Clarification

An important architectural distinction was established during Phase 02:

> **EDA is not the same as data cleaning.**

EDA is used to:

* understand the data
* identify potential quality problems
* investigate anomalies
* establish evidence for future validation rules
* document findings

EDA does not automatically:

* remove outliers
* correct values
* impute missing values
* overwrite source attributes

This distinction became particularly important for extreme ages, extreme incomes, missing interest rates, and the `loan_income_ratio` discrepancy.

---

## Evolution of the Data-Quality Architecture

Phase 02 initially appeared to suggest that EDA findings would immediately become domain validation and cleaning rules.

During implementation, this was refined.

EDA findings are now treated as **candidates for later validation rules**, rather than automatic cleaning instructions.

The refined concept is:

```text
EDA Finding
    ↓
Potential Quality / Business Rule
    ↓
Determine Authoritative Definition
    ↓
Implement Validation Rule
    ↓
Define Appropriate Action
```

The action following a validation failure may depend on the nature of the problem:

```text
Validation Failure
        ↓
┌───────┼────────┬────────────┐
│       │        │            │
Reject  Quarantine Correct   Investigate
```

The appropriate action will be determined when the validation and processing architecture is implemented.

---

## Separation of Source-Level Quality and ML Preprocessing

A major architectural clarification occurred after completing the domain EDA.

The project distinguished between two different transformation concerns.

### Source / Ingestion Layer

The first stage is concerned with making incoming data structurally valid and usable by the data platform.

Typical responsibilities include:

* schema validation
* required-column validation
* type validation
* malformed-record handling
* structural data-quality checks
* duplicate handling where justified
* basic standardization

### ML Preprocessing Layer

A later stage is concerned specifically with producing data suitable for machine learning.

Typical responsibilities may include:

* missing-value treatment
* categorical encoding
* numerical transformations
* feature preparation
* training/validation/test-safe transformations
* training/inference consistency

These responsibilities should not be collapsed into one generic cleaning stage.

---

## AWS Service Responsibilities Clarified

The responsibilities of the AWS services were also refined.

### Amazon S3

S3 provides the persistent storage layer and data lake foundation.

### AWS Glue

Glue provides managed data processing and ETL capabilities.

### Glue Data Catalog

The Glue Data Catalog provides metadata and schema information for datasets stored in the data lake.

### Amazon Athena

Athena provides serverless SQL-based exploration, profiling, querying, and validation over data stored in S3.

Athena is therefore not considered the primary data-cleaning or ETL engine.

### SageMaker Processing

SageMaker Processing will provide a managed execution environment for repeatable ML-oriented preprocessing workloads where appropriate.

---

## Revised Phase 02 Data Lifecycle

The Phase 02 architecture was therefore refined into the following lifecycle:

```text
                    SOURCE DATA
                        │
                        ▼
              Source / Ingestion Layer
                        │
                ┌───────┴────────┐
                │ Validation     │
                │ Basic cleaning │
                └───────┬────────┘
                        │
                        ▼
              Standardized / Curated
                   Domain Data
                        │
                        ▼
                 Domain-Level EDA
                        │
                        ▼
              Domain Validation
                        │
                        ▼
              Curated ML Dataset
                        │
                        ▼
              ML Dataset EDA
                        │
                        ▼
          ML Preprocessing / Features
                        │
                        ▼
              Training-Ready Dataset
```

This lifecycle is the current architectural direction and may be refined further as Phase 02 implementation progresses.

---

## Phase 02 Current Roadmap

At the current milestone, the Phase 02 implementation has progressed through:

```text
1. Domain Design
       ✓ Complete

2. Domain Decomposition
       ✓ Complete

3. Domain-Level EDA
       ✓ Complete

4. AWS Data Foundation
       │
       ├── Amazon S3
       ├── AWS Glue
       ├── Glue Data Catalog
       └── Amazon Athena

5. Source / Ingestion Validation
       │
       └── Structural and basic data-quality controls

6. Domain Processing / Standardization
       │
       └── AWS Glue

7. Cross-Domain Integration
       │
       └── Curated ML Dataset

8. Curated Dataset Validation
       │
       └── Business, consistency, and quality rules

9. ML Dataset EDA
       │
       └── Analysis of the integrated curated dataset

10. ML Preprocessing
       │
       ├── Missing-value strategy
       ├── Encoding
       ├── Transformations
       └── Training / inference consistency

11. Training-Ready Dataset
       │
       └── Versioning and metadata

12. Dataset Versioning / Lineage
       │
       └── Reproducibility
```

Only the first three stages are currently complete.

The remaining stages will be implemented progressively and validated through the project's normal engineering workflow.

---

## Current Implementation Strategy

The project adopted a **local-first, cloud-validation-second** strategy.

Reusable transformation logic will be developed using Python and PySpark where appropriate and should remain as independent from AWS-specific execution details as practical.

The intended execution model is:

```text
Reusable Transformation Logic
             ↓
      Python / PySpark
             ↓
      ┌──────┴──────┐
      ↓             ↓
Local Execution   AWS Glue Execution
```

AWS services are introduced when they provide meaningful architectural or learning value rather than simply duplicating local operations.

Terraform will be used for infrastructure provisioning where appropriate, AWS SDK / `boto3` for programmatic interaction, and the AWS Console for visual inspection and resource verification.

---

## Current Phase 02 Status

At this milestone:

* Domain design is complete.
* Domain decomposition is implemented and tested.
* Three domain datasets are generated locally.
* Domain-level EDA is complete.
* Cross-domain relationship integrity has been verified.
* The distinction between EDA, source-level data quality, and ML preprocessing has been clarified.
* The responsibilities of S3, Glue, Glue Data Catalog, Athena, and SageMaker Processing have been clarified.
* The Phase 02 implementation lifecycle has been refined accordingly.

The next milestone is the implementation of the **AWS data foundation**, beginning with the cloud data-lake architecture and its integration with the existing local engineering foundation.

## Evolution of the Production Data Validation Layer

During the evolution of Phase 02, an additional architectural component was identified as important for making the ML data foundation closer to a production-oriented machine learning system: a dedicated **data validation layer** between data curation and downstream ML processing.

The purpose of this component is not simply to clean data.

Its responsibility is to determine whether a dataset produced by the data platform is structurally, technically, and logically acceptable for the next stage of the ML lifecycle.

This distinction became important as the project evolved from exploratory data analysis toward a production-oriented data architecture.

---

## Validation Layer in the ML Architecture

The refined architecture now distinguishes between source-level validation and validation of the curated ML dataset.

```text
SOURCE DATA
    │
    ▼
Source / Ingestion
    │
    ├── Source validation
    └── Basic structural cleaning
    │
    ▼
Standardized Domain Data
    │
    ▼
Domain-Level EDA
    │
    ▼
Domain Processing / Standardization
    │
    └── AWS Glue
    │
    ▼
Cross-Domain Integration
    │
    ▼
CURATED ML DATASET
    │
    ▼
┌──────────────────────────────────┐
│      CURATED DATA VALIDATION     │
│                                  │
│  Schema validation               │
│  Data-type validation            │
│  Required-column validation      │
│  Identifier validation           │
│  Null / missing-value checks     │
│  Domain/business rules           │
│  Cross-column consistency        │
│  Dataset integrity checks        │
└──────────────────────────────────┘
    │
    ├── PASS ───────────────────┐
    │                           │
    └── FAIL → reject /         │
               quarantine /     │
               investigate      │
                                ▼
                         ML Dataset EDA
                                │
                                ▼
                       ML Preprocessing
                                │
                                ▼
                      Training-Ready Dataset
```

This validation layer is now considered part of the Phase 02 target architecture.

It will be designed and implemented when the curated ML dataset exists and there is sufficient context to define its validation contracts and rules.

---

## Schema Validation as a First-Class Component

One of the most important responsibilities identified for the validation layer is **schema validation**.

The validator should verify that the dataset conforms to an expected schema before it is consumed by downstream ML processes.

For example:

```text
customer_id          string       required
age                  integer      required
income               numeric      required
home_ownership       string       required
employment_length    numeric      optional
```

The validation component should be able to detect situations such as:

```text
Expected                         Actual

customer_id → string             customer_id → string       ✓
age         → integer             age         → string       ✗
income      → numeric             income      → numeric      ✓
home_ownership → string           home_ownership → string    ✓
employment_length → numeric      missing column             ✗
```

Schema validation should therefore verify more than whether a file can be loaded.

It should answer questions such as:

* Are all expected columns present?
* Are mandatory columns present?
* Are unexpected columns present?
* Has a column been renamed?
* Has a column disappeared?
* Are column names correct?
* Are column types compatible with the expected schema?
* Is the dataset structurally compatible with the next processing stage?

This effectively establishes a **data contract** between one stage of the ML data pipeline and the next.

---

## Data-Type Validation

Data-type validation is part of the schema/data-contract responsibility.

The validation layer should verify that each column contains a compatible type.

For example:

```text
age
Expected: integer
Actual:   string
→ FAIL
```

The implementation should distinguish between genuinely incompatible types and technically different representations that are still compatible.

For example, different integer representations should not necessarily be treated as a validation failure if they are semantically equivalent.

This compatibility policy will be defined when the validation component is implemented.

---

## Required-Column Validation

The validation layer should explicitly define which columns are mandatory.

For example:

```text
Required columns:

customer_id
age
income
home_ownership
```

If `income` is missing entirely:

```text
Validation Result

Status: FAIL
Rule: required_column
Column: income
```

This is different from the case where the `income` column exists but individual values are missing.

The distinction is:

```text
Missing column
    ↓
Schema / Data Contract Validation
```

versus:

```text
Column exists
    │
    └── Some values are missing
            ↓
Data Quality / Preprocessing
```

This separation prevents structural problems from being confused with normal data-quality or ML preprocessing decisions.

---

## Broader Validation Responsibilities

The validation component should not be limited to schema checks.

Its responsibilities can be organized into several categories:

```text
Validation Engine
      │
      ├── Structural validation
      │
      ├── Schema validation
      │
      ├── Data-type validation
      │
      ├── Required-field validation
      │
      ├── Identifier / integrity validation
      │
      ├── Data-quality validation
      │
      └── Business-rule validation
```

Examples include:

### Identifier and Integrity Validation

```text
customer_id must exist
application_id must exist
application_id must be unique
```

### Missing-Value Validation

```text
Required fields must not contain null values
```

The specific nullability policy will depend on the dataset and business requirements.

### Range Validation

```text
age must satisfy an accepted business range
loan_amount must satisfy an accepted business range
```

These ranges should be based on domain requirements rather than arbitrary statistical thresholds.

### Cross-Column Consistency

Some rules require relationships between multiple columns.

For example:

```text
employment_length must be compatible with age
```

This is more informative than simply checking whether `employment_length` is below an arbitrary maximum.

Similarly, the previously identified `loan_income_ratio` discrepancy demonstrates why a consistency rule should only be implemented after establishing the authoritative definition of the variable.

---

## Validation Is Not Automatic Data Repair

An important architectural principle established during Phase 02 is that the validation layer should primarily **detect and report violations**.

It should not automatically modify the data simply because a validation rule fails.

The conceptual flow is:

```text
Validation Failure
        ↓
┌───────┼──────────┬────────────┐
│       │          │            │
Reject  Quarantine Correct   Investigate
```

The appropriate action depends on the nature and severity of the violation.

For example:

* a missing mandatory column may cause rejection;
* a malformed record may be quarantined;
* a known deterministic formatting problem may be corrected;
* an unexplained business-rule violation may require investigation.

This preserves the distinction between **detecting a problem** and **deciding how to remediate it**.

---

## Validation Results and Evidence

The validation component should produce meaningful validation results rather than returning only a Boolean value.

For example:

```text
Rule: employment_length_vs_age
Status: FAIL
Rows affected: 2
Severity: ERROR
```

A production-oriented validation system should therefore provide enough information to understand:

* which rule failed
* which dataset failed
* which column or fields are involved
* how many records are affected
* the severity of the violation
* whether the dataset can continue through the pipeline
* what action should be considered

This makes validation observable and testable rather than hiding data-quality problems inside preprocessing code.

---

## Two Validation Layers

The architectural evolution also clarified that validation should not necessarily be represented as one large undifferentiated component.

Two distinct validation stages are useful.

### Validation A — Source / Ingestion Validation

This protects the data platform from structurally unusable incoming data.

```text
Source
  ↓
Schema
Types
Required fields
Basic structural integrity
Basic data-quality controls
  ↓
Standardized Domain Data
```

Its purpose is to establish that incoming data can safely enter the data platform.

### Validation B — Curated ML Dataset Validation

This protects the ML system from an invalid curated dataset.

```text
Curated ML Dataset
       ↓
Schema / Data Contract
       ↓
Data Quality
       ↓
Business Rules
       ↓
Cross-Domain Consistency
       ↓
ML Dataset Accepted / Rejected
       ↓
ML Dataset EDA
       ↓
ML Preprocessing
```

The two layers have related responsibilities but operate at different points in the lifecycle and answer different questions.

---

## Relationship Between Validation and ML Preprocessing

The validation layer does not replace ML preprocessing.

Instead, the responsibilities are separated:

```text
Curated ML Dataset
        │
        ▼
Validation
        │
        │  Is this dataset acceptable?
        ▼
Accepted Dataset
        │
        ▼
ML Preprocessing
        │
        │  How should this dataset be transformed
        │  for machine learning?
        ▼
Training-Ready Dataset
```

Validation determines whether the dataset satisfies defined contracts and quality requirements.

ML preprocessing determines how accepted data should be transformed for model development and inference.

This separation improves reproducibility, testability, and training/inference consistency.

---

## Architectural Principle: Statistical Anomaly Is Not Automatically a Data Error

The validation layer also reinforces a principle established during domain EDA:

> A statistical anomaly is not automatically a data-quality error.

For example:

* a very high income may be unusual but legitimate;
* a rare risk grade may be legitimate;
* an extreme numerical value may require investigation rather than automatic deletion.

Validation rules should therefore be based on:

* source definitions
* domain knowledge
* explicit business constraints
* data contracts
* known technical requirements
* established consistency relationships

rather than purely on statistical rarity.

---

## Future Implementation

The validation layer is now part of the Phase 02 architecture, but it will not be implemented prematurely.

The intended sequence is:

```text
AWS Data Foundation
        ↓
Domain Processing
        ↓
Cross-Domain Integration
        ↓
Curated ML Dataset
        ↓
Curated Dataset Validation
        ↓
ML Dataset EDA
        ↓
ML Preprocessing
        ↓
Training-Ready Dataset
```

This allows the validation rules to be designed against the actual curated dataset and its intended schema rather than against assumptions made before the data-platform processing is complete.

The future implementation is expected to include:

* schema contracts
* expected column definitions
* required/optional fields
* compatible data types
* identifier rules
* data-quality rules
* business rules
* cross-domain consistency rules
* validation results
* severity levels
* failure handling
* automated tests

The exact implementation technology and architecture will be determined when this milestone is reached.

---

## Resulting Architectural Principle

The addition of the validation layer represents an important evolution of Phase 02.

The project is no longer treating the data pipeline simply as:

```text
Data → Cleaning → Features
```

Instead, the architecture is evolving toward:

```text
Data
  ↓
Ingestion
  ↓
Validation
  ↓
Standardization
  ↓
Integration
  ↓
Curated Dataset
  ↓
Validation
  ↓
EDA
  ↓
ML Preprocessing
  ↓
Training-Ready Dataset
```

This establishes validation as a **first-class production component of the ML data foundation**, while preserving a clear separation between detecting data problems, remediating them, and transforming accepted data for machine learning.
