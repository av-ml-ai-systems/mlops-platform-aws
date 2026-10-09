# Phase 02 â€” Evolution

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
    â†“
S3 Data Lake
    â†“
Glue Data Catalog
    â†“
Athena
    â†“
SageMaker Processing
    â†“
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
            â†“
     Domain Decomposition
            â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚           â”‚            â”‚
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
    â†“
Potential Quality / Business Rule
    â†“
Determine Authoritative Definition
    â†“
Implement Validation Rule
    â†“
Define Appropriate Action
```

The action following a validation failure may depend on the nature of the problem:

```text
Validation Failure
        â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚       â”‚        â”‚            â”‚
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
                        â”‚
                        â–¼
              Source / Ingestion Layer
                        â”‚
                â”Œâ”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”
                â”‚ Validation     â”‚
                â”‚ Basic cleaning â”‚
                â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                        â”‚
                        â–¼
              Standardized / Curated
                   Domain Data
                        â”‚
                        â–¼
                 Domain-Level EDA
                        â”‚
                        â–¼
              Domain Validation
                        â”‚
                        â–¼
              Curated ML Dataset
                        â”‚
                        â–¼
              ML Dataset EDA
                        â”‚
                        â–¼
          ML Preprocessing / Features
                        â”‚
                        â–¼
              Training-Ready Dataset
```

This lifecycle is the current architectural direction and may be refined further as Phase 02 implementation progresses.

---

## Phase 02 Current Roadmap

At the current milestone, the Phase 02 implementation has progressed through:

```text
1. Domain Design
       âœ“ Complete

2. Domain Decomposition
       âœ“ Complete

3. Domain-Level EDA
       âœ“ Complete

4. AWS Data Foundation
       â”‚
       â”œâ”€â”€ Amazon S3
       â”œâ”€â”€ AWS Glue
       â”œâ”€â”€ Glue Data Catalog
       â””â”€â”€ Amazon Athena

5. Source / Ingestion Validation
       â”‚
       â””â”€â”€ Structural and basic data-quality controls

6. Domain Processing / Standardization
       â”‚
       â””â”€â”€ AWS Glue

7. Cross-Domain Integration
       â”‚
       â””â”€â”€ Curated ML Dataset

8. Curated Dataset Validation
       â”‚
       â””â”€â”€ Business, consistency, and quality rules

9. ML Dataset EDA
       â”‚
       â””â”€â”€ Analysis of the integrated curated dataset

10. ML Preprocessing
       â”‚
       â”œâ”€â”€ Missing-value strategy
       â”œâ”€â”€ Encoding
       â”œâ”€â”€ Transformations
       â””â”€â”€ Training / inference consistency

11. Training-Ready Dataset
       â”‚
       â””â”€â”€ Versioning and metadata

12. Dataset Versioning / Lineage
       â”‚
       â””â”€â”€ Reproducibility
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
             â†“
      Python / PySpark
             â†“
      â”Œâ”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”
      â†“             â†“
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
    â”‚
    â–¼
Source / Ingestion
    â”‚
    â”œâ”€â”€ Source validation
    â””â”€â”€ Basic structural cleaning
    â”‚
    â–¼
Standardized Domain Data
    â”‚
    â–¼
Domain-Level EDA
    â”‚
    â–¼
Domain Processing / Standardization
    â”‚
    â””â”€â”€ AWS Glue
    â”‚
    â–¼
Cross-Domain Integration
    â”‚
    â–¼
CURATED ML DATASET
    â”‚
    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚      CURATED DATA VALIDATION     â”‚
â”‚                                  â”‚
â”‚  Schema validation               â”‚
â”‚  Data-type validation            â”‚
â”‚  Required-column validation      â”‚
â”‚  Identifier validation           â”‚
â”‚  Null / missing-value checks     â”‚
â”‚  Domain/business rules           â”‚
â”‚  Cross-column consistency        â”‚
â”‚  Dataset integrity checks        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
    â”‚
    â”œâ”€â”€ PASS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚                           â”‚
    â””â”€â”€ FAIL â†’ reject /         â”‚
               quarantine /     â”‚
               investigate      â”‚
                                â–¼
                         ML Dataset EDA
                                â”‚
                                â–¼
                       ML Preprocessing
                                â”‚
                                â–¼
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

customer_id â†’ string             customer_id â†’ string       âœ“
age         â†’ integer             age         â†’ string       âœ—
income      â†’ numeric             income      â†’ numeric      âœ“
home_ownership â†’ string           home_ownership â†’ string    âœ“
employment_length â†’ numeric      missing column             âœ—
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
â†’ FAIL
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
    â†“
Schema / Data Contract Validation
```

versus:

```text
Column exists
    â”‚
    â””â”€â”€ Some values are missing
            â†“
Data Quality / Preprocessing
```

This separation prevents structural problems from being confused with normal data-quality or ML preprocessing decisions.

---

## Broader Validation Responsibilities

The validation component should not be limited to schema checks.

Its responsibilities can be organized into several categories:

```text
Validation Engine
      â”‚
      â”œâ”€â”€ Structural validation
      â”‚
      â”œâ”€â”€ Schema validation
      â”‚
      â”œâ”€â”€ Data-type validation
      â”‚
      â”œâ”€â”€ Required-field validation
      â”‚
      â”œâ”€â”€ Identifier / integrity validation
      â”‚
      â”œâ”€â”€ Data-quality validation
      â”‚
      â””â”€â”€ Business-rule validation
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
        â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚       â”‚          â”‚            â”‚
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

### Validation A â€” Source / Ingestion Validation

This protects the data platform from structurally unusable incoming data.

