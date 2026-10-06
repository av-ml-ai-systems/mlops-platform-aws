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

## Ephemeral AWS Infrastructure and Reproducible Cloud Validation

### Evolution

The initial Phase 2 plan assumed that the AWS data foundation could remain provisioned while the implementation progressed. During the transition from local-first development to the AWS data platform, the approach was refined to use **ephemeral AWS infrastructure as the default operating model**.

The objective is not to maintain a permanently running AWS environment. The objective is to gain hands-on experience with the AWS data platform, validate the architecture against real AWS services, inspect the resulting resources in the AWS Console, collect implementation evidence, and then remove the infrastructure when the validation session is complete.

The infrastructure remains reproducible because the **local project repository contains the Terraform configuration, application code, SQL, tests, documentation, and other implementation assets required to recreate the environment**.

Git and GitHub provide version control, history, and remote backup of the project, but AWS reconstruction does not fundamentally depend on GitHub. The local project itself is the operational reconstruction source.

This results in the following operating model:

```text
                    LOCAL PROJECT
                         │
              ┌──────────┴──────────┐
              │                     │
        Terraform code         Application /
        configuration          processing code
              │                     │
              └──────────┬──────────┘
                         │
                         ▼
                Provision AWS Resources
                         │
                         ▼
              Upload / Process / Validate
                         │
                         ▼
               Console Inspection
                  + Evidence
                         │
                         ▼
                  Document Results
                         │
                         ▼
                 Destroy Resources
                         │
                         ▼
                 AWS removed
                         │
                         ▼
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
│
├── src/
│   └── mlops_engineering_roadmap/
│
├── tests/
│
├── notebooks/
│
├── sql/
│
├── infrastructure/
│   └── terraform/
│       └── aws/
│
├── scripts/
│
├── docs/
│   └── Phase-02/
│
└── README.md
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
                 ┌──────────────────┐
                 │ Terraform        │
                 │ Python/PySpark   │
                 │ SQL              │
                 │ Tests            │
                 │ Configuration    │
                 │ Documentation    │
                 └────────┬─────────┘
                          │
                          │ terraform apply
                          ▼
                    AWS ENVIRONMENT
                          │
                          │ validation
                          ▼
                    AWS RESOURCES
                          │
                          │ terraform destroy
                          ▼
                    AWS REMOVED
                          │
                          │
                          └───────────────┐
                                          │
                       terraform apply    │
                                          ▼
                                   AWS RECREATED
```

### Role of Git and GitHub

Git remains an important part of the engineering workflow, but it should not be confused with the reconstruction mechanism itself.

The relationship is:

```text
                 LOCAL PROJECT
                       │
              ┌────────┴────────┐
              ▼                 ▼
       Local development       Git
       and execution       version history
              │                 │
              │                 ▼
              │              GitHub
              │        remote repository /
              │        backup / portfolio
              │
              └───────────────┐
                              ▼
                     AWS reconstruction
```

Therefore:

* **Local project** → operational source for development and reconstruction.
* **Terraform** → infrastructure definition and recreation mechanism.
* **Git** → version control and historical record.
* **GitHub** → remote repository, backup, and portfolio visibility.
* **AWS** → temporary execution and validation environment.

The AWS environment should never become the only place where the architecture exists.

### Standard AWS session lifecycle

Each AWS implementation session will follow a controlled lifecycle:

```text
1. CREATE
      │
      ▼
2. VERIFY
      │
      ▼
3. INSPECT
      │
      ▼
4. DOCUMENT
      │
      ▼
5. SCREENSHOT / EVIDENCE
      │
      ▼
6. DESTROY
      │
      ▼
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
      │
      ▼
Infrastructure Exists
      │
      ▼
Functional Validation
      │
      ▼
Expected AWS Behavior
```

#### 3. Inspect

The AWS Console will be used as a complementary learning and verification tool.

The Console is useful for understanding how the infrastructure appears from an AWS operational perspective and for visually confirming configuration.

The Console is **not** the authoritative mechanism for creating or maintaining infrastructure.

Terraform remains the infrastructure definition.

```text
Terraform
   │
   ├──► Defines infrastructure
   │
   └──► Recreates infrastructure

AWS Console
   │
   ├──► Inspect
   ├──► Understand
   └──► Capture evidence
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
      │
      │ authoritative implementation
      ▼
AWS Resources
      │
      │ temporary validation
      ▼
Screenshots / Evidence
      │
      ▼
Documentation
```

