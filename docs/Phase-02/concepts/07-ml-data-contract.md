# ML Data Contract

## 1. Purpose and Scope

This contract defines the requirements for the curated loan-risk dataset before it is consumed by downstream machine learning pipelines.

It establishes the dataset schema, candidate features, target definition, data quality requirements, validation evidence, and conditions that must be satisfied before model training.

The contract supports reproducibility, data quality, traceability, and leakage prevention throughout the MLOps lifecycle.

## 2. Dataset Location and Data Lineage

### 2.1 Source Dataset

The project uses the Credit Risk Dataset obtained from Kaggle.

The original dataset contains customer characteristics, credit history information, loan application attributes, and the loan outcome.

### 2.2 Data Processing Flow

The data pipeline follows this sequence:

1. Original dataset ingestion.
2. Standardization and validation.
3. Decomposition into customer, financial history, and loan application domains.
4. AWS Glue ETL transformation and joining.
5. Curated dataset storage in Amazon S3.
6. Data Catalog registration and validation through Amazon Athena.
7. Downstream ML data preparation.

### 2.3 Curated Dataset Location

**Dataset name:** `curated_loan_risk_dataset`

**S3 location:**

`s3://mlops-engineering-data-lake-882507341805/curated/loan_risk_dataset/`

The dataset is registered in the AWS Glue Data Catalog and queried through Amazon Athena.

### 2.4 Lineage Requirements

Each preparation run should record the source dataset version, transformation configuration, execution information, and output location.

Changes to upstream data or transformation logic must be traceable to the resulting ML dataset.

## 3. Dataset Schema

The curated dataset contains 14 columns.

| Column | Logical role | Expected data type |
|---|---|---|
| `application_id` | Application identifier | String |
| `customer_id` | Customer identifier | String |
| `loan_amount` | Candidate feature | Numeric |
| `loan_purpose` | Candidate feature | Categorical |
| `risk_grade` | Candidate feature | Categorical |
| `loan_interest_rate` | Candidate feature | Numeric |
| `loan_income_ratio` | Candidate feature | Numeric |
| `loan_outcome` | Target | Binary integer |
| `age` | Candidate feature | Numeric |
| `income` | Candidate feature | Numeric |
| `home_ownership` | Candidate feature | Categorical |
| `employment_length` | Candidate feature | Numeric |
| `default_history` | Candidate feature | Categorical or binary, subject to verification |
| `credit_history_length` | Candidate feature | Numeric |

These are the intended logical types for ML preparation, not a claim about the current physical schema.

AWS Glue currently registers the curated columns as strings. Downstream processing must explicitly parse and validate values against their intended types.

The final schema must be checked for missing, unexpected, or incorrectly typed columns before training.

## 4. Feature Definitions and Model Input Policy

### 4.1 Candidate Features

The curated dataset contains the following candidate predictive features.

| Feature | Definition | Considerations |
|---|---|---|
| `loan_amount` | Amount of the loan requested | Verify positive and otherwise permitted values. |
| `loan_purpose` | Intended purpose of the loan | Validate categories and prepare for categorical encoding. |
| `risk_grade` | Risk grade associated with the loan | Confirm when the grade is assigned and whether it leaks target information. |
| `loan_interest_rate` | Interest rate associated with the loan | Confirm availability at prediction time. |
| `loan_income_ratio` | Ratio relating loan amount and income | Verify its formula, units, and valid range. |
| `age` | Customer age | Validate against applicable domain and project policies. |
| `income` | Customer income | Verify units and permitted values. |
| `home_ownership` | Customer's home ownership category | Validate categories and prepare for encoding. |
| `employment_length` | Length of employment | Verify units and missing-value policy. |
| `default_history` | Historical default information | Confirm its representation and availability at prediction time. |
| `credit_history_length` | Duration of credit history | Verify units and permitted values. |

These 11 fields are candidate inputs, not an irrevocable final feature list.

Their final inclusion depends on data validation, the prediction use case, availability at inference time, and leakage analysis.

### 4.2 Identifiers and Feature Exclusions

The following columns must not be used as predictive features in the initial model:

- `application_id`
- `customer_id`

These identifiers support traceability and operational data management. They should be excluded from the model input matrix unless a separately justified modeling decision establishes otherwise.

The target column, `loan_outcome`, must never be included among the input features.

The final feature list must be explicitly defined and validated by the ML preparation pipeline.

## 5. Target Variable Definition

### 5.1 Target Column

The model prediction target is `loan_outcome`.

The original source column, `loan_status`, is renamed to `loan_outcome` during domain decomposition. The transformation does not change the original target values.

The target semantics are based on the source Credit Risk Dataset documentation.

| Value | Meaning |
|---|---|
| `0` | Non-default |
| `1` | Default |

### 5.2 Machine Learning Task

The prediction task is binary classification.

The model is intended to predict whether a loan will default, subject to the precise prediction use case and the availability of input features at prediction time.

### 5.3 Target Validation

Before training, the pipeline must verify that:

- The target column exists.
- No target values are missing.
- Values can be parsed as integers.
- Only the values `0` and `1` are permitted.
- The target is excluded from all model input features.

Unexpected target values must cause validation to fail or require explicit investigation.

### 5.4 Observed Target Distribution

The current curated dataset contains 32,581 records.

| Target | Meaning | Records | Percentage |
|---|---|---:|---:|
| `0` | Non-default | 25,473 | 78.19% |
| `1` | Default | 7,108 | 21.81% |
| **Total** | | **32,581** | **100%** |