```text
Source
  â†“
Schema
Types
Required fields
Basic structural integrity
Basic data-quality controls
  â†“
Standardized Domain Data
```

Its purpose is to establish that incoming data can safely enter the data platform.

### Validation B â€” Curated ML Dataset Validation

This protects the ML system from an invalid curated dataset.

```text
Curated ML Dataset
       â†“
Schema / Data Contract
       â†“
Data Quality
       â†“
Business Rules
       â†“
Cross-Domain Consistency
       â†“
ML Dataset Accepted / Rejected
       â†“
ML Dataset EDA
       â†“
ML Preprocessing
```

The two layers have related responsibilities but operate at different points in the lifecycle and answer different questions.

---

## Relationship Between Validation and ML Preprocessing

The validation layer does not replace ML preprocessing.

Instead, the responsibilities are separated:

```text
Curated ML Dataset
        â”‚
        â–¼
Validation
        â”‚
        â”‚  Is this dataset acceptable?
        â–¼
Accepted Dataset
        â”‚
        â–¼
ML Preprocessing
        â”‚
        â”‚  How should this dataset be transformed
        â”‚  for machine learning?
        â–¼
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
        â†“
Domain Processing
        â†“
Cross-Domain Integration
        â†“
Curated ML Dataset
        â†“
Curated Dataset Validation
        â†“
ML Dataset EDA
        â†“
ML Preprocessing
        â†“
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
Data â†’ Cleaning â†’ Features
```

Instead, the architecture is evolving toward:

```text
Data
  â†“
Ingestion
  â†“
Validation
  â†“
Standardization
  â†“
Integration
  â†“
Curated Dataset
  â†“
Validation
  â†“
EDA
  â†“
ML Preprocessing
  â†“
Training-Ready Dataset
```

This establishes validation as a **first-class production component of the ML data foundation**, while preserving a clear separation between detecting data problems, remediating them, and transforming accepted data for machine learning.

## Ephemeral AWS Infrastructure and Reproducible Cloud Validation

### Evolution

The initial Phase 2 plan assumed that the AWS data foundation could remain provisioned while the implementation progressed. During the transition from local-first development to the AWS data platform, the approach was refined to use **ephemeral AWS infrastructure as the default operating model**.

The objective is not to maintain a permanently running AWS environment. The objective is to gain hands-on experience with the AWS data platform, validate the architecture against real AWS services, inspect the resulting resources in the AWS Console, collect implementation evidence, and then remove the infrastructure when the validation session is complete.

The infrastructure remains reproducible because the **local project repository contains the Terraform configuration, application code, SQL, tests, documentation, and other implementation assets required to recreate the environment**.

Git and GitHub provide version control, history, and remote backup of the project, but AWS reconstruction does not fundamentally depend on GitHub. The local project itself is the operational reconstruction source.

This results in the following operating model:

```text
                    LOCAL PROJECT
                         â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              â”‚                     â”‚
        Terraform code         Application /
        configuration          processing code
              â”‚                     â”‚
              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚
                         â–¼
                Provision AWS Resources
                         â”‚
                         â–¼
              Upload / Process / Validate
                         â”‚
                         â–¼
               Console Inspection
                  + Evidence
                         â”‚
                         â–¼
                  Document Results
                         â”‚
                         â–¼
                 Destroy Resources
                         â”‚
                         â–¼
                 AWS removed
                         â”‚
                         â–¼
              Recreate later from
                local project
```

### Why the approach changed

The project is being developed as an MLOps learning and portfolio platform rather than as a permanently hosted production service.

Keeping cloud resources alive between implementation sessions provides limited additional learning value while introducing unnecessary cost and resource-management overhead.

The revised approach therefore prioritizes:

* reproducibility over persistence
* infrastructure-as-code over manually maintained resources
* controlled cloud usage over continuously running infrastructure
* real AWS validation over theoretical architecture
* documented evidence over permanent environments
* explicit resource destruction after validation
* rapid recreation when the next implementation session begins

This is also consistent with an important MLOps principle:

> **The environment should be reproducible from the project source rather than depend on manually preserved infrastructure.**

### Local project as the reconstruction source

The **local project repository is the primary operational source of truth for infrastructure reconstruction**.

Terraform configuration will live inside the project alongside the data-engineering and ML platform code that it supports.

Conceptually, the project will contain:

```text
mlops-platform-aws/
â”‚
â”œâ”€â”€ src/
â”‚   â””â”€â”€ mlops_engineering_roadmap/
â”‚
â”œâ”€â”€ tests/
â”‚
â”œâ”€â”€ notebooks/
â”‚
â”œâ”€â”€ sql/
â”‚
â”œâ”€â”€ infrastructure/
â”‚   â””â”€â”€ terraform/
â”‚       â””â”€â”€ aws/
â”‚
â”œâ”€â”€ scripts/
â”‚
â”œâ”€â”€ docs/
â”‚   â””â”€â”€ Phase-02/
â”‚
â””â”€â”€ README.md
```

The exact directory structure will evolve as Phase 2 is implemented. The important principle is that Terraform belongs **inside the project**, rather than being maintained as a separate external infrastructure project.

The project should contain the implementation required to recreate the AWS environment, including where applicable:

* Terraform configuration
* Terraform variables and configuration
* processing logic
* validation logic
* Athena SQL
* tests
* scripts
* documentation
* architecture definitions
* implementation notes

The resulting relationship is:

