# Data Quality Policy

## 1. Purpose

This document defines the data quality standards, validation principles, and decision framework for the loan-risk machine learning project.

The objective is to establish a clear and reproducible policy for identifying, evaluating, and handling data quality issues before the data is consumed by downstream machine learning processes.

The policy is based on the findings identified during the Exploratory Data Analysis (EDA) phase.

The main objectives are to:

- Identify data quality issues that may affect downstream analysis or machine learning.
- Distinguish genuine data errors from statistically unusual but valid observations.
- Define business rules for determining whether observations or feature values are valid.
- Establish consistent criteria for handling duplicates, missing values, invalid values, inconsistencies, and anomalous observations.
- Preserve the original raw data as an immutable source of truth.
- Provide a documented specification that can later be implemented as part of the data preprocessing pipeline.
- Support a realistic production-oriented data architecture in which raw and curated data are maintained separately.

This policy is therefore a design specification rather than an implementation document.

The decisions defined here will subsequently be translated into preprocessing transformations and implemented within the project's data pipeline.

---

## 2. Scope

This policy applies to the loan-risk dataset used throughout the project.

The original dataset contains:

- 32,581 observations
- 12 features
- A binary target variable: `loan_status`

The dataset contains information related to three logical business domains:

- Customer information
- Loan information
- Credit information

The current source dataset is a monolithic dataset used as the initial analytical source.

The project will subsequently decompose this source into logical business-domain datasets in order to simulate a more realistic production data environment and provide hands-on experience with AWS data engineering technologies such as Amazon S3, AWS Glue, and Amazon Athena.

The data quality policy therefore applies conceptually to:

1. The original raw source.
2. The logical domain datasets derived from the raw source.
3. The curated datasets produced after data-quality processing.
4. The integrated analytical dataset subsequently used by the machine learning pipeline.

The policy covers the following categories of data quality:

- Exact duplicate records
- Missing values
- Invalid or implausible values
- Statistical anomalies and extreme observations
- Business-rule violations
- Internal feature inconsistencies
- Unexpected categorical values
- Unexpected target values
- Data-type consistency
- Relationships between related variables
- Data integrity across logical business domains

This policy does not define machine learning feature engineering decisions.

Feature engineering will be addressed separately after the data-quality and preprocessing policies have been established.

---

## 3. Data Quality Principles

The following principles govern all data quality decisions in this project.

### 3.1 Raw Data Preservation

The original raw data must remain unchanged.

Raw data represents the original source received by the data platform and must be preserved for:

- Reproducibility
- Auditing
- Debugging
- Data lineage
- Reprocessing
- Comparison between raw and curated data

Data quality transformations must therefore produce a separate processed or curated representation rather than modifying the raw source.

---

### 3.2 Statistical Anomaly Does Not Automatically Mean Data Error

An observation being statistically unusual does not automatically mean that it is invalid.

For example, a very high `person_income` value may be statistically extreme while still representing a legitimate applicant.

Therefore:

> Statistical outlier ≠ automatic data error

Unusual observations must be investigated using both statistical evidence and business/domain knowledge.

---

### 3.3 Business Validity Takes Priority Over Distributional Appearance

Data should not be cleaned simply because a distribution is skewed, multimodal, or contains extreme observations.

The shape of a distribution describes the data but does not, by itself, determine whether observations are valid.

A value should be considered invalid when there is sufficient evidence that it violates a business rule, logical constraint, or known domain limitation.

---

### 3.4 Preserve Valid Information

Valid observations should be retained even when they are statistically unusual.

The objective of data quality processing is not to make the dataset statistically "clean" or normally distributed.

The objective is to produce a dataset that is:

- Valid
- Consistent
- Traceable
- Reproducible
- Suitable for downstream processing

Extreme but legitimate observations may contain important information for a credit-risk model and should not be removed without justification.

---

### 3.5 Explicit Decisions

Every identified data quality issue must have an explicit documented decision.

For each issue, the policy should establish:

- What was observed?
- Why might it be a problem?
- Is it statistically unusual, logically invalid, or both?
- What business rule applies?
- Should the value or record be retained?
- Should it be corrected?
- Should it be removed?
- Should it be imputed?
- Should it be flagged for downstream processing?
- At which stage should the treatment occur?

No data transformation should be introduced merely because it is a common preprocessing technique.

---

### 3.6 Domain-Aware Validation

Data quality must be evaluated in the context of the business meaning of each variable.

For example, an employment length of `123` years is not merely an extreme statistical value.

When combined with an applicant age in the early twenties, it represents a clear business-rule violation.