The target distribution is imbalanced. Model evaluation must therefore consider minority-class performance rather than relying exclusively on accuracy.

## 6. Data Quality and Validation Expectations

The curated dataset must satisfy the following requirements before ML preparation is considered complete.

| Validation area | Requirement |
|---|---|
| Schema | Confirm all 14 expected columns exist and unexpected schema changes are investigated. |
| Data types | Parse numeric and categorical columns according to their logical types. |
| Missing values | Measure missingness per column and apply documented handling rules. |
| Numeric values | Check permitted ranges, invalid values, and parsing failures. |
| Categorical values | Inspect observed categories and investigate unexpected values. |
| Target | Require valid, non-missing binary values. |
| Identifiers | Validate identifier integrity and exclude identifiers from predictive inputs. |
| Duplicates | Check duplicate applications and define the correct business-level uniqueness rule before removing records. |
| Feature leakage | Investigate features that may contain information unavailable at prediction time. |
| Reproducibility | Record dataset versions, preparation settings, and data split configuration. |

### 6.1 Numeric Preparation

Numerical features must be converted to appropriate numeric types.

The preparation pipeline must distinguish invalid values from legitimate missing values and document how each is handled.

### 6.2 Categorical Preparation

Categorical features must be checked for inconsistent or unexpected values.

Any encoding must be fitted using training data only and then applied consistently to validation, test, and inference data.

### 6.3 Missing-Value Policy

Missing values must be measured before selecting an imputation or exclusion strategy.

Imputation rules must be documented and learned from training data when applicable.

### 6.4 Leakage Prevention

Features must represent information available at the intended prediction time.

In particular, `risk_grade`, `loan_interest_rate`, and `default_history` require further investigation before their inclusion is finalized.

No feature should be accepted merely because it improves model performance.

## 7. Current Validation Evidence

The following checks have already been completed.

| Check | Result |
|---|---|
| Domain validation tests | 10 tests passed |
| Glue ETL job | Succeeded |
| Glue Data Catalog | Four tables registered |
| Curated dataset | 32,581 records |
| Distinct-row count | 32,581 |
| Target distribution | 25,473 non-default; 7,108 default |
| Domain row counts | 32,581 records per domain |
| Cross-domain customer identifiers | No unmatched identifiers reported |

The matching total and distinct-row counts indicate that no exact duplicate rows were detected by that check. They do not establish uniqueness under every possible business rule.

Similarly, successful ETL execution and domain tests do not establish that every ML-specific validation requirement has been satisfied.

The logical data types, complete feature validity, missing-value handling, and final leakage assessment still require verification.

## 8. Requirements Before ML Training

The ML preparation pipeline must complete the following tasks before producing training data.

1. Read the curated dataset from its registered S3 location.
2. Validate the expected schema and explicitly convert data types.
3. Measure missing values and validate numeric and categorical fields.
4. Validate the target and exclude it from the input feature matrix.
5. Exclude identifiers from predictive inputs.
6. Investigate feature availability and target leakage.
7. Define and apply the approved preprocessing rules.
8. Create reproducible training, validation, and test partitions.
9. Preserve the target distribution through stratified splitting when appropriate.
10. Record the source version, split configuration, preprocessing configuration, and validation results.

Learned preprocessing operations, including imputation and encoding, must be fitted using training data only.

The validation and test sets must not influence preprocessing fit or model selection in ways that compromise an unbiased evaluation.

The exact split proportions and random seed will be specified in the ML preparation implementation.

### 8.1 Evaluation Requirements

Accuracy alone is insufficient for evaluating the binary classifier.

Evaluation should include:

- Precision.
- Recall.
- F1-score.
- Confusion matrix.

Additional metrics, including ROC-AUC or precision-recall AUC, may be included where appropriate.

Metric selection should reflect the costs of false positives and false negatives in the intended use case.

## 9. Contract Ownership and Change Management

This contract defines the expected interface between data engineering and downstream ML components.

Changes to the source schema, target definition, candidate features, data types, or validation rules must be reviewed and documented.

A change that affects model inputs or target semantics requires corresponding updates to data preparation and validation logic.

Where practical, automated tests should enforce the contract and detect unexpected changes before training.

## 10. Known Gaps and Open Items

The following items remain open:

1. Confirm the availability of each candidate feature at prediction time.
2. Investigate possible leakage involving `risk_grade` and `loan_interest_rate`.
3. Verify the representation and interpretation of `default_history`.
4. Establish permitted ranges and units for numerical fields.
5. Measure missing values and define handling policies.
6. Verify the intended business-level uniqueness rule for loan applications.
7. Implement and test explicit type conversion.
8. Finalize the model feature list.
9. Implement reproducible train, validation, and test splitting.
10. Define the final ML dataset validation gate.

These items must be addressed at the appropriate stage before model training is approved.

## 11. Definition of Done

The ML data contract is considered operationally satisfied when:

- The curated dataset matches the expected schema.
- Logical data types are validated and enforced.
- The target semantics and permitted values are confirmed.
- Missing values and invalid values are handled according to documented rules.
- Identifiers are excluded from predictive inputs.
- Feature availability and leakage risks have been assessed.
- The final feature list is explicitly defined.
- Train, validation, and test datasets are generated reproducibly.
- Validation results and dataset lineage are recorded.
- Automated checks prevent invalid data from silently entering model training.

The existence of this document does not itself satisfy these requirements. Completion must be supported by implementation and validation evidence.