```text
                    LOCAL PROJECT
                 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                 â”‚ Terraform        â”‚
                 â”‚ Python/PySpark   â”‚
                 â”‚ SQL              â”‚
                 â”‚ Tests            â”‚
                 â”‚ Configuration    â”‚
                 â”‚ Documentation    â”‚
                 â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                          â”‚
                          â”‚ terraform apply
                          â–¼
                    AWS ENVIRONMENT
                          â”‚
                          â”‚ validation
                          â–¼
                    AWS RESOURCES
                          â”‚
                          â”‚ terraform destroy
                          â–¼
                    AWS REMOVED
                          â”‚
                          â”‚
                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                          â”‚
                       terraform apply    â”‚
                                          â–¼
                                   AWS RECREATED
```

### Role of Git and GitHub

Git remains an important part of the engineering workflow, but it should not be confused with the reconstruction mechanism itself.

The relationship is:

```text
                 LOCAL PROJECT
                       â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”
              â–¼                 â–¼
       Local development       Git
       and execution       version history
              â”‚                 â”‚
              â”‚                 â–¼
              â”‚              GitHub
              â”‚        remote repository /
              â”‚        backup / portfolio
              â”‚
              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                              â–¼
                     AWS reconstruction
```

Therefore:

* **Local project** â†’ operational source for development and reconstruction.
* **Terraform** â†’ infrastructure definition and recreation mechanism.
* **Git** â†’ version control and historical record.
* **GitHub** â†’ remote repository, backup, and portfolio visibility.
* **AWS** â†’ temporary execution and validation environment.

The AWS environment should never become the only place where the architecture exists.

### Standard AWS session lifecycle

Each AWS implementation session will follow a controlled lifecycle:

```text
1. CREATE
      â”‚
      â–¼
2. VERIFY
      â”‚
      â–¼
3. INSPECT
      â”‚
      â–¼
4. DOCUMENT
      â”‚
      â–¼
5. SCREENSHOT / EVIDENCE
      â”‚
      â–¼
6. DESTROY
      â”‚
      â–¼
7. RECREATE LATER FROM THE LOCAL PROJECT
```

#### 1. Create

Terraform provisions only the AWS resources required for the current implementation milestone.

Examples may include:

* S3 bucket
* S3 configuration
* Glue database
* Glue crawler
* Glue job
* Athena workgroup
* SageMaker Processing resources

Not all resources will be created simultaneously. The infrastructure will grow incrementally as Phase 2 progresses.

#### 2. Verify

After provisioning, the implementation will be verified programmatically and, where useful, through the AWS Console.

Verification should establish that:

* the expected resources exist
* Terraform reports the expected state
* configuration is correct
* permissions are sufficient
* resources can perform the intended operation
* expected data can be uploaded, processed, queried, or validated

Cloud validation is therefore not based solely on successful Terraform execution.

```text
Terraform Apply
      â”‚
      â–¼
Infrastructure Exists
      â”‚
      â–¼
Functional Validation
      â”‚
      â–¼
Expected AWS Behavior
```

#### 3. Inspect

The AWS Console will be used as a complementary learning and verification tool.

The Console is useful for understanding how the infrastructure appears from an AWS operational perspective and for visually confirming configuration.

The Console is **not** the authoritative mechanism for creating or maintaining infrastructure.

Terraform remains the infrastructure definition.

```text
Terraform
   â”‚
   â”œâ”€â”€â–º Defines infrastructure
   â”‚
   â””â”€â”€â–º Recreates infrastructure

AWS Console
   â”‚
   â”œâ”€â”€â–º Inspect
   â”œâ”€â”€â–º Understand
   â””â”€â”€â–º Capture evidence
```

#### 4. Document

The important results of the implementation session will be recorded in the Phase 2 documentation.

Documentation should capture:

* what was provisioned
* why the resource was required
* how it fits into the architecture
* what was validated
* important implementation decisions
* relevant limitations or findings
* evidence that the AWS implementation worked

The Phase 2 evolution document records architectural evolution and rationale, while implementation-specific documentation can contain operational details.

#### 5. Screenshot / evidence

When useful, screenshots will be captured from the AWS Console to provide visual evidence of the implemented architecture.

Examples include:

* S3 bucket configuration
* S3 object structure
* Glue database/table configuration
* Glue crawler results
* Athena query execution
* SageMaker Processing configuration or execution
* relevant AWS resource status

The screenshots are evidence of the cloud validation performed during the session. They do not replace Terraform or source code.

The implementation itself remains reproducible from the local project.

```text
LOCAL PROJECT
      â”‚
      â”‚ authoritative implementation
      â–¼
AWS Resources
      â”‚
      â”‚ temporary validation
      â–¼
Screenshots / Evidence
      â”‚
      â–¼
Documentation
```

#### 6. Destroy

After validation and evidence collection are complete, the temporary AWS resources will normally be destroyed.

The default policy is:

```text
AWS resource created for validation
             â”‚
             â–¼
        Validate it
             â”‚
             â–¼
       Capture evidence
             â”‚
             â–¼
       Destroy resource
```

Resources expected to be destroyed after validation include, where applicable:

* S3 bucket and temporary data
* Glue crawlers
* Glue jobs
* Glue databases or workgroups when no longer required
* Athena workgroups when unnecessary
* SageMaker Processing resources
* EC2 or other compute resources
* other temporary AWS infrastructure created specifically for the session

The exact destruction sequence will depend on resource dependencies.

### S3-specific consideration

S3 requires additional care because bucket destruction is not equivalent to simply deleting the bucket declaration.

If S3 versioning is enabled, previous object versions may remain even after the current object is deleted.

Therefore, the destruction process must account for:

```text
S3 Bucket
   â”‚
   â”œâ”€â”€ Current objects
   â”‚
   â””â”€â”€ Previous object versions
             â”‚
             â–¼
       Complete cleanup
             â”‚
             â–¼
       Bucket destruction
```