Similarly, a very high income is unusual but may still be legitimate.

Therefore, validation should consider relationships between variables rather than evaluating every feature independently.

---

### 3.7 Separation of Data Quality and Feature Engineering

Data quality processing and feature engineering are separate concerns.

Data quality processing focuses on ensuring that the source data is valid, consistent, and reliable.

Feature engineering focuses on creating or transforming variables to improve their usefulness for a machine learning model.

This separation will allow the project to maintain a clear boundary between:

- Data correction and validation
- Data preprocessing
- Machine learning feature creation

---

### 3.8 Reproducibility

Data quality decisions must be deterministic, documented, and reproducible.

A future execution of the same preprocessing pipeline against the same raw input should produce the same data-quality outcome.

The policy should therefore avoid undocumented manual corrections whenever possible.

---

### 3.9 Data Lineage

Every transformation applied to the data should be traceable to:

- An identified data quality issue
- A documented policy decision
- A specific preprocessing operation

The project should make it possible to understand how a record moved from:

`Raw`

to:

`Validated / Curated`

and eventually to:

`ML-ready`

without losing the relationship with the original source.

---

### 3.10 Production-Oriented Design

The data quality process should be designed with production data engineering principles in mind.

The project will intentionally preserve the distinction between:

`Raw Data`

and:

`Curated Data`

rather than modifying the original source dataset.

This will allow the later AWS architecture to demonstrate a realistic data lifecycle:

```
Raw Data
    ↓
Data Quality Validation
    ↓
Cleaning / Preprocessing
    ↓
Curated Data
    ↓
Data Integration
    ↓
ML-ready Dataset
```

The final objective is not simply to obtain a clean dataset.

The objective is to establish a **reproducible, auditable, and production-oriented data quality process** that can support the downstream machine learning system.

## 4. Identified Data Quality Issues

The EDA identified several data quality issues and potential data-quality risks in the original dataset.

These issues are classified according to their nature and the appropriate validation strategy.

The objective of this section is not to define the implementation yet, but to document what was observed and establish the policy decision that will later be implemented during preprocessing.

---

### 4.1 Exact Duplicate Records

The dataset contains **165 exact duplicate records**.

An exact duplicate is a record in which all feature values and the target value are identical to another record.

Because these records do not provide additional information and represent repeated copies of the same observation, they should not be retained as independent observations for model development.

**Policy decision:**

- Exact duplicate records will be removed during preprocessing.
- The raw source will remain unchanged.
- Duplicate detection will be performed before downstream modeling.
- The number of removed records should be recorded as part of the preprocessing process.
- The resulting curated dataset should contain no exact duplicate records.

The distinction between raw and curated data is important:

```
Raw Dataset
    ↓
Duplicate Detection
    ↓
Exact Duplicates Identified
    ↓
Remove Duplicates
    ↓
Curated Dataset
```

This treatment applies specifically to **exact duplicates across the complete record**.

Near-duplicates or partially duplicated records will not be removed automatically and require separate investigation.

---

### 4.2 Missing Values

Two variables contain missing values:

| Feature | Missing Records | Approximate Proportion |
|---|---:|---:|
| `loan_int_rate` | 3,116 | 9.56% |
| `person_emp_length` | 895 | 2.75% |

The missingness is therefore concentrated in two numerical features.

Missing values are not automatically considered data errors.

A missing value may represent:

- Information that was not collected
- Information unavailable at the time of data creation
- A data ingestion problem
- A legitimate absence of information
- A systematic issue in the source system

Therefore, the policy must distinguish between **missing information** and **invalid information**.

**Policy decision:**

- Missing values will not be replaced during the EDA stage.
- Missing-value treatment will be defined during preprocessing.
- The treatment must consider the business meaning of each variable.
- Imputation strategies must be applied using information available within the appropriate training data boundaries.
- The target variable `loan_status` must not be imputed.
- Missingness should be assessed for its potential relationship with the target and other features before selecting the final treatment.

The final preprocessing strategy may involve:

- Statistical imputation
- Business-rule-based imputation
- Missing-value indicators
- Model-specific handling of missing values
- Record removal, if justified

The specific strategy will be defined in the Preprocessing Policy.

---

### 4.3 Implausible `person_age` Values

The EDA identified unusually high values in `person_age`.

The maximum observed age is **144 years**.

Examples include applicants with ages of:

- 123
- 144

These values are statistically extreme and, more importantly, are highly implausible from a business perspective.

However, the policy must distinguish between statistical anomaly and confirmed invalidity.

