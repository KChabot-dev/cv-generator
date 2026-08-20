## Current Phase

Implementation — typed domain models and validation.

### Completed

* Python project bootstrap and reproducible development environment
* pytest, Ruff, and mypy quality tooling
* `CandidateProfile` domain model and validation
* reusable strict `DomainModel`
* partial career-date representation
* JSON serialization/deserialization for candidate data
* JSON Schema generation from Pydantic models
* `JobMetadata`
* structured `JobRequirement`
* experience qualifiers and contexts
* requirement source grounding
* `JobSpec`
* stable requirement-ID validation
* JSON round-trip validation for `JobSpec`

### Next

* Implement `EvidenceMap`
* represent requirement-to-evidence relationships and provenance
* define evidence strength and limitations
* add validation for evidence mappings
* continue building the remaining pipeline domain contracts
