# 02 — Data Preparation and Leakage Prevention

## 1. Purpose

This document defines how Phase 03 prepares validated, versioned data for model training.

The goal is to produce reliable model inputs through data quality validation, exploratory data analysis (EDA), feature engineering, and appropriate dataset splitting while preserving reproducibility and preventing data leakage.

The Phase 02 curated dataset remains immutable. Phase 03 applies training-specific transformations without repeating upstream data curation.

## 2. Data Preparation Workflow

The initial workflow is:

```text
Phase 02 Versioned Dataset
          |
          v
Schema and Data Quality Validation
          |
          v
Exploratory Data Analysis (EDA)
          |
          v
Train / Validation / Test Split
          |
          v
Fit Transformations on Training Data
          |
          v
Transform Validation and Test Data
          |
          v
Validate Model-Ready Datasets
          |
          v
Training Workflow
```

The exact sequence of operations may vary according to the dataset and model. In particular, transformations that learn information from data must respect the splitting strategy.

## 3. Dataset Inspection and EDA

Before implementing transformations, understand the dataset's structure, quality, target variable, and statistical characteristics.

### Structural validation

Check:

- Required columns and expected schema.
- Data types and feature availability.
- Missing or unexpected columns.
- Target variable existence and valid values.
- Duplicate rows and, where relevant, duplicate entity identifiers.

### Data quality and consistency

Investigate:

- Missing-value frequency and patterns.
- Invalid values and outliers.
- Class distribution and imbalance.
- Duplicate records and uniqueness constraints.
- Cross-column relationships and business rules.
- Statistical distributions and unusual values.

A detected anomaly does not automatically justify removing or modifying data. Establish whether it is an error, a legitimate rare observation, or a meaningful business case.

### Dataset versioning

Record the source dataset version and relevant metadata. Preserve the connection between the original dataset, preprocessing configuration, resulting datasets, and training runs.

## 4. Feature Engineering

Feature engineering transforms available data into useful model inputs.

Common operations include:

- Imputation of missing values.
- Encoding categorical variables.
- Scaling or normalization where appropriate.
- Feature creation and transformation.
- Feature selection where justified.
- Handling invalid values and defining consistent feature types.

### Model-specific preprocessing

Different algorithms may require different preprocessing.

For example, logistic regression may benefit from feature scaling, while tree-based algorithms generally do not require it. Do not apply transformations indiscriminately to every candidate model.

### Preventing feature leakage

Every feature must be based on information legitimately available at the time a prediction would be made.

Avoid features that directly reveal the target, contain information recorded only after the outcome, or indirectly encode information from validation or test observations.

Feature engineering should be implemented in reusable, testable Python modules. Keep transformation logic separate from orchestration and model-training code.

## 5. Train, Validation, and Test Splitting

The datasets serve different purposes:

| Dataset | Purpose |
|---|---|
| Training | Fit model parameters and learned preprocessing transformations |
| Validation | Compare candidates, tune hyperparameters, and select models |
| Test | Estimate final performance after model and configuration decisions are complete |

### Choosing a splitting strategy

The appropriate strategy depends on the data-generating process:

- **Stratified split:** Useful for independent classification observations when preserving class proportions matters.
- **Group split:** Appropriate when related records share an entity, customer, patient, or other grouping that must not cross partitions.
- **Time-based split:** Appropriate when temporal ordering matters and future information must not influence past predictions.
- **Cross-validation:** Useful for estimating model performance or comparing candidates when the data and computational budget support it.

Do not automatically use a random split. First inspect the dataset and identify dependencies between observations.

The final splitting strategy must be documented and reproducible.

## 6. Data Leakage Prevention

Data leakage occurs when information unavailable to a model at prediction time influences training or evaluation, resulting in misleading performance estimates.

### Common leakage sources

- Target information included directly or indirectly in features.
- Features containing future information.
- Duplicate or closely related observations across partitions.
- Preprocessing fitted using the entire dataset before splitting.
- Resampling performed before splitting.
- Repeatedly using test results to select models or tune hyperparameters.

### Correct preprocessing sequence

1. Split the data using the selected strategy.
2. Fit learned preprocessing transformations using training data only.
3. Apply the fitted transformations to validation and test data without refitting.
4. Apply resampling or similar imbalance-handling techniques only to training data, if justified.
5. Preserve the natural distribution of validation and test data.
6. Keep the test set isolated from model selection and hyperparameter tuning.

A scikit-learn `Pipeline` can help ensure that learned preprocessing is fitted correctly during model training and cross-validation.

## 7. Training-Serving Feature Consistency

Training-serving skew occurs when features are calculated differently during model training and inference.

Differences in missing-value handling, encoding, scaling, feature definitions, or input formats can cause production predictions to behave differently from offline evaluation.

To reduce this risk:

- Reuse the same versioned transformation logic wherever practical.
- Preserve feature definitions and preprocessing configuration.
- Validate inference inputs against the expected schema.
- Test transformations with representative inputs.
- Avoid duplicating feature logic independently across training and inference systems.

Feature Store implementation is outside Phase 03 scope and belongs to Phase 04. However, Phase 03 must establish the feature definitions and transformation discipline required for future consistency.

## 8. Automated Validation and Quality Gates

Data validation should be automated and tested rather than performed only through manual inspection.

Useful checks include:

- Required columns and data types.
- Valid target values.
- Missing-value and duplicate thresholds.
- Domain and business-rule constraints.
- Expected feature formats.
- Partition integrity and leakage-related checks.
- Output schema and consistency after transformations.

Define explicit pass/fail criteria. If critical checks fail, stop the workflow and report the reason rather than silently continuing with unsuitable data.

Validation results should be traceable to the dataset version, processing configuration, and execution that produced them.

## 9. Engineering Principles

- Preserve the original Phase 02 dataset.
- Develop preprocessing logic locally before managed cloud execution.
- Separate data validation, feature engineering, and training responsibilities.
- Use modular, testable transformations and configuration-driven rules.
- Record dataset versions, transformation versions, and relevant metadata.
- Validate intermediate outputs before training.
- Avoid unnecessary transformations and repeated data preparation.
- Preserve reproducibility without retaining unnecessary temporary resources.

## 10. Key Takeaways

Reliable training data requires more than a valid schema. It must satisfy structural, quality, consistency, and business requirements while representing information legitimately available at prediction time.

The splitting strategy must reflect the dataset's dependencies. Learned transformations must be fitted only on training data, and validation and test sets must remain isolated from training-only resampling and model-selection decisions.

Feature engineering, automated quality gates, and traceability are essential parts of the training workflow—not optional cleanup tasks.

## 11. Interview Preparation

Be prepared to explain:

- How do schema validation and data quality validation differ?
- How would you choose between stratified, group, and time-based splitting?
- Why can fitting a scaler before splitting cause leakage?
- Why must resampling occur only on training data?
- How do you prevent target leakage?
- What causes training-serving skew?
- How would you test and version feature engineering transformations?
- How should a pipeline respond when a critical data quality check fails?