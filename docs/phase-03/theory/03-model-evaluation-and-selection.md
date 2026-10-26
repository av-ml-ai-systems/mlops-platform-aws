# 03 — Model Evaluation and Selection

## 1. Purpose

This document defines how Phase 03 evaluates candidate models, compares their performance, and selects a model for further optimization and approval.

Model selection must consider predictive performance, business requirements, model complexity, and reproducibility—not just a single metric.

## 2. Evaluation Workflow

```text
Trained Candidate Models
          |
          v
Evaluate on Validation Data
          |
          v
Compare Metrics and Business Trade-offs
          |
          v
Apply Acceptance Criteria
          |
          v
Select Candidate
          |
          v
Hyperparameter Optimization
          |
          v
Final Test Evaluation
          |
          v
Model Validation and Approval
```

The test set must remain isolated from model selection and hyperparameter tuning. After decisions are finalized, use it for the final performance assessment.

## 3. Classification Metrics

For a binary classification problem:

- **Accuracy:** Proportion of correct predictions. It can be misleading when classes are imbalanced.
- **Precision:** Among predicted positive cases, how many are actually positive?
- **Recall:** Among actual positive cases, how many does the model identify?
- **F1-score:** Harmonic mean of precision and recall.
- **ROC-AUC:** Measures how well the model ranks positive cases above negative cases across classification thresholds.
- **PR-AUC:** Summarizes the precision-recall trade-off across thresholds and is particularly informative for many imbalanced classification problems.

Useful supporting tools include the confusion matrix, ROC curve, and Precision–Recall curve.

### Choosing metrics

Metric selection depends on the business problem and class distribution.

For example, in loan-risk prediction, missing a genuinely high-risk applicant and incorrectly classifying a low-risk applicant can have different consequences. The appropriate balance between precision and recall must reflect those consequences.

Define a **primary metric** and supporting metrics before comparing candidates. Do not automatically choose accuracy or assume that one metric suits every problem.

## 4. Class Imbalance and Thresholds

When one class is much less frequent than another, a model may achieve high accuracy while performing poorly on the minority class.

Possible approaches include:

- Class weighting.
- Oversampling or undersampling the training data.
- Adjusting the classification threshold.

These techniques should be evaluated against the chosen business objective. Resampling must occur only within training data, never before the dataset split or on validation and test data.

Threshold selection must use validation data, not the test set.

## 5. Candidate Model Comparison

Start with a simple baseline and a small, meaningful set of candidate models.

Compare candidates using:

- The same data partitions and evaluation procedure.
- The primary and supporting metrics.
- False-positive and false-negative trade-offs.
- Training and inference complexity.
- Reproducibility and operational requirements.

A more complex model is not automatically preferable to a simpler model with comparable performance.

Record each candidate's configuration, metrics, dataset version, and experiment identifier so that the comparison can be reproduced.

## 6. Acceptance Criteria and Selection

Define acceptance criteria before final selection. They may include:

- Minimum required predictive performance.
- Acceptable precision or recall.
- Business constraints on false positives and false negatives.
- Operational constraints, such as inference latency or model complexity.

Select the candidate using validation results and the documented criteria. If no candidate meets the requirements, investigate the shortcomings instead of approving a model by default.

After selection and any subsequent optimization, evaluate the finalized candidate on the reserved test set. Preserve the results as evidence for the model's validation and approval process.

## 7. Engineering Principles

- Use metrics appropriate to the problem and class distribution.
- Prevent leakage during training, tuning, and evaluation.
- Keep the test set isolated until final evaluation.
- Track evaluation results and candidate configurations.
- Make selection criteria explicit and reproducible.
- Separate model selection from model approval.

## 8. Key Takeaways

Model evaluation is a decision process, not merely a metric calculation. Reliable selection combines appropriate metrics, business trade-offs, consistent experiments, and explicit acceptance criteria.

Validation data supports model selection and tuning; the test set provides the final performance assessment. The selected model must still pass the required validation and governance gates before approval.

## 9. Interview Preparation

Be prepared to explain:

- Why can accuracy be misleading for imbalanced data?
- When would you prioritize precision over recall, or recall over precision?
- What is the difference between ROC-AUC and PR-AUC?
- Why must the test set remain isolated during tuning?
- How do you define model acceptance criteria?
- Why might a simpler model be selected over a more complex candidate?