For a lending dataset, an applicant age of 144 years is not considered a realistic business value.

**Policy decision:**

- Ages that violate the established business-validity range will be classified as invalid.
- The raw values will be preserved in the raw dataset.
- Invalid ages will be handled during preprocessing.
- The specific treatment will be determined after establishing the business-validity rule.
- The preprocessing pipeline must explicitly identify these records rather than silently modifying them.

The general principle is:

```
Statistical Anomaly
        ↓
Business Validation
        ↓
Business Rule Violation
        ↓
Invalid Value
        ↓
Preprocessing Treatment
```

The exact valid age range will be documented in the Preprocessing Policy rather than assumed solely from the statistical distribution.

---

### 4.4 Implausible `person_emp_length` Values

The EDA identified extremely large employment-length values.

The maximum observed value is **123 years**.

More importantly, some observations combine very young applicants with extremely long employment histories.

Examples include:

| `person_age` | `person_emp_length` | `person_income` | `loan_status` |
|---:|---:|---:|---:|
| 22 | 123.0 | 59,000 | 1 |
| 21 | 123.0 | 192,000 | 0 |
| 23 | 123.0 | 92,111 | 1 |

These observations represent a clear business-rule problem.

Employment length cannot reasonably exceed the applicant's available lifetime or violate the logical relationship between age and employment history.

**Policy decision:**

- Employment-length values that violate established business constraints will be classified as invalid.
- Values will not be clipped merely because they are statistically extreme.
- Business-rule validation will consider the relationship between `person_age` and `person_emp_length`.
- Invalid employment-length values will be handled during preprocessing.
- The raw values will remain unchanged.
- The specific treatment will be defined in the Preprocessing Policy.

This is an important example of **relational data validation**.

The validity of `person_emp_length` cannot always be determined by examining the feature independently.

---

### 4.5 Extreme `person_income` Values

The EDA identified a highly right-skewed income distribution with several extreme observations.

The maximum observed income is **6,000,000**.

Additional high-income observations were identified in the upper tail, including values above:

- 1 million
- 1.3 million
- 1.4 million
- 1.7 million
- 1.9 million
- 2 million
- 6 million

These observations are statistically unusual but cannot automatically be classified as invalid.

High-income applicants can be legitimate members of the lending population.

**Policy decision:**

- Extreme income values will not be removed solely because they are statistical outliers.
- The raw values will be preserved.
- The upper tail should be subjected to business/domain validation.
- Potential unit inconsistencies, data-entry errors, and source-system encoding issues should be considered.
- If an income value is confirmed to be valid, it will be retained.
- If an income value is confirmed to be invalid, it will be handled according to the preprocessing policy.
- No automatic winsorization or arbitrary clipping will be performed at this stage.

This reinforces the principle:

> Statistical outlier ≠ data error

---

### 4.6 Internal Consistency of `loan_percent_income`

The EDA investigated whether `loan_percent_income` was consistent with the relationship between `loan_amnt` and `person_income`.

A calculated ratio was compared against the existing `loan_percent_income` feature.

The investigation identified **388 observations** with noticeable differences between the calculated ratio and the stored value.

Examples showed that the stored feature does not always exactly reproduce a simple calculation based on the available variables.

However, the differences may result from:

- Rounding
- Different source-system calculation rules
- Different definitions of income
- Different timing of the underlying values
- Data-generation methodology
- Actual data-quality problems

Therefore, the discrepancy cannot automatically be classified as an error.

**Policy decision:**

- The discrepancy will be treated as a **data consistency issue requiring investigation**.
- The existing `loan_percent_income` value will not automatically be overwritten.
- The raw value will be preserved.
- The underlying data-generation rule should be understood before deciding whether recalculation is appropriate.
- If the business definition confirms that the feature should be deterministically derived from `loan_amnt` and `person_income`, the preprocessing policy may define a recalculation rule.
- Otherwise, the original feature should be retained.

This distinction is important because preprocessing should not silently replace source information without understanding its original definition.

---

### 4.7 Multimodality in `loan_amnt`

The EDA showed that `loan_amnt` is not simply right-skewed.

The distribution contains several noticeable concentrations or modes, together with an upper tail.

This may reflect:

- Commonly requested loan amounts
- Standardized lending amounts
- Different loan-purpose populations
- Different borrower segments
- Source-system constraints

The observed multimodality is therefore not itself a data-quality error.

**Policy decision:**

- Multimodality will not be treated as a cleaning problem.
- Loan amounts will not be transformed or removed solely because the distribution contains multiple modes.
- Extreme loan amounts will be evaluated according to business validity.
- The distribution should be retained as part of the natural structure of the feature unless specific invalid values are identified.

