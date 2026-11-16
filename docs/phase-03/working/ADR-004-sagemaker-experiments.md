# ADR-004: SageMaker Experiments for Experiment Tracking

**Status:** Accepted

### Context
Phase 03 requires traceability and comparison of training experiments.

### Decision
Use Amazon SageMaker Experiments to organize and track experiment runs, parameters, metrics, and execution metadata.

### Alternatives
- MLflow.
- Custom tracking implementation.
- Manual experiment records.

### Consequences
Provides integration with SageMaker training workflows. Creates dependency on AWS-managed experiment tracking capabilities.