Terraform destruction must therefore be tested carefully for the chosen S3 configuration.

The goal is to ensure that ephemeral infrastructure is genuinely removed rather than leaving versioned objects or other residual resources behind.

### 7. Recreate later

When the next Phase 2 session begins, the infrastructure can be recreated directly from the local project.

The intended process is:

```text
LOCAL PROJECT
      â”‚
      â”œâ”€â”€ Terraform
      â”œâ”€â”€ Configuration
      â”œâ”€â”€ Processing code
      â”œâ”€â”€ Validation code
      â”œâ”€â”€ Athena SQL
      â”œâ”€â”€ Tests
      â””â”€â”€ Documentation
             â”‚
             â–¼
        terraform apply
             â”‚
             â–¼
       AWS infrastructure
             â”‚
             â–¼
       Repeat validation
```

This means that destroying the infrastructure does **not** mean losing the implementation.

The cloud environment is temporary; the engineering implementation is persistent.

### What is persistent and what is ephemeral

The project deliberately separates persistent engineering assets from temporary cloud resources.

#### Persistent

The following remain in the local project:

* Terraform configuration
* Terraform variables and configuration templates
* Python / PySpark processing logic
* validation logic
* Athena SQL
* tests
* configuration definitions
* architecture documentation
* Phase evolution documentation
* ADRs where appropriate
* README documentation
* implementation notes
* screenshots and validation evidence, where appropriate and safe to retain

Git provides version history for these assets, and GitHub provides a remote copy of the project.

#### Ephemeral

The following are normally created only for cloud validation:

* S3 buckets
* temporary S3 data
* Glue jobs
* Glue crawlers
* Athena workgroups when not required persistently
* SageMaker Processing resources
* temporary compute
* other temporary AWS infrastructure

The fundamental distinction is:

```text
PERSISTENT
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
Local project
Terraform
Tests
SQL
Documentation
Evidence
Git history
        â”‚
        â”‚ recreates
        â–¼
EPHEMERAL
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
AWS infrastructure
AWS data
AWS compute
AWS managed resources
```

### Terraform's role

Terraform becomes the mechanism that makes this ephemeral model practical.

Without infrastructure-as-code, repeatedly destroying and recreating resources would introduce unnecessary manual work and increase the risk of configuration drift.

With Terraform:

```text
Local Project
      â”‚
      â–¼
Terraform Configuration
      â”‚
      â–¼
terraform apply
      â”‚
      â–¼
AWS resources
      â”‚
      â–¼
Validate
      â”‚
      â–¼
terraform destroy
      â”‚
      â–¼
AWS resources removed
      â”‚
      â–¼
terraform apply
      â”‚
      â–¼
AWS resources recreated
```

This provides practical experience with:

* Infrastructure as Code
* reproducible environments
* controlled provisioning
* controlled destruction
* infrastructure lifecycle management
* configuration consistency
* reduction of manual configuration
* environment recreation

The ability to recreate the environment becomes part of the MLOps engineering outcome rather than merely a cost-saving technique.

### Controlled destruction

Destruction must remain an **explicit operational action**.

Normal processing or validation workflows must never accidentally execute a destructive operation.

For example:

```text
Normal pipeline
      â”‚
      â”œâ”€â”€ Provision if explicitly required
      â”œâ”€â”€ Process
      â”œâ”€â”€ Validate
      â””â”€â”€ Produce results

Separate infrastructure lifecycle operation
      â”‚
      â””â”€â”€ Explicit terraform destroy
```

The project will therefore keep the distinction between:

* data-processing operations
* validation operations
* infrastructure provisioning
* infrastructure destruction

This separation reduces the risk of accidentally deleting infrastructure or data during normal development.

### Cost-control principle

Cost control is an explicit architectural concern because the project is being developed under a limited personal budget.

The strategy is therefore:

```text
Use AWS when AWS provides learning or architectural value
                    â”‚
                    â–¼
            Keep resources small
                    â”‚
                    â–¼
          Validate real behavior
                    â”‚
                    â–¼
          Capture implementation evidence
                    â”‚
                    â–¼
              Destroy resources
```

The project does not attempt to avoid AWS entirely.

Instead, it uses AWS deliberately and temporarily where managed services provide meaningful MLOps experience.

This preserves the practical value of working with:

* Amazon S3
* AWS Glue
* Glue Data Catalog
* Amazon Athena
* Amazon SageMaker

while minimizing unnecessary persistent resource usage.

### Architectural and MLOps value

The ephemeral infrastructure strategy is itself an MLOps engineering lesson.

The important principle is not:

> "Keep the cloud environment running."

The important principle is:

> **"Make the cloud environment reproducible."**

A production system may require persistent infrastructure, but a learning and portfolio environment does not need to remain permanently provisioned to demonstrate that the architecture works.

The Phase 2 project therefore treats AWS as a reproducible execution and validation environment rather than as a manually maintained development environment.

### Resulting Phase 2 operating principle

```text
             LOCAL PROJECT
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â”‚ Code                â”‚
        â”‚ Terraform           â”‚
        â”‚ Configuration       â”‚
        â”‚ Tests               â”‚
        â”‚ SQL                 â”‚
        â”‚ Documentation       â”‚
        â”‚ Evidence            â”‚
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                   â”‚
                   â–¼
          REPRODUCIBLE AWS
            ENVIRONMENT
                   â”‚
                   â–¼
             AWS VALIDATION
                   â”‚
          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”
          â–¼                 â–¼
    Console Inspection   Programmatic
    + Screenshots         Validation
          â”‚                 â”‚
          â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                   â–¼
              DOCUMENT
               RESULTS
                   â”‚
                   â–¼
              DESTROY AWS
               RESOURCES
                   â”‚
                   â–¼
             RECREATE LATER
             FROM LOCAL PROJECT
```