---

### 4.8 Multimodality in `loan_int_rate`

The EDA identified multiple concentrations in the interest-rate distribution.

This may reflect different lending or risk segments and may be associated with:

- `loan_grade`
- Borrower risk
- Loan characteristics
- Lending policies
- Loan purpose
- Other underwriting variables

Multimodality therefore does not constitute a data-quality error by itself.

There is also an important modeling consideration: interest rate may encode information about the lender's assessment of borrower risk.

Depending on the exact prediction-time scenario, this feature could potentially introduce **target leakage** or represent information that would not be available at the intended prediction point.

**Policy decision:**

- Multimodality will not be treated as a cleaning problem.
- Missing interest rates will be handled separately.
- The temporal/business availability of `loan_int_rate` must be validated before final model inclusion.
- The feature should not be removed or transformed merely because its distribution is multimodal.
- Potential leakage will be addressed during feature-availability and modeling analysis.

---

### 4.9 Discrete Nature of `cb_person_cred_hist_length`

`cb_person_cred_hist_length` represents credit-history length and behaves as a discrete numerical variable.

The distribution contains sharp peaks because the variable takes discrete values.

The EDA also showed a right-skewed structure, with shorter credit histories being more common.

This is not a data-quality problem.

It is primarily a characteristic of the feature's measurement scale.

**Policy decision:**

- Discrete values will be preserved.
- The variable will not be artificially converted into a continuous variable.
- KDE-based interpretations will not be used as evidence of continuous behavior.
- Any transformation must preserve the semantic meaning of credit-history length.

---

### 4.10 Categorical Domain Validation

The categorical features were validated against their expected categories.

The validation identified:

- No unexpected categories
- No missing expected categories

The validated categorical variables are:

- `person_home_ownership`
- `loan_intent`
- `loan_grade`
- `cb_person_default_on_file`

Therefore, there is no current evidence of invalid categorical labels in these features.

**Policy decision:**

- Existing valid categories will be preserved.
- Unexpected categories appearing in future data should be detected by validation rules.
- Unexpected categories should trigger a data-quality event rather than being silently converted.
- The raw categorical values must remain unchanged.
- Category handling for machine learning encoding belongs to preprocessing/feature preparation, not to the raw-data quality layer.

---

### 4.11 Target Validation

The target variable `loan_status` was validated against its expected binary values.

The observed values are:

- `0`
- `1`

No unexpected target values were identified.

Therefore, the target currently satisfies the expected domain constraint.

**Policy decision:**

- Only valid target values `0` and `1` are accepted.
- Unexpected target values must be flagged as data-quality errors.
- The target must never be imputed.
- Records with invalid target values should not be used for supervised model training until the underlying issue has been resolved.

---

### 4.12 Duplicate Records

The dataset contains **165 exact duplicate records**.

Because these records contain identical information across all columns, they do not represent additional independent observations.

**Policy decision:**

- Exact duplicates will be removed during preprocessing.
- Removal will occur on the derived processing/curated layer.
- The raw source remains unchanged.
- Duplicate removal must be deterministic and reproducible.
- The preprocessing process should record the number of duplicates removed.

---

### 4.13 Overall Classification of Identified Issues

The identified issues can be classified into three broad groups.

**Confirmed or strongly supported data-quality problems**

- Exact duplicate records
- Implausible `person_age` values
- Implausible `person_emp_length` values
- Relational inconsistencies involving age and employment length

**Potential data-quality problems requiring business validation**

- Extreme `person_income` values
- `loan_percent_income` inconsistencies
- Other extreme numerical observations

**Distributional characteristics that are not data-quality errors**

- Right-skewed distributions
- Multimodality in `loan_amnt`
- Multimodality in `loan_int_rate`
- Discrete structure of `cb_person_cred_hist_length`

This distinction prevents the preprocessing stage from becoming an arbitrary process of removing unusual observations.

---

### 4.14 Data Quality Decision Framework

All future data-quality decisions should follow the same general framework:

```
Observed Issue
        ↓
Classify Issue
        ↓
Statistical Anomaly?
        ↓
Business / Domain Validation
        ↓
Is the Value Valid?
      ↙       ↘
    Yes        No
     ↓          ↓
   Keep     Handle in
            Preprocessing
```

The purpose of this framework is to ensure that cleaning decisions are based on evidence and business meaning rather than on distributional appearance alone.

---

### 4.15 Relationship With the Preprocessing Policy

