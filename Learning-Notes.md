# Learning Notes

## Python Project Environment and Tooling

- An IDE such as VS Code or PyCharm is an interface over the underlying development tools; the project should remain usable independently of the IDE.
- A virtual environment provides an isolated Python runtime context for a project.
- `pyproject.toml` declares project metadata, Python requirements, dependencies, build configuration, and tool configuration.
- `uv` resolves and manages project dependencies and environments.
- `uv.lock` records the resolved dependency solution for reproducibility.
- Runtime dependencies and development dependencies serve different purposes.
- pytest tests software behavior.
- Ruff performs linting/formatting and other code-quality checks.
- mypy performs static type checking.
- CI can later automate these checks whenever code changes are pushed.

## Domain Models, Validation, and Testing

- Pydantic models define both the structure of domain data and runtime validation rules.
- `model_validator(mode="after")` is useful for invariants involving multiple fields.
- Generic reusable logic should be separated from domain-specific business rules when appropriate.
- Unit tests should protect meaningful behavior, edge cases, and regressions rather than test library behavior unnecessarily.
- Tests remain part of the codebase and help detect regressions during refactoring.
- pytest, Ruff, and mypy cover different concerns:
  - pytest: behavioral correctness
  - Ruff: code quality and consistency
  - mypy: static type consistency
- A failing test during the `EducationRecord` refactor successfully detected that an existing business rule had been removed.

## JobSpec Domain Modelling

* Domain models should describe the object itself independently from later decisions about the candidate. `JobSpec` describes the employer and position; candidate fit is evaluated later.
* Enums constrain controlled vocabularies such as work arrangement, employment type, requirement category, priority, expected proficiency, and experience context.
* Qualifiers should remain attached to the concept they modify. For example, “3+ years of professional Python development” keeps the years and professional context attached to that specific requirement.
* Pydantic field constraints handle simple rules such as non-negative years, while `model_validator` handles rules involving several fields or the model as a whole.
* Shared model configuration such as rejecting unknown fields belongs in the common `DomainModel` rather than being repeated in every model.
* Structural validation and semantic validation are different. Pydantic can verify that `REQUIRED` is a valid priority, but a later semantic validation stage must verify that the original posting actually described the requirement as required.
* Tests should focus on domain contracts and failure modes rather than retesting basic Pydantic or Python behavior.
* Writing a failing duplicate-requirement-ID test before implementing the validator provided a small example of test-driven development.
* 
## Evidence Modelling and Traceability

- Evidence should be represented as documented scenarios rather than duplicated every time it supports another requirement.
- `SourceItem` preserves provenance back to the Professional Portfolio/RAG.
- Evidence capability and requirement fit are separate concepts: the same capability may strongly satisfy one requirement and only partially satisfy another.
- Depth, repetition, autonomy, context, and confidence should remain separate rather than being collapsed into one arbitrary skill score.
- Unsupported requirements must remain observable and must not receive evidence or claim eligibility.
- Top-level models can validate reference integrity that individual nested models cannot verify alone.
- Cross-model references, such as `EvidenceMap.requirement_id` → `JobSpec.REQ-*`, will be validated later where both models are available.

## CV Content Planning

- `CVContentPlan` separates content strategy from final CV wording.
- `SectionPlan` describes document organization, while `PlannedContentItem` describes content placed inside those sections.
- Requirement-targeted content must preserve evidence traceability.
- Planning can explicitly define allowed claim scope and prohibited implications before any prose is generated.
- Parent models can enforce relationships that nested objects cannot detect individually, such as unique section ordering and unique planned-item IDs.
- References to objects in other domains (`REQ-*`, `SCEN-*`, `EXP-*`, etc.) require later cross-model validation.

## CV Draft Modelling and Claim Provenance

- `CVDraft` represents the exact CV content proposed for a specific application, while `CVContentPlan` defines what should be communicated before wording is generated.
- Generated factual statements are represented as `DraftClaim` objects so final CV text remains traceable.
- Claims distinguish between canonical candidate data, evidence-derived information, and mixed claims.
- Canonical claims reference stable candidate entities such as `EXP-*` or `EDU-*`; evidence-based claims reference `SCEN-*`.
- CV elements such as summaries, skills, and experience bullets reference claims rather than independently carrying provenance.
- Parent models validate internal references, such as `ExperienceBullet -> CLAIM-*`, because nested models cannot know whether a referenced claim actually exists.
- References across domain boundaries remain intentionally unresolved inside individual models. Examples include:
  - `DraftClaim.plan_item_ref -> CVContentPlan`
  - `DraftClaim.requirement_refs -> JobSpec`
  - `DraftClaim.evidence_refs -> EvidenceMap`
  - `DraftExperience.source_entity_ref -> CandidateProfile`
- These relationships require a later cross-model validation layer where all relevant domain objects are available.
- Data modelling can involve substantial domain complexity without substantial algorithmic complexity. Much of the implementation work consists of encoding previously defined contracts and invariants into typed models.

## Domain Model Milestone

The first implementation of the core domain layer is complete:

1. `CandidateProfile` — canonical, job-independent candidate information.
2. `JobSpec` — structured representation of the employer and job requirements.
3. `EvidenceMap` — evidence provenance, capability assessment, and requirement matching.
4. `CVContentPlan` — job-specific content selection, emphasis, and claim boundaries.
5. `CVDraft` — exact proposed CV content with claim-level provenance.

The domain layer establishes the contracts that later pipeline components must respect.

## Cross-Model Validation

- Individual Pydantic models can validate only information available inside their own boundaries.
- Relationships between domain models require a separate cross-model validation layer.
- Cross-model validation protects reference integrity across `JobSpec`, `EvidenceMap`, `CVContentPlan`, `CVDraft`, and `CandidateProfile`.
- Validation progresses beyond checking whether IDs exist: it also verifies that evidence is approved for a requirement, claims are eligible, draft claims stay within their content-plan boundaries, and canonical candidate facts are not altered.
- Validation errors were initially represented as `list[str]` to establish behavior with minimal abstraction.
- As validation became a subsystem, raw strings were replaced with structured `ValidationIssue` objects containing stable codes, stages, severities, references, and human-readable messages.
- Individual validators return `list[ValidationIssue]`.
- `validate_pipeline_contracts()` aggregates those issues into a `ValidationReport`.
- `ValidationReport.is_valid` provides the application-level decision about whether the pipeline may continue.
- Structured validation results will later support logging, debugging, and targeted LLM retry behavior without parsing human-readable error strings.