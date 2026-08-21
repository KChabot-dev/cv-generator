## Current Phase

Implementation — Application pipeline services.

## Completed

### Architecture and Design
- High-level CV generation pipeline
- Core data contracts
- Stable identifier strategy
- Missing-information handling
- Validation-gate architecture
- Evidence matching and claim-boundary design

### Project Bootstrap
- Python 3.13 project
- uv dependency management
- Pydantic v2
- pytest
- Ruff
- mypy
- src-layout package structure

### Domain Models
- `CandidateProfile`
  - canonical identity
  - education
  - experiences
  - languages
  - date precision and consistency validation
  - stable ID validation

- `JobSpec`
  - job metadata
  - structured requirements
  - requirement classifications
  - experience requirements
  - unique requirement IDs

- `EvidenceMap`
  - source provenance
  - evidence scenarios
  - scenario-to-requirement matching
  - capability assessment
  - requirement match and claim eligibility
  - unsupported-requirement safeguards
  - internal reference integrity

- `CVContentPlan`
  - application target
  - document strategy
  - section planning
  - planned content items
  - evidence traceability
  - claim boundaries
  - omission tracking
  - section and item consistency validation

- `CVDraft`
  - application reference
  - candidate header
  - professional summary
  - skills
  - experiences and bullets
  - education
  - publications
  - presentations
  - languages
  - claim provenance
  - canonical/evidence/mixed claim distinction
  - internal claim-reference validation

### Domain Testing
- Validation behavior
- Important failure modes
- Internal reference integrity
- JSON serialization/deserialization round trips
- Ruff, mypy, and pytest quality checks

### Cross-Model Validation
- `JobSpec` ↔ `EvidenceMap` requirement completeness and reference validation
- `EvidenceMap` ↔ `CVContentPlan` reference and evidence-alignment validation
- Claim-eligibility enforcement
- `CVContentPlan` ↔ `CVDraft` plan-reference and claim-boundary validation
- `CandidateProfile` ↔ `CVDraft` canonical-fact validation
- Structured `ValidationIssue` model
- `ValidationReport` aggregation
- Pipeline-wide validation gate
- Aggregate valid and invalid pipeline tests

### Intermediate Artifact Persistence
- Generic typed JSON save/load
- Automatic parent-directory creation
- Invalid JSON/schema handling
- Stable artifact directory layout
- Global `CandidateProfile` persistence
- Per-run `JobSpec`, `EvidenceMap`, `CVContentPlan`, `CVDraft`, and `ValidationReport`
- `ArtifactStore` facade
- Filesystem persistence tests
  
### Application Services — In Progress

Completed:
- Test factories for coherent pipeline artifacts
- Shared pytest `ArtifactStore` fixture
- AI-provider-independent application ports using `Protocol`
- Job analysis orchestration and persistence
- Evidence matching, validation, and persistence
- CV content planning, validation, and persistence
- CandidateProfile-to-CVContentPlan source reference validation
- 

Next:
- CV writing application service
- Draft validation and persistence
- End-to-end pipeline orchestration