This section identifies the data-quality issues and establishes the high-level decisions.

The exact operational treatment of each issue will be defined separately in the **Preprocessing Policy**.

The Preprocessing Policy will specify:

- Validation rules
- Transformation rules
- Missing-value strategies
- Duplicate-removal procedures
- Invalid-value handling
- Record-level treatment
- Feature-level treatment
- Ordering of preprocessing operations
- Data-quality checks after preprocessing
- Reproducibility requirements

This separation ensures that the Data Quality Policy answers:

> **What is considered a data-quality issue and what is our decision?**

while the Preprocessing Policy answers:

> **How exactly will that decision be implemented?**

# 5. Data Quality Decision Matrix

The following matrix converts the EDA findings into explicit data-quality decisions.

| Issue | Feature(s) | Classification | Policy Decision |
|---|---|---|---|
| Exact duplicates | All columns | Data quality error | Remove during preprocessing |
| Implausible age | `person_age` | Business-rule violation | Validate and handle during preprocessing |
| Implausible employment length | `person_emp_length` | Business-rule violation | Validate against age and handle during preprocessing |
| Extreme income | `person_income` | Potential anomaly | Investigate; do not automatically remove |
| Loan/income inconsistency | `loan_percent_income` | Consistency issue | Validate source definition before changing |
| Missing values | `loan_int_rate`, `person_emp_length` | Missing data | Define treatment in preprocessing policy |
| Unexpected categorical values | Categorical features | Data quality error | Reject/flag during validation |
| Invalid target values | `loan_status` | Data quality error | Reject/flag; never impute |
| Multimodality | `loan_amnt`, `loan_int_rate` | Distribution characteristic | Do not treat as a cleaning error |
| Discrete feature | `cb_person_cred_hist_length` | Distribution characteristic | Preserve semantic structure |

The central principle is:

```
Unusual
    ↓
Investigate
    ↓
Business validation
    ↓
Valid → Keep
Invalid → Handle
```

---

# 6. Duplicate-Record Policy

Exact duplicate records will be removed from the processing dataset.

The raw source must remain unchanged.

Duplicate handling will therefore follow:

```
Raw Data
    ↓
Duplicate Detection
    ↓
Remove Exact Duplicates
    ↓
Curated Data
```

Only exact duplicates across the complete record are covered by this policy.

Near-duplicates or partial duplicates require separate investigation.

---

# 7. Missing-Value Policy

Missing values were identified in:

- `loan_int_rate`
- `person_emp_length`

Missing values will not be automatically removed or replaced during the raw-data validation stage.

The final treatment will be defined during preprocessing according to:

- Feature semantics
- Missingness behavior
- Model requirements
- Training-data boundaries

The target variable must never be imputed.

---

# 8. Invalid-Value and Business-Rule Policy

Values that violate established business rules will be treated differently from legitimate statistical outliers.

Examples include:

- Implausible `person_age`
- Implausible `person_emp_length`
- Invalid categorical values
- Invalid `loan_status` values

Validation should consider relationships between features where appropriate.

For example:

```
person_age
     +
person_emp_length
     ↓
Business-rule validation
     ↓
Valid / Invalid
```

Invalid observations will be handled during preprocessing according to the specific rule defined for each feature.

---

# 9. Outlier Policy

Statistical outliers will **not** be removed automatically.

An extreme value will first be classified as either:

1. A legitimate observation
2. A data-quality error
3. An observation requiring further investigation

In particular:

- Extreme `person_income` values will be investigated rather than automatically removed.
- High `loan_amnt` values will be evaluated according to business validity.
- High `loan_percent_income` values will not be removed merely because they are rare.

The guiding principle is:

```
Statistical Outlier ≠ Data Error
```

Any transformation, clipping, winsorization, or removal must have a documented justification.

---

# 10. Data Quality Validation Requirements

The preprocessing pipeline must verify that the resulting curated data satisfies the established quality rules.

At minimum, validation must check:

- No exact duplicate records
- Valid `person_age` values
- Valid `person_emp_length` values
- Valid categorical domains
- Valid `loan_status` values
- Defined treatment of missing values
- Consistency of derived/related financial features
- Preservation of required data types
- No unintended loss of records or columns

The overall workflow is:

```
Raw Data
    ↓
Quality Validation
    ↓
Preprocessing
    ↓
Post-Processing Validation
    ↓
Curated Data
```

The validation process should be **reproducible and auditable** so that the same rules can be applied consistently to future data.

The detailed implementation of these rules belongs to the Preprocessing Policy and pipeline, not to this document.