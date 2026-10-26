# 05 — Hyperparameter Optimization

## 1. Purpose

Hyperparameter optimization (HPO) searches for model configurations that improve performance on a defined evaluation metric.

Unlike model parameters, which are learned during training, hyperparameters are configured before or during the training process. Examples include learning rate, tree depth, regularization strength, and the number of estimators.

Phase 03 will apply targeted optimization to a selected candidate rather than launching large, expensive searches without justification.

## 2. Optimization Workflow

```text id="d2fr8k"
Baseline Model
      |
      v
Evaluate on Validation Data
      |
      v
Define Search Space and Metric
      |
      v
Run Hyperparameter Search
      |
      v
Compare Configurations
      |
      v
Select Tuned Candidate
      |
      v
Final Test Evaluation
```

The search strategy, search space, evaluation metric, and stopping conditions should be defined before optimization begins.

## 3. Search Strategies

### Grid Search

Evaluates every specified combination of hyperparameter values.

- **Advantage:** Systematic and easy to understand.
- **Limitation:** Can become expensive as the number of parameters and values grows.

### Random Search

Samples configurations from defined distributions or ranges.

- **Advantage:** Explores broad spaces without testing every combination.
- **Limitation:** Does not necessarily focus subsequent trials on promising regions.

### Bayesian Optimization

Uses results from previous evaluations to guide the selection of subsequent configurations.

- **Advantage:** Can search efficiently when each training run is expensive.
- **Limitation:** Introduces additional search logic and may be less suitable for some highly parallel workloads.

No strategy is universally best. The choice depends on the search space, training cost, available resources, and optimization objective.

## 4. Amazon SageMaker Hyperparameter Tuning

SageMaker Hyperparameter Tuning Jobs automate the evaluation of candidate configurations.

A tuning job typically requires:

- A training job configuration.
- Hyperparameters and their search ranges.
- An objective metric to optimize.
- A maximum number of training jobs or another stopping limit.
- Relevant resource and execution settings.

SageMaker supports search strategies such as random and Bayesian optimization. Supported stopping and early-stopping capabilities depend on the selected configuration and training algorithm.

The objective metric must correspond to the model-selection goals defined in the evaluation strategy.

## 5. Preventing Leakage During Tuning

Hyperparameter tuning must not use test-set performance to guide the search.

- Train each configuration using the training partition.
- Compare configurations using validation results.
- Apply preprocessing without fitting transformations on validation or test data.
- Keep resampling restricted to training data.
- Reserve the test set for final evaluation after tuning and selection.

Repeatedly using test results to choose configurations compromises the independence of the final evaluation.

## 6. Controlled Optimization

Before launching HPO:

1. Establish a baseline result.
2. Identify the hyperparameters most likely to affect performance.
3. Define reasonable search ranges.
4. Select the objective metric and stopping limits.
5. Run a limited search and review the results.
6. Compare the tuned candidate against the baseline using consistent evaluation procedures.

Use local experiments when they are sufficient for understanding the search space. Use SageMaker HPO when managed execution and integration justify the additional infrastructure.

Avoid unnecessary parallelism, oversized search spaces, and repeated runs that do not answer a specific question.

## 7. Tracking and Reproducibility

Record:

- Search strategy and search-space definitions.
- Objective metric and stopping configuration.
- Tested hyperparameter values.
- Training and validation results.
- Dataset, code, and configuration versions.
- Job identifiers and required artifacts.

Use SageMaker Experiments to maintain the relationship between tuning trials and their results.

Preserve the selected configuration and the evidence supporting the decision.

## 8. Key Takeaways

HPO is a controlled search for better model configurations, not a substitute for good data preparation or evaluation.

Phase 03 will establish a baseline, optimize a selected candidate with a justified search space, track results, and compare the tuned model against the baseline. The reserved test set will remain isolated until final evaluation.

## 9. Interview Preparation

Be prepared to explain:

- What is the difference between model parameters and hyperparameters?
- How do Grid Search, Random Search, and Bayesian Optimization differ?
- What does SageMaker HPO automate?
- Why should tuning use validation data rather than the test set?
- How would you limit an HPO experiment's scope?
- How do you determine whether tuning actually improved the model?