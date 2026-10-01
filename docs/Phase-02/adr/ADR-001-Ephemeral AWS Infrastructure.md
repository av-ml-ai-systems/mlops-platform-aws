# ADR-001 — Ephemeral AWS Infrastructure

## Status

Accepted

## Context

Phase 02 uses AWS to validate an enterprise-oriented ML platform architecture.

The project is being developed in a cost-conscious, local-first environment. Keeping AWS resources permanently deployed would create unnecessary ongoing costs and would make the learning environment unnecessarily dependent on persistent cloud state.

The project must therefore remain reconstructable without relying on currently deployed AWS resources.

## Decision

AWS infrastructure will be **ephemeral by default** during Phase 02 development and learning.

The standard operating lifecycle is:

```text
Local Project
    ↓
Terraform
    ↓
Create AWS
    ↓
Verify
    ↓
Inspect
    ↓
Capture Evidence
    ↓
Document
    ↓
Destroy AWS
    ↓
Recreate Later
```

Terraform configuration remains inside the project repository and is version-controlled with the rest of the platform.

The local project is the primary reconstruction source.

Git provides version history, while GitHub provides remote repository storage and backup.

AWS is the temporary execution and validation environment.

## Consequences

### Positive

* Reduces unnecessary AWS costs.
* Forces infrastructure reproducibility.
* Makes infrastructure reconstruction a deliberate engineering capability.
* Keeps the project independent from persistent cloud state.
* Encourages Infrastructure as Code.
* Makes resource ownership and lifecycle explicit.

### Negative

* AWS resources must be recreated when needed.
* Validation sessions require provisioning time.
* Persistent cloud state cannot be assumed between sessions.
* Destruction requires careful handling of resources such as versioned S3 objects.

## Scope

This decision describes the Phase 02 learning/development deployment strategy.

It does not imply that a production enterprise platform should destroy its data-storage resources after every development session.

The logical architecture and the deployment lifecycle are separate concerns.

## Result

The project must remain capable of reconstructing the AWS environment from the local repository without depending on an existing AWS deployment.
