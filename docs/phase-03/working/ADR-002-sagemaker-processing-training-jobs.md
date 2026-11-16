# ADR-002: SageMaker Processing and Training Jobs

**Status:** Accepted

### Context
The training workflow requires scalable and isolated execution environments.

### Decision
Use SageMaker Processing Jobs for data preparation and evaluation, and SageMaker Training Jobs for model training.

### Alternatives
- Local execution.
- Custom EC2 instances.
- AWS Batch.

### Consequences
Provides managed execution environments and integration with S3 and SageMaker Pipelines. Requires appropriate instance selection and cost management.