### Current Phase 2 implication

The next implementation step is to design the **S3 Data Lake foundation** before provisioning it.

The intended sequence is:

```text
Phase 2
   â”‚
   â–¼
S3 Data Lake Architecture
   â”‚
   â–¼
Terraform Implementation
   â”‚
   â–¼
Create AWS Resources
   â”‚
   â–¼
Upload Domain Datasets
   â”‚
   â–¼
Programmatic Verification
   â”‚
   â–¼
AWS Console Inspection
   â”‚
   â–¼
Screenshots / Evidence
   â”‚
   â–¼
Documentation
   â”‚
   â–¼
Destroy AWS Resources
   â”‚
   â–¼
Recreate Later from Local Project
```

The three-layer S3 data-lake architecture will be designed next. The architectural target is **Raw â†’ Standardized â†’ Curated**, but only the resources required for the current milestone will be provisioned initially.

### AWS Data Lake Infrastructure Validation

The Phase 2 AWS data foundation was validated through an ephemeral Terraform deployment.

Terraform provisioned the initial S3 data lake bucket:

- **Bucket:** `mlops-engineering-data-lake-882507341805`
- **Region:** `us-east-2`
- **Terraform resource:** `aws_s3_bucket.mlops_data_lake`

The deployment was validated through three complementary mechanisms:

1. **Terraform validation**
   - `terraform validate`
   - `terraform plan`
   - `terraform apply`

2. **AWS CLI verification**
   - `aws s3 ls`
   - `aws s3api head-bucket --bucket mlops-engineering-data-lake-882507341805`

3. **AWS Console verification**
   - The bucket was inspected directly in the AWS Console.
   - Screenshots were captured as visual evidence of the deployed resource.

The bucket was intentionally created as an ephemeral learning/validation resource. The deployment confirms that the local Terraform configuration can successfully provision the AWS data lake foundation and that the resulting resource is accessible through both the AWS CLI and Console.

The resource will be destroyed after the documentation milestone is captured, consistent with the project's ephemeral AWS infrastructure strategy.

### S3 Bucket Versioning Validation

The S3 data lake infrastructure was extended with object versioning to improve protection against accidental overwrites and support object-level data history.

Terraform configured S3 Versioning for the data lake bucket:

* **Bucket:** `mlops-engineering-data-lake-882507341805`
* **Region:** `us-east-2`
* **Terraform resource:** `aws_s3_bucket_versioning.mlops_data_lake`
* **Versioning status:** Enabled

The configuration was validated through three mechanisms:

1. **Terraform validation**

   * `terraform fmt`
   * `terraform validate`
   * `terraform plan`
   * `terraform apply`

2. **AWS CLI verification**

   * `aws s3api get-bucket-versioning`
   * `aws s3api head-bucket`

   The bucket returned:

   `Status: Enabled`

   and confirmed the expected bucket ARN and region.

3. **AWS Console verification**

   * The bucket was inspected directly in the AWS Console.
   * Bucket Versioning was confirmed as **Enabled**.
   * Screenshots were captured as visual evidence.

S3 Versioning provides version history for individual objects stored in the bucket. It is an infrastructure-level capability and is distinct from dataset-level versioning and ML lineage, which will be addressed separately in the Phase 2 dataset versioning strategy.

The deployment remains ephemeral and will be destroyed after validation, consistent with the project's AWS infrastructure strategy.

### S3 Data Lake Hardening Validation

The S3 data lake foundation was consolidated into a single infrastructure milestone with the following security and data-protection controls:

* **S3 Bucket**

  * Bucket: `mlops-engineering-data-lake-882507341805`
  * Region: `us-east-2`

* **Object Versioning**

  * Enabled to preserve previous object versions.

* **Server-Side Encryption**

  * SSE-S3 using AES256.
  * Encryption is automatically applied to new objects.
  * AWS-managed S3 encryption keys are used.

* **Public Access Protection**

  * Block Public ACLs: Enabled
  * Block Public Policy: Enabled
  * Ignore Public ACLs: Enabled
  * Restrict Public Buckets: Enabled

* **Object Ownership**

  * `BucketOwnerEnforced`
  * ACL-based object ownership and permissions are disabled.

The configuration was validated through three mechanisms:

1. **Terraform validation**

   * `terraform fmt`
   * `terraform validate`
   * `terraform plan`
   * `terraform apply`

2. **AWS CLI verification**

   * S3 Versioning confirmed as `Enabled`.
   * Server-side encryption confirmed as `AES256`.
   * All four public-access-block controls confirmed as `true`.
   * Object ownership confirmed as `BucketOwnerEnforced`.
   * Bucket existence and region confirmed through `head-bucket`.

3. **AWS Console verification**

   * The bucket configuration was inspected directly in the AWS Console.
   * Screenshots were captured as visual evidence of:

     * default SSE-S3 encryption,
     * public access protection,
     * and object ownership configuration.

The S3 foundation is intentionally implemented as one physical bucket with multiple infrastructure-level configuration controls. Logical data-lake layers such as `raw/`, `standardized/`, and `curated/` will be addressed later as part of the data processing architecture.

The deployment remains ephemeral and will be destroyed after the documentation milestone is captured, consistent with the project's AWS infrastructure strategy.

### AWS Glue Data Catalog Validation

After validating the S3 data lake foundation, the next Phase 2 milestone was the integration of AWS Glue Data Catalog.

