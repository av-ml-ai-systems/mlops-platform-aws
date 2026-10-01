# Orchestration Layer

## 1. Purpose

The Orchestration Layer coordinates the execution of the ML lifecycle.

Its responsibility is to control:

* Execution order
* Dependencies between stages
* Pipeline triggers
* Scheduling
* Failure handling
* Reproducibility

The orchestration layer coordinates existing platform components. It does not replace their responsibilities.

---

## 2. Position in the Architecture

The Orchestration Layer sits above the main ML platform components.

```text
                    ORCHESTRATION LAYER
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Processing        Training        Governance
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                      Deployment
                           │
                           ▼
                      Monitoring
```

---

## 3. What Is Orchestrated

The orchestration workflow coordinates the major stages of the ML lifecycle:

1. Data ingestion
2. Data validation
3. Data processing
4. Curated dataset validation
5. ML preprocessing
6. Model training
7. Model evaluation
8. Model registration
9. Model deployment
10. Monitoring

The orchestrator ensures that downstream stages execute only when their required upstream stages have completed successfully.

---

## 4. Pipeline Dependencies

A simplified dependency chain is:

```text
Data Ingestion
      │
      ▼
Source Validation
      │
      ▼
Data Processing
      │
      ▼
Curated Dataset Validation
      │
      ▼
ML Preprocessing
      │
      ▼
Model Training
      │
      ▼
Model Evaluation
      │
      ▼
Model Registration
      │
      ▼
Model Deployment
      │
      ▼
Monitoring
```

A failed validation or processing stage should prevent dependent stages from executing.

---

## 5. AWS Integration

The orchestration layer can coordinate AWS services such as:

* AWS Glue
* Amazon Athena
* SageMaker Processing
* SageMaker Training
* SageMaker Model Registry
* Deployment services
* Monitoring services

The orchestrator is responsible for coordinating these services rather than duplicating their functionality.

---

## 6. Reproducibility

Pipeline executions should be reproducible through controlled:

* Dataset versions
* Processing code versions
* Training code versions
* Configuration
* Model versions
* Pipeline definitions

Conceptually:

```text
Dataset Version
       +
Processing Version
       +
Training Version
       +
Configuration
       │
       ▼
Reproducible Pipeline Execution
```

---

## 7. Failure Handling

Pipeline failures should be explicit and traceable.

Examples include:

* Validation failure
* Processing failure
* Training failure
* Model evaluation failure
* Deployment failure

A downstream stage should not execute when a required upstream stage has failed.

```text
Stage
 │
 ▼
Success ───────► Continue
 │
 ▼
Failure
 │
 ├── Stop dependent stages
 ├── Record failure
 └── Investigate / retry
```

Retries should be controlled and should not create inconsistent or duplicated dataset or model artifacts.

---

## 8. Local-First and Ephemeral AWS Execution

The orchestration workflow should support local development and controlled AWS execution.

```text
Local Development
       │
       ▼
Local Validation
       │
       ▼
Terraform
       │
       ▼
Create AWS Resources
       │
       ▼
Execute Pipeline
       │
       ▼
Verify Results
       │
       ▼
Document Evidence
       │
       ▼
Destroy AWS Resources
```

The local project remains the primary reconstruction source for the orchestration environment.

---

## 9. Design Principles

The Orchestration Layer follows these principles:

### Explicit Dependencies

Each pipeline stage must have clearly defined inputs and outputs.

### Failure Isolation

A failed stage should prevent invalid downstream execution.

### Reproducibility

Pipeline execution should be traceable to specific dataset, code, configuration, and model versions.

### Idempotency

Repeated execution should not create unintended duplicate artifacts or inconsistent state.

### Separation of Responsibilities

The orchestrator coordinates services but does not duplicate their internal processing logic.

### Controlled Execution

AWS infrastructure may be created for execution and validation and destroyed afterward when persistence is not required.

---

## 10. Architectural Summary

The Orchestration Layer connects the platform components into a controlled ML lifecycle:

```text
                 ORCHESTRATION
                      │
                      ▼
              Data / Validation
                      │
                      ▼
                  Processing
                      │
                      ▼
                   Training
                      │
                      ▼
              Model Governance
                      │
                      ▼
                 Deployment
                      │
                      ▼
                 Monitoring
```

Its primary role is to provide **execution control, dependency management, failure handling, and reproducibility across the ML lifecycle**.
