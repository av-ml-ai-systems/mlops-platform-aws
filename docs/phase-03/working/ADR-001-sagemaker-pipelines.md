# ADR-001: SageMaker Pipelines for Workflow Orchestration

**Status:** Accepted

### Context
Phase 03 requires an orchestrated, reproducible ML training workflow.

### Decision
Use Amazon SageMaker Pipelines to orchestrate processing, training, evaluation, and model registration steps.

### Alternatives
- AWS Step Functions.
- Apache Airflow.
- Manual job execution.

### Consequences
Provides native SageMaker integration, execution tracking, and pipeline reproducibility. Introduces dependency on AWS SageMaker services.