The objective was to make the standardized domain datasets stored in S3 discoverable through AWS Glue Data Catalog and to validate the relationship between S3 data, Glue metadata, and the crawler.

#### S3 standardized datasets

The three standardized domain datasets were uploaded to:

```text
s3://mlops-engineering-data-lake-882507341805/standardized/
â”œâ”€â”€ customer/customer.csv
â”œâ”€â”€ financial_history/financial_history.csv
â””â”€â”€ loan_application/loan_application.csv
```

The original source dataset remained conceptually separate from these standardized domain datasets.

#### Glue Data Catalog database

A Glue Data Catalog database was created:

```text
mlops_engineering_data_lake
```

This database provides the metadata layer for the standardized datasets stored in S3.

#### Glue crawler

A crawler was created with the following configuration:

```text
Crawler:
mlops-standardized-data-crawler

S3 target:
s3://mlops-engineering-data-lake-882507341805/standardized/

Database:
mlops_engineering_data_lake

Schedule:
On demand
```

The crawler was initially unable to discover the datasets because its IAM role did not have permission to read the S3 objects.

#### IAM permission issue and resolution

The crawler initially used:

```text
MLOpsGlueCrawlerRole
```

with the AWS-managed:

```text
AWSGlueServiceRole
```

policy.

The crawler execution completed, but CloudWatch logs showed:

```text
glue.amazonaws.com is not authorized to perform:
s3:GetObject
```

The issue was therefore identified as an S3 data-access permission problem rather than a crawler configuration failure.

A dedicated inline policy was added to the crawler role:

```text
MLOpsGlueCrawlerS3ReadAccess
```

The policy grants only the permissions required by the crawler:

```text
s3:ListBucket
s3:GetObject
```

The permissions were restricted to the project S3 bucket and the `standardized/` prefix.

This established a least-privilege access model instead of granting broad S3 permissions.

#### Crawler validation

After the IAM policy was added, the crawler was executed again.

The crawler completed successfully and the Data Catalog contained three tables:

```text
customer
financial_history
loan_application
```

Their S3 locations were validated as:

```text
customer
s3://mlops-engineering-data-lake-882507341805/standardized/customer/

financial_history
s3://mlops-engineering-data-lake-882507341805/standardized/financial_history/

loan_application
s3://mlops-engineering-data-lake-882507341805/standardized/loan_application/
```

#### Schema validation

The crawler successfully inferred the expected schemas.

Customer:

```text
customer_id         string
age                 bigint
income              bigint
home_ownership      string
employment_length   double
```

Financial History:

```text
customer_id             string
default_history         string
credit_history_length   bigint
```

Loan Application:

```text
application_id       string
customer_id          string
loan_amount          bigint
loan_purpose         string
risk_grade           string
loan_interest_rate   double
loan_income_ratio    double
loan_outcome         bigint
```

#### Validation evidence

AWS Console screenshots were captured showing:

* the Glue Data Catalog database and its three tables;
* the `customer` table schema and S3 location;
* the successful crawler execution.

#### Architectural outcome

The validated metadata flow is:

```text
S3 Standardized Data
        â”‚
        â–¼
Glue Crawler
        â”‚
        â–¼
Glue Data Catalog
        â”‚
        â”œâ”€â”€ customer
        â”œâ”€â”€ financial_history
        â””â”€â”€ loan_application
```

This establishes the metadata/catalog layer required for subsequent Athena-based exploration and validation.

#### Infrastructure lifecycle decision

The Glue environment used during this milestone is considered temporary learning infrastructure.

The manually validated IAM configuration will be codified in Terraform before the Glue environment is recreated.

The target infrastructure will include:

```text
Terraform
    â”‚
    â”œâ”€â”€ Glue IAM role
    â”œâ”€â”€ Glue IAM policies
    â”œâ”€â”€ Glue Data Catalog database
    â””â”€â”€ Glue crawler
```

This separates the initial manual AWS validation from the subsequent infrastructure-as-code implementation.

The Glue environment will be destroyed after today's validation to keep the AWS learning account clean and minimize unnecessary AWS usage.

The next Phase 2 implementation step will be to reproduce the validated Glue IAM and Data Catalog foundation through Terraform.

### Terraform Automation and Athena Console Validation

This stage converted the AWS data-foundation configuration discovered and validated manually during the previous Glue Data Catalog session into reproducible Terraform-managed infrastructure and completed the Athena Console validation of the resulting platform.

#### Terraform Automation of the AWS Data Foundation

The previous Glue implementation identified the required AWS resources and revealed an operational permission requirement: the Glue crawler needed explicit S3 read access to inspect the standardized datasets.

That configuration was codified in Terraform rather than recreated manually.

Terraform now manages:

* Amazon S3 data lake bucket.
* S3 bucket versioning.
* S3 server-side encryption.
* S3 public access blocking.
* S3 ownership controls.
* The three standardized domain datasets as `aws_s3_object` resources.
* Glue crawler IAM role.
* AWS-managed Glue service-role permissions.
* Least-privilege S3 read permissions for the Glue crawler.
* Glue Data Catalog database.
* Glue crawler targeting the standardized S3 layer.

The three existing validated domain datasets were imported into Terraform state and the manually created AWS environment was subsequently destroyed before performing a clean Terraform deployment.

The clean deployment completed successfully:

```text
Apply complete! Resources: 13 added, 0 changed, 0 destroyed.
```

Terraform state contained the expected S3, IAM, Glue Catalog, and Glue crawler resources.

Terraform validation also completed successfully:

```text
terraform validate
Success! The configuration is valid.
```

A subsequent Terraform plan reported no infrastructure drift:

```text
No changes. Your infrastructure matches the configuration.
```

