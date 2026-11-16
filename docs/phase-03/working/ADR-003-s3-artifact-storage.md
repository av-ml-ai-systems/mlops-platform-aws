# ADR-003: Amazon S3 for Dataset and Model Artifact Storage

**Status:** Accepted

### Context
Training requires persistent storage for datasets, processing outputs, evaluation results, and model artifacts.

### Decision
Use Amazon S3 as the central storage layer, following the logical organization defined in the artifact lineage architecture.

### Alternatives
- EBS volumes.
- EFS.
- Local filesystem storage.

### Consequences
Provides durable, scalable storage and integration with AWS ML services. Requires lifecycle policies, access controls, and cost management.