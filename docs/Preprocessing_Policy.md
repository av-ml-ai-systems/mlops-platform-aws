# Preprocessing Policy

## 1. Purpose

This document defines the preprocessing rules required to transform validated raw data into a consistent, reliable, and ML-ready dataset.

The policy translates the decisions established in the Data Quality Policy into concrete preprocessing requirements.

The objective is to ensure that preprocessing is:

- Reproducible
- Deterministic
- Auditable
- Consistent across datasets
- Suitable for downstream machine learning

---

## 2. Scope

This policy applies to the raw lending dataset and to the domain-oriented datasets that will later be derived from it.

The preprocessing process covers:

- Duplicate removal
- Invalid-value handling
- Missing-value treatment
- Business-rule validation
- Data-type consistency
- Cross-feature consistency checks
- Post-processing validation

Feature engineering is explicitly outside the scope of this document.

The raw source data must remain unchanged.

The intended data flow is:

```
Raw Data
    ↓
Domain Separation
    ↓
Data Quality Validation
    ↓
Preprocessing
    ↓
Curated Domain Data
    ↓
Integration
    ↓
ML-ready Dataset
```

---

## 3. Preprocessing Principles

The preprocessing pipeline must follow these principles.

### 3.1 Preserve Raw Data

Raw data is immutable.

No cleaning or transformation should overwrite the original source dataset.

---

### 3.2 Reproducibility

The same input data and preprocessing rules must produce the same output.

Preprocessing decisions must therefore be explicit and deterministic.

---

### 3.3 Separation of Responsibilities

Data quality validation determines whether data satisfies defined quality rules.

Preprocessing applies the corresponding treatment.

Feature engineering creates new representations or features for modeling.

These responsibilities must remain separate.

---

### 3.4 No Automatic Outlier Removal

Statistical extremeness alone is not sufficient justification for removing an observation.

Values must first be evaluated against business and data-quality rules.

---

### 3.5 Preserve Information Whenever Possible

Valid observations should be retained.

Data should only be removed, modified, or imputed when there is a documented justification.

---

### 3.6 Validate Before and After Processing

The pipeline should validate the relevant quality conditions before preprocessing and verify that the resulting curated data satisfies those conditions afterward.

## 4. Duplicate Handling

Exact duplicate records will be removed during preprocessing.

The definition of an exact duplicate is a record with identical values across all columns.

The raw dataset remains unchanged.

The preprocessing process must:

- Detect exact duplicates.
- Remove duplicated copies.
- Preserve one instance of each unique record.
- Record the number of duplicates removed.
- Validate that no exact duplicates remain after processing.

Near-duplicates and partial duplicates are outside the scope of automatic removal.

---

## 5. Invalid and Anomalous Values

Values that violate established business rules must be identified and handled explicitly.

### 5.1 `person_age`

Implausible ages must be detected through business-rule validation.

The specific acceptable range will be defined as an explicit preprocessing rule.

Invalid values must not be silently retained or arbitrarily clipped.

---

### 5.2 `person_emp_length`

Employment length must be validated against business constraints and its relationship with `person_age`.

Values such as `123` years are considered invalid.

Invalid employment-length values require a defined treatment rather than automatic clipping.

---

### 5.3 `person_income`

Extreme income values must not be removed solely because they are statistical outliers.

The preprocessing pipeline should distinguish between:

- Valid high-income observations
- Confirmed invalid values
- Values requiring further investigation

Only confirmed invalid values should be subject to corrective treatment.

---

### 5.4 `loan_percent_income`

Consistency with related financial variables should be validated.

The feature must not be automatically recalculated or overwritten until its source definition has been established.

---

## 6. Missing-Value Treatment

Missing values exist in:

- `loan_int_rate`
- `person_emp_length`

Missing-value treatment will be defined according to the semantic role of each feature and the requirements of the downstream model.

Possible treatments include:

- Imputation
- Missing-value indicators
- Model-native missing-value handling
- Record removal when justified

The chosen method must be documented and reproducible.

The target variable `loan_status` must never be imputed.

Missing-value treatment must be performed without using information from the validation or test datasets to determine training-time imputation parameters.

---

## 7. Post-Preprocessing Validation

After preprocessing, the resulting curated dataset must be validated.

At minimum, the following checks must be performed:

- Exact duplicates have been removed.
- Invalid business-rule values have been handled.
- Missing values have received their defined treatment.
- Categorical values remain within the expected domain.
- `loan_status` contains only valid target values.
- Required columns and data types are preserved.
- No unintended records have been removed.
- No unintended feature values have been modified.

The final validation establishes that the preprocessing process produced a consistent curated dataset suitable for downstream data integration and machine learning.

The preprocessing workflow is therefore:

```
Raw Domain Data
    ↓
Preprocessing
    ↓
Post-Processing Validation
    ↓
Curated Domain Data
```

Feature engineering begins only after this stage.