This established that the AWS data foundation can be reconstructed from the repository rather than depending on manually configured AWS resources.

#### Glue Data Catalog Validation

The Terraform-managed Glue crawler was executed successfully against the standardized S3 layer.

The crawler discovered the expected three tables:

* `customer`
* `financial_history`
* `loan_application`

The discovered schemas matched the previously validated local domain datasets.

The Glue Data Catalog therefore provides the metadata layer required by downstream query and analytics services without moving the underlying datasets out of Amazon S3.

#### Athena Query Configuration

The Athena Query Editor was inspected through the AWS Console using the `primary` workgroup.

The query editor exposed:

* Data source: `AwsDataCatalog`
* Database: `mlops_engineering_data_lake`
* Tables:

  * `customer`
  * `financial_history`
  * `loan_application`

Athena query results were configured to use the existing S3 location:

```text
s3://mlops-engineering-data-lake-882507341805/athena-results/
```

This separates the source datasets from Athena-generated query-result objects.

The resulting logical organization is:

```text
mlops-engineering-data-lake-882507341805/
â”‚
â”œâ”€â”€ standardized/
â”‚   â”œâ”€â”€ customer/customer.csv
â”‚   â”œâ”€â”€ financial_history/financial_history.csv
â”‚   â””â”€â”€ loan_application/loan_application.csv
â”‚
â””â”€â”€ athena-results/
    â””â”€â”€ Athena query result objects
```

#### Athena Console Validation

Athena was validated interactively through the AWS Console rather than exclusively through the CLI.

##### Metadata validation

The following query successfully returned the three Glue Catalog tables:

```sql
SHOW TABLES;
```

Result:

```text
customer
financial_history
loan_application
```

No underlying data was scanned for this metadata operation.

##### Data-access validation

The following query successfully queried the S3-backed `customer` dataset:

```sql
SELECT COUNT(*) AS row_count
FROM customer;
```

Result:

```text
row_count = 32581
```

Athena reported approximately 914.55 KB of data scanned.

This matched the previously validated local dataset and the earlier CLI validation.

##### Analytical query validation

Athena was also used to perform an aggregation over the `loan_application` dataset:

```sql
SELECT risk_grade, COUNT(*) AS application_count
FROM loan_application
GROUP BY risk_grade
ORDER BY risk_grade;
```

The result matched the previously established domain EDA distribution:

| Risk grade | Application count |
| ---------- | ----------------: |
| A          |            10,777 |
| B          |            10,451 |
| C          |             6,458 |
| D          |             3,626 |
| E          |               964 |
| F          |               241 |
| G          |                64 |

Athena reported approximately 1.48 MB of data scanned.

#### Athena Query History

The Athena Console Query History was inspected to understand operational query metadata.

The history exposed:

* Query execution IDs.
* Query text.
* Execution timestamps.
* Query status.
* Execution duration.
* Data scanned.
* Athena engine version.
* Query-result S3 locations.
* Cache status.
* Result-management information.

The executions used Athena engine version 3 and successfully produced query-result objects under the configured S3 prefix.

This demonstrated that Athena is not a database containing copied datasets. It is a serverless query engine that uses Glue Data Catalog metadata to interpret and query data stored in Amazon S3.

#### Architecture Validation

The complete validated architecture is now:

```text
Validated Local Domain Data
            â”‚
            â–¼
        Terraform
            â”‚
            â–¼
      Amazon S3 Data Lake
       standardized/
            â”‚
            â–¼
       Glue Crawler
            â”‚
            â–¼
   Glue Data Catalog
            â”‚
            â–¼
      Amazon Athena
            â”‚
       SQL queries
            â”‚
            â”œâ”€â”€ metadata validation
            â”œâ”€â”€ row-count validation
            â””â”€â”€ analytical aggregation
            â”‚
            â–¼
     athena-results/
```

The roles of the services are clearly separated:

* **Amazon S3** stores the actual datasets.
* **AWS Glue Crawler** discovers dataset structure and schema.
* **Glue Data Catalog** stores metadata describing the datasets.
* **Amazon Athena** queries the S3 data using that metadata.
* **Terraform** provides reproducible infrastructure configuration.

#### Engineering Lessons

This implementation established several important engineering principles:

1. AWS infrastructure discovered manually should be codified when it becomes part of the reproducible platform.
2. Data storage, metadata management, and query execution are separate concerns.
3. Glue Catalog metadata does not replace the underlying S3 data.
4. Athena can query S3 data directly without loading it into a traditional database.
5. Athena query cost is related to the amount of data scanned, making query design and data organization operational concerns.
6. Metadata queries such as `SHOW TABLES` can validate catalog connectivity without scanning the underlying datasets.
7. Query results are separate S3 objects and must be considered during lifecycle and infrastructure cleanup.
8. Manual AWS experimentation is useful for discovering the required configuration, while Terraform is used to make the final infrastructure reproducible.
9. The local repository remains the reconstruction source for the learning environment; AWS resources are treated as ephemeral execution infrastructure.

#### Phase 2 Status After This Stage

```text
1. Source / Domain Design
   âœ“ Complete

2. Domain-Level EDA
   âœ“ Complete

3. AWS Data Foundation
   âœ“ S3
   âœ“ Glue Data Catalog
   âœ“ Athena CLI validation
   âœ“ Athena Console validation

4. Source / Ingestion Validation
   â†’ Next major milestone

5. Domain Processing / Standardization
   â†’ Pending

6. Cross-Domain Integration
   â†’ Pending

7. Curated Dataset Validation
   â†’ Pending

8. ML Dataset EDA
   â†’ Pending

9. ML Preprocessing
   â†’ Pending

10. Training-Ready Dataset
   â†’ Pending
```

