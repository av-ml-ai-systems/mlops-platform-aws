# 01 — Training Workflows

## 1. Purpose

This document establishes the architecture and core concepts for building reproducible, maintainable ML training workflows in Phase 03.

The objective is to transform a validated, versioned Phase 02 dataset into a trained, evaluated, and traceable model candidate using local development and AWS-managed services where justified.

## 2. Training Workflow Architecture

The initial workflow follows this sequence:

```text
Phase 02 Versioned Dataset
          |
          v
Dataset and Schema Validation
          |
          v
SageMaker Processing Job
(Training-Specific Transformations)
          |
          v
Training / Validation / Test Data
          |
          v
SageMaker Pipeline
          |
          v
Candidate Training Jobs
          |
          v
Model Evaluation
          |
          v
Hyperparameter Optimization
          |
          v
Model Validation Gate
          |
          v
SageMaker Model Registry
          |
          v
Approved Model Candidate
```

The workflow will be refined after inspecting the actual Phase 02 dataset. Not every step must become a separate AWS job if that would introduce unnecessary complexity.

## 3. SageMaker Processing Jobs

A SageMaker Processing Job executes a data-processing or evaluation workload in a managed environment.

Typical responsibilities include:

- Validating dataset structure, data types, and required columns.
- Applying training-specific cleaning and transformations.
- Engineering or selecting features.
- Preparing model-ready input data.
- Producing identifiable outputs and validation reports.

### Processing Job components

A Processing Job typically uses:

- **Processing code:** Python scripts or a supported processing framework.
- **Container environment:** Runtime and required dependencies.
- **Inputs:** Dataset files and configuration, commonly supplied through Amazon S3.
- **Compute resources:** Selected according to workload requirements.
- **Outputs:** Processed datasets, reports, and other artifacts persisted to designated destinations.

### Local versus managed processing

Develop and test processing logic locally first. Use SageMaker Processing Jobs when managed execution, AWS integration, or execution consistency provides sufficient value.

Avoid repeating Phase 02 data curation. Processing in Phase 03 should focus on training-specific transformations.

## 4. Separation of Processing and Training

Processing and training have different responsibilities.

| Processing | Training |
|---|---|
| Validates and transforms input data | Learns model parameters |
| Creates model-ready datasets | Produces a trained model |
| Produces data-quality evidence | Produces training metrics and model artifacts |
| Can be tested independently | Can be executed with different model configurations |

This separation improves testing, reproducibility, debugging, and independent execution.

Some validation may occur before processing, during processing, and again before training. A failed quality gate should prevent unsuitable data from reaching the training step.

## 5. SageMaker Training Jobs

A SageMaker Training Job executes model-training code in a managed compute environment.

Its principal inputs include:

- Training and validation data.
- Training script and dependencies.
- Model configuration and hyperparameters.
- Compute configuration.

Its outputs typically include:

- Trained model artifacts.
- Training metrics and logs.
- Execution metadata needed for traceability.

The training code should be reproducible given the same dataset version, code version, configuration, and relevant execution settings. Exact numerical reproducibility may still depend on the algorithm, hardware, and random operations.

## 6. SageMaker Pipelines

SageMaker Pipelines orchestrates connected ML workflow steps and their dependencies.

A pipeline can coordinate processing, training, evaluation, conditional validation, and model registration.

Important design principles:

- Define explicit inputs, outputs, parameters, and dependencies.
- Make failures visible and prevent invalid candidates from advancing.
- Avoid unnecessary steps and repeated processing.
- Preserve the relationship between dataset versions, code, configurations, and results.
- Separate temporary compute resources from artifacts and records that must persist.

A pipeline is not a replacement for well-designed Python modules. The code should remain modular and testable independently of orchestration.

## 7. Reproducibility and Traceability

Every meaningful training run should identify:

- Source dataset version.
- Processing code and configuration.
- Training code version.
- Model type and hyperparameters.
- Evaluation metrics and acceptance criteria.
- Pipeline and job execution identifiers.
- Locations of required outputs and artifacts.

Amazon SageMaker Experiments will be used to organize experiment tracking. Required evidence and approved model artifacts must remain available after temporary compute resources are removed.

Versioned inputs and configuration should allow the workflow to be reconstructed without repeating upstream data preparation.

## 8. Validation Gates

Validation gates determine whether workflow outputs may proceed to the next stage.

Examples include:

- Dataset validation before training.
- Evaluation-metric checks after training.
- Acceptance criteria before model registration or approval.

A gate must have explicit criteria and observable results. A job completing successfully does not automatically mean its dataset or model is acceptable.

Model registration and model approval are also distinct: registration records a model version; approval indicates that it has satisfied the required governance criteria.

## 9. Engineering and Infrastructure Principles

- Develop and test locally before using managed AWS compute.
- Use modular Python code, configuration, logging, and automated tests.
- Use Terraform for infrastructure as appropriate.
- Identify which resources are temporary and which artifacts or records must persist.
- Avoid unnecessary parallel jobs, repeated processing, and oversized workloads.
- Clean up temporary AWS resources without deleting required experiment evidence or approved artifacts.
- Record significant architectural decisions in ADRs.

## 10. Key Takeaways

A reliable training workflow separates data processing, model training, evaluation, and governance while connecting them through explicit, reproducible steps.

SageMaker Processing Jobs prepare training-specific data; Training Jobs train candidate models; Pipelines orchestrate the workflow; Experiments record runs; and the Model Registry manages model versions and approval status.

The implementation must be guided by the actual Phase 02 dataset and validated incrementally. The goal is a reproducible, traceable workflow—not the maximum number of AWS services or pipeline steps.

## 11. Interview Preparation

Be prepared to explain:

- Why separate processing from training?
- When would you use local processing versus a SageMaker Processing Job?
- What does SageMaker Pipelines orchestrate?
- How do you reproduce a training run?
- How do you prevent invalid data or models from advancing?
- What is the difference between model registration and approval?
- How do you preserve experiment evidence while cleaning up temporary infrastructure?