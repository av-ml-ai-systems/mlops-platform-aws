# Phase 00 — Evolution

## Purpose

This document records the significant changes and decisions that shaped Phase 00 of the MLOps Engineer / AWS Roadmap. It is intended to preserve the evolution of the project rather than document every individual implementation step.

---

## Initial Direction

Phase 00 began as the foundational stage of the MLOps roadmap.

The initial objective was to establish the conceptual foundation required to transition from traditional Data Science workflows toward production-oriented ML engineering and MLOps.

The learning focus was expanded from:

```text
Data → Model → Prediction
```

toward the broader ML lifecycle:

```text
Data
  ↓
Data Engineering
  ↓
Data Quality
  ↓
Training
  ↓
Model Management
  ↓
Deployment
  ↓
Monitoring
  ↓
Automation
```

This became the conceptual foundation for the subsequent phases.

---

## Evolution Toward an AWS-First Strategy

The roadmap was then structured around an AWS-first cloud strategy.

The objective was not simply to learn individual AWS services, but to understand how managed cloud services fit into an end-to-end MLOps architecture.

The project therefore began incorporating:

* Amazon S3
* AWS IAM
* AWS CLI
* Terraform
* Infrastructure as Code
* cloud-native architecture
* reproducibility
* Git/GitHub workflows
* automated engineering checks

The emphasis shifted from learning services independently toward understanding their role within an ML platform.

---

## Local-First and Cloud-Native Development

A local-first development approach was established.

The project would be developed and validated locally where practical, while AWS would be used to understand and validate cloud infrastructure and managed services.

This established an important principle for the later phases:

> Cloud services should add architectural value rather than being introduced simply for the sake of using the cloud.

This approach also supported cost-conscious experimentation.

---

## Infrastructure and Engineering Foundation

Phase 00 expanded from conceptual MLOps learning into practical infrastructure work.

The following capabilities were established and validated:

* AWS account and IAM fundamentals
* MFA and secure AWS access
* AWS CLI configuration
* Terraform installation and configuration
* AWS provider configuration
* Terraform validation
* S3 infrastructure lifecycle
* infrastructure creation and destruction
* resource cleanup
* Git/GitHub workflow
* pre-commit verification
* Infrastructure as Code principles
* AWS architecture fundamentals
* CloudFormation concepts

A complete S3 create → verify → destroy lifecycle was used to establish the basic Infrastructure as Code workflow.

---

## Documentation and Architecture

The project began formalizing engineering decisions and architecture through documentation.

This included:

* engineering principles
* Python packaging workflow
* architecture documentation
* AWS infrastructure concepts
* Terraform/IaC concepts
* ADR-based documentation for significant decisions
* interview-oriented documentation of the engineering concepts learned

A visual architecture representation was also introduced to make the relationship between infrastructure components and the broader ML platform easier to reason about.

---

## AWS Account Constraint

The practical AWS work was ultimately constrained by the availability of the AWS Free Tier.

The AWS account's free-tier period expired, so continued AWS experimentation could not proceed under the original free-cost assumptions.

As a result, Phase 00's theoretical AWS foundation remained complete, while further cloud experimentation was deferred until it could be performed under an appropriate cost-conscious strategy.

This constraint influenced the roadmap's later emphasis on:

```text
Local Development
        ↓
Local Validation
        ↓
Targeted Cloud Validation
        ↓
Resource Cleanup
```

rather than maintaining unnecessary cloud infrastructure.

---

## Phase 00 Resulting Foundation

By the end of Phase 00, the roadmap had evolved from a general MLOps learning plan into an engineering-oriented, AWS-first ML platform roadmap.

The resulting foundation established:

```text
MLOps Fundamentals
        ↓
AWS Architecture
        ↓
Infrastructure as Code
        ↓
Terraform
        ↓
S3
        ↓
Git / Engineering Practices
        ↓
Reproducible Cloud Infrastructure
```

This foundation became the basis for Phase 01 and the subsequent ML data platform work.

---

## Key Evolution Principles

The most important principles established during Phase 00 were:

* MLOps is an end-to-end engineering lifecycle, not only model deployment.
* Architecture and reproducibility are as important as model development.
* Cloud services should have a clear architectural purpose.
* Infrastructure should be reproducible through Infrastructure as Code.
* Local development and cloud execution should be complementary.
* Cloud resources should be created deliberately and cleaned up when no longer required.
* Significant architectural decisions should be documented rather than retained only in conversation.
