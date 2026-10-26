# Model Registry and Governance

## 1. Purpose

This document explains how to version, evaluate, register, and govern trained models before they become candidates for deployment.

In Phase 03, Amazon SageMaker Model Registry will provide centralized model versioning and lifecycle management. The objective is to produce a validated, traceable, and approved model candidate for Phase 04.

**Registering a model does not automatically make it approved for production.**

## 2. Amazon SageMaker Model Registry

The SageMaker Model Registry organizes models into **model packages** and **model package groups**.

- **Model package group:** Groups versions of a model associated with the same model purpose or application.
- **Model package:** Represents a specific model version, including its artifacts, metadata, and evaluation information.
- **Model version:** Allows different trained candidates to be identified, compared, and managed independently.
- **Approval status:** Records whether a registered model version is pending approval, approved, or rejected.

For this project, the registry will preserve the selected candidate and its associated metadata so it can be retrieved and evaluated for deployment in Phase 04.

## 3. Model Lineage and Traceability

A registered model must be traceable to the data and workflow that produced it.

The following information should be captured whenever applicable:

- **Dataset:** Source dataset identifier and version from Phase 02.
- **Processing:** Processing configuration, transformation version, and processed-data references.
- **Code:** Git commit or another reliable code-version identifier.
- **Configuration:** Training parameters, feature configuration, and relevant settings.
- **Experiment:** SageMaker Experiments identifier and relevant trial information.
- **Evaluation:** Metrics, acceptance criteria, and candidate-selection decision.
- **Artifacts:** Model artifact location and references to supporting evaluation outputs.

This information enables the team to understand how a model was produced and investigate differences between versions.

A model artifact alone is insufficient for complete reproducibility: the relevant data references, code, configuration, and execution evidence must also be preserved.

## 4. Validation Gates and Acceptance Criteria

A validation gate prevents a candidate from advancing when it fails predefined requirements.

Validation should cover several dimensions:

| Validation area | Example checks |
|---|---|
| Data and lineage | Dataset version and processing information are identifiable. |
| Artifact integrity | Expected model artifacts exist and can be loaded. |
| Evaluation | Required metrics are present and meet defined thresholds. |
| Model quality | Performance is acceptable relative to the baseline and alternatives. |
| Reproducibility | Training configuration, code version, and experiment references are recorded. |
| Governance | Required metadata and evaluation evidence are available. |

Acceptance thresholds must be established from the dataset, class distribution, and business requirements rather than invented before inspecting the data.

For the classification task, the gate may evaluate a primary metric and supporting metrics, including the consequences of false positives and false negatives.

A candidate that fails a required check must not be approved. The failure should be recorded, investigated, and resolved before the candidate is reconsidered.

## 5. Registration vs. Approval

Model registration and model approval are separate lifecycle steps.

1. Train and evaluate a candidate.
2. Verify its artifacts, metadata, lineage, and evaluation results.
3. Register the candidate in SageMaker Model Registry.
4. Execute the defined validation and governance checks.
5. Approve or reject the registered version according to the acceptance criteria.

Registration provides versioning and traceability. Approval indicates that the candidate has satisfied the defined requirements for the next stage.

Approval does not, by itself, deploy a model or guarantee its performance in a live environment.

## 6. Persistence and Infrastructure Lifecycle

Model governance must remain reliable even when temporary AWS resources are removed.

The project should distinguish between:

- **Temporary resources:** Compute instances, training jobs, processing jobs, and other resources that can be removed after execution.
- **Persistent evidence:** Required model artifacts, registered model versions, experiment records, evaluation results, dataset references, and configuration/code identifiers.

Before cleaning up AWS infrastructure, verify which resources contain evidence needed for future reproduction, comparison, or deployment.

Use Terraform for infrastructure management where appropriate, and document significant architecture or lifecycle decisions in Architecture Decision Records (ADRs).

Resource cleanup must not unintentionally destroy the approved model candidate or the evidence needed to understand and reproduce it.

## 7. Engineering Principles

- Register only candidates with sufficient metadata and evaluation evidence.
- Preserve model versions instead of overwriting previous candidates.
- Keep approval criteria explicit, testable, and documented.
- Maintain traceability from the Phase 02 dataset to the registered model.
- Separate model training, evaluation, registration, approval, and deployment responsibilities.
- Preserve essential artifacts and experiment evidence during infrastructure cleanup.
- Avoid introducing deployment infrastructure into Phase 03; deployment belongs to Phase 04.

## 8. Key Takeaways

- SageMaker Model Registry provides centralized model versioning and lifecycle management.
- Model lineage connects a trained model to its dataset, processing workflow, code, configuration, experiment, and evaluation.
- Validation gates prevent candidates that fail required criteria from advancing.
- Registration and approval represent different stages of the model lifecycle.
- Persistent artifacts and evidence must survive the cleanup of temporary compute infrastructure.
- Phase 03 ends with an approved, traceable model candidate ready for Phase 04—not a deployed inference service.

## 9. Interview Preparation

Be prepared to explain:

- What problem does a model registry solve?
- What is the difference between a model package group and a model package?
- Why is model versioning important?
- How can a model be traced to its training dataset and code?
- What checks should a model validation gate perform?
- Why are registration and approval separate?
- How should model artifacts and experiment evidence be preserved during infrastructure cleanup?
- What additional validation is required before an approved model is deployed?