The AWS data foundation is therefore considered technically validated before moving into the next Phase 2 milestone.

## Dataset Validation Component

The next Phase 2 milestone was the implementation of a reusable dataset validation component for the standardized domain datasets.

The objective was to establish a validation boundary between domain-level processing and the future cross-domain integration step. Validation was intentionally separated from cleaning and preprocessing: the validator evaluates whether a dataset satisfies its defined contract but does not automatically modify or repair the data.

Three domain-specific validation modules were implemented:

- Customer Profile
- Financial History
- Loan Application

The validation component was organized into:

- domain-specific validation rules
- shared validation execution
- structured validation results
- dataset-level validation reports

Each validation rule produces a structured result containing:

- rule name
- PASS / WARNING / FAIL status
- severity
- validation message
- number of affected rows

The complete validation execution is represented by a `ValidationReport`. Its overall status is derived from the individual rule results:

- any FAIL â†’ overall FAIL
- otherwise any WARNING â†’ overall WARNING
- otherwise â†’ PASS

### Validation Rules Implemented

The Customer Profile validator checks:

- expected schema
- expected data types
- customer identifier presence and uniqueness
- valid age and income values
- allowed home-ownership categories
- employment-length consistency with customer age

The Financial History validator checks:

- expected schema
- expected data types
- customer identifier presence and uniqueness
- valid default-history values
- valid credit-history length

The Loan Application validator checks:

- expected schema
- expected data types
- application identifier presence and uniqueness
- customer identifier presence
- valid loan amounts
- valid loan-to-income ratios
- allowed loan purposes
- valid risk grades
- valid loan outcomes

The validation rules were intentionally based on defensible data contracts rather than arbitrary thresholds derived from observed values during EDA.

### Validation Against the Real Domain Datasets

The validators were executed against the actual domain datasets generated during Phase 2.

The results were:

- Customer Profile: FAIL â€” 2 employment-consistency violations
- Financial History: PASS
- Loan Application: PASS

The two Customer Profile failures correspond to the two clearly inconsistent employment-history records identified during domain EDA.

During implementation, the employment consistency rule was refined. An initial rule based on an estimated working-age assumption produced excessive false positives. The rule was therefore reduced to the defensible invariant that employment duration cannot exceed customer age.

After this correction, the validator identified exactly the two records previously identified during EDA, demonstrating consistency between exploratory analysis and formal validation.

The source datasets were not modified by the validation process.

### Validation Tests and Engineering Quality

A dedicated validation test module was added covering:

- valid domain datasets
- invalid employment history
- invalid categorical values
- invalid risk grades
- validation report status behavior

The complete project test suite passed:

- 28 tests passed

The validation modules also passed:

- Ruff checks
- Ruff formatting checks
- MyPy
- pre-commit hooks

### Git Milestone

The validation component was committed and pushed to the main branch.

Commit:

`2668222 feat: implement phase 2 dataset validation`

This milestone establishes the validation layer for the individual domain datasets.

### Next Step

Individual domain validation is now complete.

The next Phase 2 step is cross-domain integration using Athena. The validated Customer Profile, Financial History, and Loan Application datasets will be joined into a single authoritative curated ML dataset.

The curated dataset will then require its own validation layer to verify:

- join integrity
- expected row cardinality
- application uniqueness
- customer referential integrity
- final schema and data types
- required ML features
- target validity
- final dataset quality

Curated-dataset validation is therefore intentionally deferred until the Athena integration has been implemented.

---

## 2026-10-09 â€” Domain Cleaning and Validation Pipelines

### Completed

Implemented a local domain-cleaning and validation foundation for the three credit-risk datasets.

**Domain cleaning**
- Customer Profile: remove exact duplicate rows, standardize categorical values, and set inconsistent employment lengths to missing.
- Financial History: remove exact duplicate rows and standardize default-history values.
- Loan Application: remove exact duplicate rows and standardize loan-purpose and risk-grade values.
- Preserve legitimate missing values and unusual but potentially valid records.
- Generate separate JSON cleaning reports.
- Preserve raw input datasets.

**Domain validation**
- Implement domain-specific validation rules for all three datasets.
- Implement a validation orchestrator that reads processed datasets, executes the existing rules, and persists JSON reports separately from cleaning reports.
- Keep validation read-only and separate from cleaning responsibilities.

### Real-data verification

The cleaning and validation pipelines were executed against the actual processed datasets.

- Customer Profile: 32,581 input rows and 32,581 output rows; 2 inconsistent employment lengths set to missing.
- Financial History: 32,581 input rows and 32,581 output rows; no cleaning issues reported.
- Loan Application: 32,581 input rows and 32,581 output rows; 3,116 missing interest rates preserved and reported as a warning.
- Domain validation: all 18 rules passed across the three datasets.
- Full automated test suite: 61 tests passed.

Persisted reports:

- `data/processed/cleaning_reports/`
- `data/processed/validation_reports/`

### Architecture and boundaries

The current implementation is local and uses Python and pandas. It establishes the domain-cleaning and validation logic before cloud integration.

The following work remains separate and is not completed by this milestone:

- AWS execution of the cleaning and validation workflows.
- Glue Data Catalog integration.
- Athena-based cross-domain joins and curated dataset creation.
- Curated dataset validation.
- SageMaker Processing and ML-specific preprocessing.

### Next steps

1. Review and finalize the Phase 2 documentation.
2. Review the Git diff and stage the intended implementation, tests, and documentation changes.
3. Commit and push the completed local domain-cleaning and validation milestone.
4. Plan Athena integration as a separate next step.
5.
