# Business Domain Design

## 1. Purpose

Define the logical business domains of the lending dataset before implementing domain decomposition and AWS data processing.

The original monolithic dataset will be transformed into three business-oriented datasets while keeping the raw source immutable.

## 2. Business Domains

| Domain | Purpose |
|---|---|
| Customer Profile | Represents information about the loan applicant |
| Financial History | Represents available historical credit information |
| Loan Application | Represents the current loan request and its outcome |

These domains represent the core business entities required for the credit-risk ML use case.

## 3. Column-to-Domain Mapping

### Customer Profile Dataset

| Column | Description |
|---|---|
| `person_age` | Applicant age |
| `person_income` | Applicant income |
| `person_home_ownership` | Home ownership status |
| `person_emp_length` | Employment length |

### Financial History Dataset

| Column | Description |
|---|---|
| `cb_person_default_on_file` | Historical default indicator |
| `cb_person_cred_hist_length` | Length of credit history |

The source dataset provides limited historical financial information. It does not contain detailed loan, debt, or payment history.

### Loan Application Dataset

| Column | Description |
|---|---|
| `loan_amnt` | Requested loan amount |
| `loan_intent` | Purpose of the loan |
| `loan_grade` | Loan risk grade |
| `loan_int_rate` | Loan interest rate |
| `loan_percent_income` | Loan amount relative to income |
| `loan_status` | Loan outcome / ML prediction target |

`loan_status` belongs to the Loan Application domain because it represents the outcome of the current application.

## 4. Relationships / Keys

The source dataset does not contain native customer or application identifiers.

Technical identifiers will therefore be introduced during source-level processing for this architecture exercise.

| Dataset | Key |
|---|---|
| Customer Profile | `customer_id` — primary key |
| Financial History | `customer_id` — relationship key |
| Loan Application | `application_id` — primary key; `customer_id` — relationship key |

These identifiers are technical/synthetic keys for the exercise and do not represent real-world customer identities.

Logical relationship:

```
Customer Profile
       |
       | customer_id
       +--------------------+
       |                    |
       ↓                    ↓
Financial History    Loan Application
                         |
                         | application_id
                         ↓
                  ML-ready Dataset
```

The keys allow the domain datasets to be integrated into a single ML-ready dataset.

## 5. S3 Dataset Structure

The decomposed datasets will eventually be stored independently in Amazon S3.

```
S3
└── lending/
    ├── customer_profile/
    ├── financial_history/
    └── loan_application/
```

The exact S3 partitioning, file format, and storage conventions will be defined during the AWS Data Architecture stage.

## 6. Glue Data Catalog

Each domain dataset will be represented as a table in the AWS Glue Data Catalog.

The catalog will provide the metadata required to discover and query the datasets stored in Amazon S3.

AWS Glue will be the primary data processing and transformation engine.

## 7. Athena Usage

Amazon Athena will provide the SQL query and validation layer over the S3 datasets.

Athena will be used for:

- Inspecting domain datasets.
- Validating schemas and data quality.
- Supporting domain-level EDA.
- Validating relationships between datasets.
- Supporting data integration analysis.

Athena is not the primary ETL engine. Data transformations will be implemented through AWS Glue.

## 8. Key Design Decisions

- The original raw dataset remains immutable.
- Source-level processing occurs before domain decomposition.
- The dataset is decomposed into three business-oriented datasets.
- Domain-specific EDA and validation occur after decomposition.
- Technical keys are introduced because the source has no native customer or application identifiers.
- `loan_status` remains part of the Loan Application dataset and is the ML prediction target.
- The three domain datasets will eventually be integrated into an ML-ready dataset.
- Feature engineering occurs after data integration.
- Engineered features may subsequently be managed through Feature Store concepts.
- Feature engineering and Feature Store implementation are outside the scope of this document.
- The architecture is intentionally designed around a small dataset; complexity comes from the architecture and processing workflow rather than data volume.