#### 6. Destroy

After validation and evidence collection are complete, the temporary AWS resources will normally be destroyed.

The default policy is:

```text
AWS resource created for validation
             │
             ▼
        Validate it
             │
             ▼
       Capture evidence
             │
             ▼
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
   │
   ├── Current objects
   │
   └── Previous object versions
             │
             ▼
       Complete cleanup
             │
             ▼
       Bucket destruction
```

Terraform destruction must therefore be tested carefully for the chosen S3 configuration.

The goal is to ensure that ephemeral infrastructure is genuinely removed rather than leaving versioned objects or other residual resources behind.

### 7. Recreate later

When the next Phase 2 session begins, the infrastructure can be recreated directly from the local project.

The intended process is:

```text
LOCAL PROJECT
      │
      ├── Terraform
      ├── Configuration
      ├── Processing code
      ├── Validation code
      ├── Athena SQL
      ├── Tests
      └── Documentation
             │
             ▼
        terraform apply
             │
             ▼
       AWS infrastructure
             │
             ▼
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
──────────
Local project
Terraform
Tests
SQL
Documentation
Evidence
Git history
        │
        │ recreates
        ▼
EPHEMERAL
──────────
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
      │
      ▼
Terraform Configuration
      │
      ▼
terraform apply
      │
      ▼
AWS resources
      │
      ▼
Validate
      │
      ▼
terraform destroy
      │
      ▼
AWS resources removed
      │
      ▼
terraform apply
      │
      ▼
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
      │
      ├── Provision if explicitly required
      ├── Process
      ├── Validate
      └── Produce results

Separate infrastructure lifecycle operation
      │
      └── Explicit terraform destroy
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
                    │
                    ▼
            Keep resources small
                    │
                    ▼
          Validate real behavior
                    │
                    ▼
          Capture implementation evidence
                    │
                    ▼
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
        ┌─────────────────────┐
        │ Code                │
        │ Terraform           │
        │ Configuration       │
        │ Tests               │
        │ SQL                 │
        │ Documentation       │
        │ Evidence            │
        └──────────┬──────────┘
                   │
                   ▼
          REPRODUCIBLE AWS
            ENVIRONMENT
                   │
                   ▼
             AWS VALIDATION
                   │
          ┌────────┴────────┐
          ▼                 ▼
    Console Inspection   Programmatic
    + Screenshots         Validation
          │                 │
          └────────┬────────┘
                   ▼
              DOCUMENT
               RESULTS
                   │
                   ▼
              DESTROY AWS
               RESOURCES
                   │
                   ▼
             RECREATE LATER
             FROM LOCAL PROJECT
```

### Current Phase 2 implication

The next implementation step is to design the **S3 Data Lake foundation** before provisioning it.

The intended sequence is:

```text
Phase 2
   │
   ▼
S3 Data Lake Architecture
   │
   ▼
Terraform Implementation
   │
   ▼
Create AWS Resources
   │
   ▼
Upload Domain Datasets
   │
   ▼
Programmatic Verification
   │
   ▼
AWS Console Inspection
   │
   ▼
Screenshots / Evidence
   │
   ▼
Documentation
   │
   ▼
Destroy AWS Resources
   │
   ▼
Recreate Later from Local Project
```

The three-layer S3 data-lake architecture will be designed next. The architectural target is **Raw → Standardized → Curated**, but only the resources required for the current milestone will be provisioned initially.

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
├── customer/customer.csv
├── financial_history/financial_history.csv
└── loan_application/loan_application.csv
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
        │
        ▼
Glue Crawler
        │
        ▼
Glue Data Catalog
        │
        ├── customer
        ├── financial_history
        └── loan_application
```

This establishes the metadata/catalog layer required for subsequent Athena-based exploration and validation.

#### Infrastructure lifecycle decision

The Glue environment used during this milestone is considered temporary learning infrastructure.

The manually validated IAM configuration will be codified in Terraform before the Glue environment is recreated.

The target infrastructure will include:

```text
Terraform
    │
    ├── Glue IAM role
    ├── Glue IAM policies
    ├── Glue Data Catalog database
    └── Glue crawler
```

This separates the initial manual AWS validation from the subsequent infrastructure-as-code implementation.

The Glue environment will be destroyed after today's validation to keep the AWS learning account clean and minimize unnecessary AWS usage.

The next Phase 2 implementation step will be to reproduce the validated Glue IAM and Data Catalog foundation through Terraform.
