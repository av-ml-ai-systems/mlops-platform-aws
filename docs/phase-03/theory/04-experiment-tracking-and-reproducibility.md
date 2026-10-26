# 04 — Experiment Tracking and Reproducibility

## 1. Purpose

Experiment tracking records how models are trained and evaluated so that results can be compared, explained, and reproduced.

Phase 03 will use **Amazon SageMaker Experiments** to organize training experiments and their associated parameters, metrics, artifacts, and execution metadata.

## 2. What Should Be Tracked?

Each meaningful experiment should capture:

- **Dataset:** Source dataset version and processing output references.
- **Code:** Git commit or other identifier for the training and processing code.
- **Configuration:** Model type, hyperparameters, preprocessing settings, and relevant execution parameters.
- **Metrics:** Training metrics and validation results used for comparison.
- **Artifacts:** Model artifacts, evaluation reports, and other required outputs.
- **Execution metadata:** Experiment identifiers, job names, timestamps, and relevant pipeline execution information.

Tracking these elements makes it possible to understand why two runs produced different results.

## 3. Amazon SageMaker Experiments

SageMaker Experiments provides AWS-native capabilities for organizing and tracking ML experiments.

Its concepts include:

- **Experiment:** Groups related model-development work.
- **Trial:** Represents a particular run or experimental configuration.
- **Trial components:** Capture individual activities or jobs associated with a trial, such as processing, training, or evaluation.

The implementation should associate each meaningful run with its relevant dataset, configuration, execution, metrics, and artifacts. The exact integration will depend on the SageMaker SDK and workflow architecture selected during implementation.

MLflow will not be implemented in this phase; it may be compared conceptually with SageMaker Experiments when discussing experiment-tracking approaches.

## 4. Reproducible Experiments

A reproducible experiment requires more than saving the trained model.

Preserve the information needed to reconstruct the run:

1. Identify the exact input dataset version.
2. Identify the processing and training code versions.
3. Preserve configuration and hyperparameters.
4. Record the relevant environment and dependency versions.
5. Capture execution identifiers, metrics, and required artifacts.
6. Document the evaluation procedure and selection decision.

The same inputs and configuration should support a repeatable workflow. Exact numerical results may vary because of hardware, parallel execution, nondeterministic operations, or algorithm-specific behavior.

## 5. Artifact Persistence and Infrastructure Lifecycle

Training compute resources may be temporary, but important experiment evidence must persist.

Separate:

- **Temporary resources:** Compute instances, processing environments, and other resources that can be removed after execution.
- **Persistent records and artifacts:** Experiment metadata, evaluation reports, required model artifacts, and approved model versions.

Store required artifacts in appropriate persistent locations, such as designated Amazon S3 paths, and preserve the references needed to retrieve them.

Before cleaning up AWS resources, verify which outputs must survive. Do not delete essential experiment evidence merely because the associated compute job has finished.

## 6. Comparing Experiments

Experiments should use consistent data partitions and evaluation procedures.

Record comparable metrics and configurations so that differences can be interpreted meaningfully. Avoid changing several experimental factors simultaneously when doing so would make the results difficult to explain.

Use validation results for candidate selection and tuning. Keep the test set isolated until final evaluation.

## 7. Engineering Principles

- Track dataset, code, configuration, and execution versions.
- Use SageMaker Experiments as the selected tracking solution.
- Automate metric and artifact capture where practical.
- Keep experiment records separate from temporary compute resources.
- Preserve traceability between processing, training, evaluation, and model registration.
- Avoid unnecessary experiments and repeated cloud execution.
- Test the tracking integration to ensure records are actually persisted.

## 8. Key Takeaways

Experiment tracking makes model development auditable and comparable. Reproducibility depends on preserving the relevant data, code, configuration, execution metadata, metrics, and artifacts.

SageMaker Experiments will provide the tracking foundation for Phase 03. Required records and model artifacts must remain accessible even after temporary infrastructure is removed.

## 9. Interview Preparation

Be prepared to explain:

- What information is required to reproduce a training run?
- How do SageMaker Experiments organize experiments and individual runs?
- Why is saving only the trained model insufficient?
- How do you preserve evidence after deleting temporary compute resources?
- How would you investigate a difference between two training runs?
- How does experiment tracking support model lineage and governance?