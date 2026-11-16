# Phase 03 — Summary and Continuity

## 1. Phase Objective

Develop a reproducible, testable, and auditable ML training and model management system using AWS managed services.

The phase covers data preparation, feature engineering, training, experiment tracking, model evaluation, hyperparameter optimization, model registry, approval, and end-to-end validation.

The initial implementation focuses on classical Machine Learning and CPU-based execution.

## 2. Previous Phase Context

- **Phase 00 — Foundations:** Established the theoretical foundations of ML engineering, MLOps, software engineering, cloud computing, and AI systems.
- **Phase 01 — Data Engineering and Feature Platform:** Developed local data processing, domain separation, feature engineering, validation, and dataset versioning.
- **Phase 02 — Data Foundation and AWS Integration:** Established AWS infrastructure using Terraform, Amazon S3, AWS Glue, Glue Data Catalog, Athena, IAM, and CloudWatch.

Phase 03 builds upon these foundations rather than replacing them.

## 3. Dataset and Existing Implementation

The project uses the Kaggle Credit Risk dataset, published as a curated loan risk dataset.

- Target: `loan_outcome`.
- `0`: Non-default.
- `1`: Default.
- Approximately 32,581 records and 14 columns in the previously inspected curated dataset.

Phase 01 contains local data engineering and feature engineering components.

Phase 02 established the AWS data lake and Glue-based publication workflow.

Important consideration: Some legacy feature definitions differ from the curated dataset schema. Their compatibility must be evaluated during M2 rather than assumed.

## 4. Initial AWS Architecture

The proposed architecture uses:

| Component | Responsibility |
|---|---|
| Amazon S3 | Dataset and model artifact storage |
| SageMaker Processing | Data preparation and evaluation |
| SageMaker Training | Model training |
| SageMaker Pipelines | Workflow orchestration |
| SageMaker Experiments | Experiment tracking |
| SageMaker Model Registry | Model versioning and approval |
| Terraform | Infrastructure provisioning |
| CloudWatch | Logs and monitoring |

The architecture is an initial design and must be validated during implementation.

## 5. Milestone 1 — Completed Design

M1 established the theoretical, methodological, and architectural foundations.

### Training and Evaluation

- Default-class recall is the primary evaluation metric.
- Default-class precision is secondary.
- PR-AUC, F1, ROC-AUC, and confusion matrix provide supporting evaluation.
- Train, validation, and holdout test datasets will be used.
- Baseline and candidate models will be compared before selection.
- Provisional performance targets are hypotheses, not approved business requirements.

### Reproducibility and Traceability

Training executions must record dataset versions, configurations, random seeds, software versions, source code references, metrics, and model artifacts.

### Infrastructure

Terraform will manage AWS infrastructure. Temporary resources must be cleaned up after execution, while preserving required artifacts and evidence.

### Architectural Decisions

Four initial ADRs were created:

- ADR-001: SageMaker Pipelines for workflow orchestration.
- ADR-002: SageMaker Processing and Training Jobs.
- ADR-003: Amazon S3 for artifact storage.
- ADR-004: SageMaker Experiments for experiment tracking.

These decisions may be revised if implementation reveals technical constraints.

## 6. Main M1 Documents

Location: `Phase 03/Working/`, except the six theory documents.

**Theory:**
- Six training and MLOps theory documents covering training workflows, data preparation, evaluation, reproducibility, HPO, and model governance.

**Working:**
- `training_and_evaluation_strategy.md`
- `aws_training_architecture.md`
- `model_artifacts_and_experiment_lineage.md`
- `training_reproducibility_strategy.md`
- `aws_infrastructure_lifecycle.md`
- `ADR-001-sagemaker-pipelines.md`
- `ADR-002-sagemaker-processing-training-jobs.md`
- `ADR-003-s3-artifact-storage.md`
- `ADR-004-sagemaker-experiments.md`
- `phase_03_initial_architecture_and_implementation_plan.md`
- `phase_03_summary_and_continuity.md`

## 7. Phase 03 Milestones

| Milestone | Objective |
|---|---|
| M1 | Theory review and initial architecture design — completed |
| M2 | EDA, data preparation, and feature engineering design |
| M3 | Processing and feature engineering implementation |
| M4 | Reproducible training pipeline |
| M5 | Candidate training and experiment tracking |
| M6 | Model evaluation and selection |
| M7 | Hyperparameter optimization |
| M8 | Model Registry and approval gate |
| M9 | End-to-end evaluation |

## 8. Working Methodology

Follow an incremental, module-by-module engineering workflow:

1. Understand the technical requirement.
2. Explain the relevant concepts and architectural decisions.
3. Design the component.
4. Implement one module at a time.
5. Provide the complete updated module.
6. Validate only that module using specific commands.
7. Wait for actual execution results.
8. Resolve failures before continuing.
9. Update project evolution and milestone tracking.

Use VS Code, Windows, PowerShell, and the existing local development environment.

## 9. Technical and Cost Constraints

- Prefer CPU-based implementations initially.
- Consider the available computer resources (16 GB RAM).
- Avoid unnecessary Docker or infrastructure complexity.
- Use AWS managed services where appropriate.
- Provision only the resources required for the current task.
- Monitor AWS costs carefully.
- Preserve outputs before destroying temporary infrastructure.
- Never assume that AWS resources have been deleted without verification.

## 10. AI Collaboration Strategy

**Google AI Studio:**
Primary workspace for module implementation, code generation, testing, debugging, and technical development.

**ChatGPT:**
Independent architecture review, technical explanations, documentation, milestone planning, and evaluation of implementation decisions.

Both platforms must follow the same project documentation, repository state, and technical decisions.

The GitHub repository and maintained project documentation are the sources of truth.

## 11. Current Status and Next Action

**Phase:** 03 — Training Systems and Model Management.

**Current status:** Milestone 1 completed.

**Next:** Milestone 2 — EDA, Data Preparation, and Feature Engineering Design.

The first activity is to inspect the existing curated dataset, its schema, quality, distributions, and compatibility with the proposed feature engineering approach.

No implementation should begin until the relevant data preparation and feature engineering decisions have been established.