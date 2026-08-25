# Learning Notes

## Python Project Environment and Tooling

- An IDE such as VS Code or PyCharm is an interface over the underlying development tools; the project should remain usable independently of the IDE.

- A virtual environment provides an isolated Python runtime context for a project.

- `pyproject.toml` declares project metadata, Python requirements, dependencies, build configuration, and tool configuration.

- `uv` resolves and manages project dependencies and environments.

- `uv.lock` records the resolved dependency solution for reproducibility.

- Runtime dependencies and development dependencies serve different purposes.

- pytest tests software behavior.

- Ruff performs linting, import checking, modernization checks, and other code-quality checks.

- mypy performs static type checking.

- pytest, Ruff, and mypy cover different concerns:
  - pytest: behavioral correctness
  - Ruff: code quality and consistency
  - mypy: static type consistency

- CI can later automate these checks whenever code changes are pushed.

- Development tools should be runnable from the command line rather than depending on IDE-specific configuration.

## Domain Models, Validation, and Testing

- Pydantic models define both the structure of domain data and runtime validation rules.

- `model_validator(mode="after")` is useful for invariants involving multiple fields.

- Field-level constraints are appropriate for simple rules, while model-level validators are appropriate for relationships between fields.

- Shared model configuration such as rejecting unknown fields belongs in a common base model rather than being repeated throughout the domain layer.

- Generic reusable logic should be separated from domain-specific business rules when appropriate.

- Domain models should represent concepts independently from the workflow that later consumes them.

- Structural validation and semantic validation are different. A model can be structurally valid while still being semantically inconsistent with another artifact or with the source information from which it was produced.

- Unit tests should protect meaningful behavior, edge cases, invariants, and regressions rather than unnecessarily retesting Python or library behavior.

- Tests remain part of the codebase and make later refactoring safer.

- A failing test during the `EducationRecord` refactor successfully detected that an existing business rule had been removed.

- Writing a failing duplicate-ID test before implementing the corresponding validator provided a small example of test-driven development.

## Typed Python and Reusable Interfaces

- Python type annotations document expected inputs and outputs while also allowing tools such as mypy to statically verify parts of the program.

# Learning Notes

## Python Project Environment and Tooling

- An IDE such as VS Code or PyCharm is an interface over the underlying development tools; the project should remain usable independently of the IDE.

- A virtual environment provides an isolated Python runtime context for a project.

- `pyproject.toml` declares project metadata, Python requirements, dependencies, build configuration, and tool configuration.

- `uv` resolves and manages project dependencies and environments.

- `uv.lock` records the resolved dependency solution for reproducibility.

- Runtime dependencies and development dependencies serve different purposes.

- pytest tests software behavior.

- Ruff performs linting, import checking, modernization checks, and other code-quality checks.

- mypy performs static type checking.

- pytest, Ruff, and mypy cover different concerns:
  - pytest: behavioral correctness
  - Ruff: code quality and consistency
  - mypy: static type consistency

- CI can later automate these checks whenever code changes are pushed.

- Development tools should be runnable from the command line rather than depending on IDE-specific configuration.

## Domain Models, Validation, and Testing

- Pydantic models define both the structure of domain data and runtime validation rules.

- `model_validator(mode="after")` is useful for invariants involving multiple fields.

- Field-level constraints are appropriate for simple rules, while model-level validators are appropriate for relationships between fields.

- Shared model configuration such as rejecting unknown fields belongs in a common base model rather than being repeated throughout the domain layer.

- Generic reusable logic should be separated from domain-specific business rules when appropriate.

- Domain models should represent concepts independently from the workflow that later consumes them.

- Structural validation and semantic validation are different. A model can be structurally valid while still being semantically inconsistent with another artifact or with the source information from which it was produced.

- Unit tests should protect meaningful behavior, edge cases, invariants, and regressions rather than unnecessarily retesting Python or library behavior.

- Tests remain part of the codebase and make later refactoring safer.

- A failing test during the `EducationRecord` refactor successfully detected that an existing business rule had been removed.

- Writing a failing duplicate-ID test before implementing the corresponding validator provided a small example of test-driven development.

## Typed Python and Reusable Interfaces

- Python type annotations document expected inputs and outputs while also allowing tools such as mypy to statically verify parts of the program.

- `TypeVar` can preserve a concrete type through generic reusable functions.

- For example, a generic JSON loader can accept `type[JobSpec]` and return `JobSpec`, rather than returning only a generic `BaseModel`.

- Python protocols provide interface-like contracts without requiring traditional inheritance.

- Structural typing means an object can satisfy a `Protocol` by implementing the required methods with compatible signatures.

- This differs from nominal typing, where a class must explicitly inherit from a particular base class or interface.

- Protocols are useful at architectural boundaries because application code can depend on required behavior rather than on a particular implementation.

## JobSpec Domain Modelling

- Domain models should describe the object itself independently from later decisions about the candidate. `JobSpec` describes the employer, position, and requirements; candidate fit is evaluated later.

- Enums constrain controlled vocabularies such as work arrangement, employment type, requirement category, priority, expected proficiency, explicitness, and experience context.

- Qualifiers should remain attached to the concept they modify. For example, “3+ years of professional Python development” keeps the years and professional context attached to that specific requirement.

- Pydantic field constraints handle simple rules such as non-negative years, while `model_validator` handles rules involving several fields or the model as a whole.

- Requirement IDs such as `REQ-*` provide stable references that later artifacts can use without copying or ambiguously re-identifying requirements.

- Structural validation can verify that values conform to the `JobSpec` schema, while later semantic checks must determine whether the structured interpretation accurately reflects the original posting.

- Candidate suitability does not belong in `JobSpec`; it belongs in later evidence-matching stages.

## Evidence Modelling and Traceability

- Evidence should be represented as documented scenarios rather than duplicated every time it supports another requirement.

- `SourceItem` preserves provenance back to the Professional Portfolio/RAG.

- Evidence capability and requirement fit are separate concepts: the same capability may strongly satisfy one requirement and only partially satisfy another.

- Depth, repetition, autonomy, context, and confidence should remain separate rather than being collapsed into one arbitrary skill score.

- `EvidenceMap` connects job requirements to documented evidence while preserving the distinction between the evidence itself and the assessment of how strongly it satisfies a requirement.

- Unsupported requirements must remain observable and must not receive evidence or claim eligibility.

- Stable scenario IDs such as `SCEN-*` allow later planning and drafting stages to trace claims back to specific supporting evidence.

- Top-level models can validate reference integrity that individual nested models cannot verify alone.

- Relationships between `EvidenceMap` and `JobSpec` are now checked by the cross-model validation layer.

- Evidence assessments must correspond to actual job requirements, and job requirements must not silently disappear from evidence assessment.

## CV Content Planning

- `CVContentPlan` separates content strategy from final CV wording.

- `SectionPlan` describes document organization, while `PlannedContentItem` describes content placed inside those sections.

- Stable `PLAN-*` IDs allow final draft claims to reference the exact planning decision that authorized them.

- Requirement-targeted content must preserve evidence traceability.

- Planning can explicitly define allowed claim scope and prohibited implications before any prose is generated.

- Content can be deliberately included or omitted rather than leaving all decisions to the final writer.

- Parent models can enforce relationships that nested objects cannot detect individually, such as unique section ordering and unique planned-item IDs.

- Cross-model validation now verifies that `REQ-*` references exist in `JobSpec` and that `SCEN-*` references exist in `EvidenceMap`.

- Cross-model validation also checks that evidence used by a planned item is actually approved for the requirement being targeted.

- Requirements with no claim eligibility cannot be used to justify included content.

- Experience and education planning items are validated against `CandidateProfile` so that `EXP-*` and `EDU-*` source references must correspond to real canonical candidate entities.

## CV Draft Modelling and Claim Provenance

- `CVDraft` represents the exact CV content proposed for a specific application, while `CVContentPlan` defines what should be communicated before wording is generated.

- Generated factual statements are represented as `DraftClaim` objects so final CV text remains traceable.

- Claims distinguish between canonical candidate data, evidence-derived information, and mixed claims.

- Canonical claims reference stable candidate entities such as `EXP-*` or `EDU-*`; evidence-based claims reference `SCEN-*`.

- Draft claims reference their originating `PLAN-*` item so the final wording remains connected to the planning decision that authorized it.

- CV elements such as summaries, skills, and experience bullets reference claims rather than independently carrying provenance.

- Parent models validate internal references, such as `ExperienceBullet -> CLAIM-*`, because nested models cannot know whether a referenced claim actually exists.

- Cross-model validation verifies relationships such as:
  - `DraftClaim.plan_item_ref -> CVContentPlan`
  - `DraftClaim.requirement_refs -> approved requirements in the plan`
  - `DraftClaim.evidence_refs -> approved evidence in the plan`
  - `DraftExperience.source_entity_ref -> CandidateProfile`
  - `DraftEducation.source_entity_ref -> CandidateProfile`

- Draft claims may not introduce requirements or evidence that were not approved by the corresponding planned item.

- Canonical candidate information such as name, experience role, organization, education, and location is checked against `CandidateProfile` rather than trusting generated draft text.

- Data modelling can involve substantial domain complexity without substantial algorithmic complexity. Much of the implementation work consists of encoding previously defined contracts and invariants into typed models.

## Domain Model Milestone

- The first implementation of the five core domain models is complete:
  1. `CandidateProfile` — canonical, job-independent candidate information.
  2. `JobSpec` — structured representation of the employer and job requirements.
  3. `EvidenceMap` — evidence provenance, capability assessment, and requirement matching.
  4. `CVContentPlan` — job-specific content selection, emphasis, and claim boundaries.
  5. `CVDraft` — exact proposed CV content with claim-level provenance.

- These models form explicit data contracts between the main stages of the CV-generation pipeline.

- Stable IDs provide traceability between independently generated artifacts.

- The domain layer establishes what valid data looks like, while later application services determine how those artifacts are produced and moved through the workflow.

## Cross-Model Validation

- Individual Pydantic models can validate only information available inside their own boundaries.

- Relationships between domain models therefore require a separate cross-model validation layer.

- Cross-model validation protects reference integrity across `CandidateProfile`, `JobSpec`, `EvidenceMap`, `CVContentPlan`, and `CVDraft`.

- Validation progresses beyond checking whether IDs exist: it also verifies that evidence is approved for a requirement, claims are eligible, draft claims stay within their content-plan boundaries, and canonical candidate facts are not altered.

- Candidate-profile-to-content-plan validation checks that planned experience and education content references real canonical candidate entities.

- Evidence-map validation checks that assessments correspond to the requirements in the current `JobSpec`.

- Content-plan validation checks references, evidence alignment, and claim eligibility.

- Draft validation checks plan references, approved requirement/evidence boundaries, and canonical candidate information.

- Validation errors were initially represented as `list[str]` to establish behavior with minimal abstraction.

- As validation became a subsystem, raw strings were replaced with structured `ValidationIssue` objects containing stable codes, stages, severities, references, and human-readable messages.

- Individual validators return `list[ValidationIssue]`.

- `ValidationReport` aggregates validation issues and exposes `is_valid` as the application-level decision about whether processing may continue.

- Stable validation codes are preferable to tests that depend on exact human-readable error wording.

- Structured validation results can later support logging, debugging, reporting, and targeted LLM retry behavior without parsing error strings.

## Artifact Persistence

- Intermediate pipeline artifacts are persisted as JSON so stages can be inspected, tested, and debugged independently.

- `json_store.py` provides generic typed serialization and deserialization for Pydantic models.

- `TypeVar` preserves the concrete model type through the generic loader.

- `model_validate_json()` reconstructs the requested Pydantic model while rerunning its validation rules.

- Invalid JSON and schema-invalid JSON fail rather than silently producing partially valid artifacts.

- `ArtifactPaths` centralizes filesystem-layout policy.

- `ArtifactStore` provides an application-friendly facade over path generation and JSON persistence.

- Persistence responsibilities are separated into:
  - `json_store` — how models are serialized and deserialized
  - `ArtifactPaths` — where artifacts are stored
  - `ArtifactStore` — which domain model belongs at which location

- `CandidateProfile` is treated as a relatively stable global artifact, while job-specific artifacts are stored under individual run directories.

- The per-run structure keeps `JobSpec`, `EvidenceMap`, `CVContentPlan`, `CVDraft`, and validation results associated with the same application attempt.

- Persisting intermediate artifacts makes failures inspectable instead of hiding all intermediate state inside one large pipeline function.

## Test Factories and Pytest Fixtures

- Test factories create coherent domain data that can be reused across tests.

- `make_valid_pipeline()` provides a complete, mutually consistent `CandidateProfile`, `JobSpec`, `EvidenceMap`, `CVContentPlan`, and `CVDraft`.

- A valid baseline can then be modified to create a specific invalid condition without rebuilding every object manually.

- Factories are particularly useful for complex domain objects with many required nested fields.

- Pytest fixtures serve a different purpose from factories.

- A useful distinction is:
  - factories create domain/test data
  - fixtures provide reusable dependencies or test environment setup

- The `artifact_store` fixture uses pytest's `tmp_path` fixture so persistence tests operate in an isolated temporary filesystem.

- Pytest fixtures use function scope by default, which prevents mutable test state from unintentionally leaking between tests.

- Existing tests do not need to be rewritten purely to use factories; factories should be introduced where they reduce meaningful duplication.

- `model_copy(update=...)` is useful for creating targeted variants of valid test objects, but updates should be used carefully because they do not necessarily rerun complete Pydantic validation.

## Testing at Different Architectural Levels

- Tests should target the responsibility of the component being tested.

- Domain tests verify model invariants and domain rules.

- Cross-model validation tests verify relationships between independently valid artifacts.

- Persistence tests verify serialization, filesystem policy, and artifact loading/saving.

- Application-service tests verify orchestration decisions such as validation, persistence, and stopping after failure.

- Higher-level application tests should not repeat every validator rule that already has focused unit tests.

- A representative invalid case is usually sufficient to prove that an application service handles validation failure correctly.

- Testing the same rule repeatedly at every layer creates unnecessary duplication and makes the suite harder to maintain.

- End-to-end application tests are valuable for verifying that independently tested components are correctly connected.

## Application Layer vs Domain Layer

- The domain layer defines what the application's information means and what valid domain objects look like.

- The application layer coordinates how those domain objects are produced, validated, persisted, and passed between stages.

- Domain models should not need to know which LLM provider, filesystem implementation, or orchestration strategy is used.

- Application services implement use cases rather than redefining domain rules.

- A useful distinction is:
  - domain layer — what valid information looks like
  - application layer — what the program does with that information

- For example, detecting an invalid evidence relationship belongs to validation, while deciding not to invoke the planner after that failure belongs to application orchestration.

## Ports and Adapters

- The application should not depend directly on a specific LLM provider, API, local model, or retrieval technology.

- Stable application-facing interfaces are defined as ports using Python `Protocol`.

- The current application ports are:
  - `JobAnalyzer`
  - `EvidenceMatcher`
  - `CVPlanner`
  - `CVWriter`

- A port defines what the application needs without defining how that behavior is implemented.

- Concrete implementations behind those interfaces are adapters.

- Possible adapters can include:
  - deterministic test implementations
  - local LLM implementations
  - external API implementations
  - retrieval implementations using the Professional Portfolio
  - future providers without changes to the core application workflow

- This architecture places unstable or external implementation details behind stable application boundaries.

- The concept is similar to scientific instrumentation software depending on a stable instrument interface while a device-specific driver handles communication with the actual hardware.

## Protocol and Structural Typing

- Python `Protocol` can describe required behavior without forcing implementing classes to inherit from it.

- A fake class used in a test can satisfy `CVWriter` simply by providing a compatible `write()` method.

- This is structural typing: compatibility is determined by the shape and behavior of the object rather than by explicit inheritance.

- Protocols allow mypy to verify that injected implementations respect the interface expected by the application.

- Protocols are particularly useful for dependencies whose implementations may change while the application-facing contract remains stable.

## Dependency Injection

- Application services receive dependencies as function parameters rather than constructing concrete implementations internally.

- For example, the pipeline receives objects satisfying `JobAnalyzer`, `EvidenceMatcher`, `CVPlanner`, and `CVWriter`.

- The application therefore does not decide whether those objects are fake test implementations, local models, API clients, or other adapters.

- This pattern is dependency injection.

- Dependency injection reduces coupling between application logic and infrastructure.

- It also makes testing simpler because deterministic fakes can replace expensive, slow, or unpredictable external dependencies.

- The same principle applies to `ArtifactStore`, which is passed into services rather than created inside every function.

## Application Stage Services

- Each major pipeline stage is implemented as an independent application service.

- `analyze_and_store_job()` coordinates job analysis and `JobSpec` persistence.

- `match_validate_and_store_evidence()` coordinates evidence matching, validation, and conditional persistence.

- `plan_validate_and_store_content()` coordinates CV planning, validation, and conditional persistence.

- `write_validate_and_store_draft()` coordinates CV writing, validation, and conditional persistence.

- Each service has a narrow responsibility and can be tested independently.

- The common stage pattern is:
  - produce a structured domain artifact
  - validate the relevant contracts
  - persist the artifact only if valid
  - return the artifact and/or validation result to the caller

- Keeping stages independent makes it easier to replace one implementation without redesigning the rest of the pipeline.

## CVWriter Boundary

- `CVWriter` deliberately does not receive the raw job posting or `JobSpec`.

- By the time writing begins, the job has already been interpreted through job analysis, evidence matching, and content planning.

- The writer receives:
  - `CandidateProfile`
  - `EvidenceMap`
  - `CVContentPlan`

- The writer's responsibility is therefore to produce strong final wording from approved information rather than independently deciding what the job requires.

- This creates an architectural guardrail against unsupported claims and unnecessary reinterpretation of the original posting.

- The content plan acts as a writing sandbox defining what may be communicated and which evidence supports it.

## Pipeline Orchestration

- Individual application services know how to execute one stage; the pipeline orchestrator knows how the complete workflow progresses.

- The orchestrator controls:
  - execution order
  - data passed between stages
  - validation checkpoints
  - stop conditions
  - final returned results

- The current application flow is:

  `Job text -> JobAnalyzer -> JobSpec -> EvidenceMatcher -> EvidenceMap -> CVPlanner -> CVContentPlan -> CVWriter -> CVDraft`

- Orchestration is separate from stage implementation so that individual services remain independently testable.

- The pipeline currently operates with injected fake implementations, allowing the complete workflow to be tested without an actual LLM.

## Fail-Fast Pipeline Behavior

- Invalid intermediate artifacts must not be allowed to propagate into downstream stages.

- The pipeline therefore stops when an intermediate validation report is invalid.

- For example, an invalid `EvidenceMap` prevents both `CVPlanner` and `CVWriter` from running.

- Valid earlier artifacts remain available for debugging, while invalid downstream artifacts are not persisted.

- A validation report is persisted to explain why the pipeline stopped.

- Fail-fast behavior prevents later components from reasoning from information that has already violated an application contract.

- Stopping at clear validation gates also creates a future location for targeted retry or repair logic.

## Fake Adapters and Test Doubles

- The complete application workflow can be tested without calling an actual AI model.

- Fake implementations return predetermined valid or invalid domain objects.

- A fake does not need to realistically simulate an LLM; its purpose is to isolate the application workflow from the external dependency.

- Fake adapters allow deterministic testing of questions such as:
  - Was the correct stage invoked?
  - Was the previous artifact passed forward?
  - Was validation performed?
  - Was valid output persisted?
  - Did the pipeline stop after an invalid stage?

- `FailIfCalled` test doubles deliberately raise `AssertionError` if a stage that should have been skipped is invoked.

- This verifies workflow control directly rather than only inferring it from missing output files.

- Real LLM quality and prompt behavior should later be tested separately from the deterministic application-orchestration tests.

## Application Pipeline Milestone

- The AI-independent application skeleton is now complete for the current V1 architecture.

- All four main application ports exist:
  - `JobAnalyzer`
  - `EvidenceMatcher`
  - `CVPlanner`
  - `CVWriter`

- Application services exist for analysis, evidence matching, planning, and writing.

- Each structured stage can be validated before downstream processing.

- Intermediate artifacts can be persisted and inspected.

- The complete pipeline has a tested successful path from synthetic job text to a persisted `CVDraft`.

- The pipeline also has a tested failure path demonstrating that invalid evidence stops downstream planning and writing.

- The application can therefore operate end-to-end using deterministic fake adapters even though real retrieval and LLM implementations have not yet been connected.

- This separates completion of the core software architecture from integration of external intelligence.

## Next Learning Phase: Professional Portfolio / RAG Integration

- The next major problem is connecting the real Professional Portfolio to the existing application architecture.

- The first objective is to determine how candidate evidence should be discovered and supplied to `EvidenceMatcher`.

- The existing Professional Portfolio structure should be inspected before selecting a retrieval technology.

- The simplest reliable V1 retrieval approach should be preferred.

- Embeddings and vector databases should not be introduced automatically simply because the system is described as RAG.

- Deterministic file discovery, structured Markdown parsing, targeted retrieval, or other simpler methods should be evaluated first.

- Retrieval should preserve provenance so selected evidence remains traceable to its original portfolio files.

- The retrieval implementation should remain behind a stable application boundary so it can evolve without changing the core pipeline.

- After portfolio retrieval is working, real implementations of `JobAnalyzer`, `EvidenceMatcher`, `CVPlanner`, and `CVWriter` can progressively replace the current fake adapters.

- LaTeX/PDF rendering belongs downstream of a validated `CVDraft` and does not need to affect the evidence-retrieval architecture.

- For example, a generic JSON loader can accept `type[JobSpec]` and return `JobSpec`, rather than returning only a generic `BaseModel`.

- Python protocols provide interface-like contracts without requiring traditional inheritance.

- Structural typing means an object can satisfy a `Protocol` by implementing the required methods with compatible signatures.

- This differs from nominal typing, where a class must explicitly inherit from a particular base class or interface.

- Protocols are useful at architectural boundaries because application code can depend on required behavior rather than on a particular implementation.

## JobSpec Domain Modelling

- Domain models should describe the object itself independently from later decisions about the candidate. `JobSpec` describes the employer, position, and requirements; candidate fit is evaluated later.

- Enums constrain controlled vocabularies such as work arrangement, employment type, requirement category, priority, expected proficiency, explicitness, and experience context.

- Qualifiers should remain attached to the concept they modify. For example, “3+ years of professional Python development” keeps the years and professional context attached to that specific requirement.

- Pydantic field constraints handle simple rules such as non-negative years, while `model_validator` handles rules involving several fields or the model as a whole.

- Requirement IDs such as `REQ-*` provide stable references that later artifacts can use without copying or ambiguously re-identifying requirements.

- Structural validation can verify that values conform to the `JobSpec` schema, while later semantic checks must determine whether the structured interpretation accurately reflects the original posting.

- Candidate suitability does not belong in `JobSpec`; it belongs in later evidence-matching stages.

## Evidence Modelling and Traceability

- Evidence should be represented as documented scenarios rather than duplicated every time it supports another requirement.

- `SourceItem` preserves provenance back to the Professional Portfolio/RAG.

- Evidence capability and requirement fit are separate concepts: the same capability may strongly satisfy one requirement and only partially satisfy another.

- Depth, repetition, autonomy, context, and confidence should remain separate rather than being collapsed into one arbitrary skill score.

- `EvidenceMap` connects job requirements to documented evidence while preserving the distinction between the evidence itself and the assessment of how strongly it satisfies a requirement.

- Unsupported requirements must remain observable and must not receive evidence or claim eligibility.

- Stable scenario IDs such as `SCEN-*` allow later planning and drafting stages to trace claims back to specific supporting evidence.

- Top-level models can validate reference integrity that individual nested models cannot verify alone.

- Relationships between `EvidenceMap` and `JobSpec` are now checked by the cross-model validation layer.

- Evidence assessments must correspond to actual job requirements, and job requirements must not silently disappear from evidence assessment.

## CV Content Planning

- `CVContentPlan` separates content strategy from final CV wording.

- `SectionPlan` describes document organization, while `PlannedContentItem` describes content placed inside those sections.

- Stable `PLAN-*` IDs allow final draft claims to reference the exact planning decision that authorized them.

- Requirement-targeted content must preserve evidence traceability.

- Planning can explicitly define allowed claim scope and prohibited implications before any prose is generated.

- Content can be deliberately included or omitted rather than leaving all decisions to the final writer.

- Parent models can enforce relationships that nested objects cannot detect individually, such as unique section ordering and unique planned-item IDs.

- Cross-model validation now verifies that `REQ-*` references exist in `JobSpec` and that `SCEN-*` references exist in `EvidenceMap`.

- Cross-model validation also checks that evidence used by a planned item is actually approved for the requirement being targeted.

- Requirements with no claim eligibility cannot be used to justify included content.

- Experience and education planning items are validated against `CandidateProfile` so that `EXP-*` and `EDU-*` source references must correspond to real canonical candidate entities.

## CV Draft Modelling and Claim Provenance

- `CVDraft` represents the exact CV content proposed for a specific application, while `CVContentPlan` defines what should be communicated before wording is generated.

- Generated factual statements are represented as `DraftClaim` objects so final CV text remains traceable.

- Claims distinguish between canonical candidate data, evidence-derived information, and mixed claims.

- Canonical claims reference stable candidate entities such as `EXP-*` or `EDU-*`; evidence-based claims reference `SCEN-*`.

- Draft claims reference their originating `PLAN-*` item so the final wording remains connected to the planning decision that authorized it.

- CV elements such as summaries, skills, and experience bullets reference claims rather than independently carrying provenance.

- Parent models validate internal references, such as `ExperienceBullet -> CLAIM-*`, because nested models cannot know whether a referenced claim actually exists.

- Cross-model validation verifies relationships such as:
  - `DraftClaim.plan_item_ref -> CVContentPlan`
  - `DraftClaim.requirement_refs -> approved requirements in the plan`
  - `DraftClaim.evidence_refs -> approved evidence in the plan`
  - `DraftExperience.source_entity_ref -> CandidateProfile`
  - `DraftEducation.source_entity_ref -> CandidateProfile`

- Draft claims may not introduce requirements or evidence that were not approved by the corresponding planned item.

- Canonical candidate information such as name, experience role, organization, education, and location is checked against `CandidateProfile` rather than trusting generated draft text.

- Data modelling can involve substantial domain complexity without substantial algorithmic complexity. Much of the implementation work consists of encoding previously defined contracts and invariants into typed models.

## Domain Model Milestone

- The first implementation of the five core domain models is complete:
  1. `CandidateProfile` — canonical, job-independent candidate information.
  2. `JobSpec` — structured representation of the employer and job requirements.
  3. `EvidenceMap` — evidence provenance, capability assessment, and requirement matching.
  4. `CVContentPlan` — job-specific content selection, emphasis, and claim boundaries.
  5. `CVDraft` — exact proposed CV content with claim-level provenance.

- These models form explicit data contracts between the main stages of the CV-generation pipeline.

- Stable IDs provide traceability between independently generated artifacts.

- The domain layer establishes what valid data looks like, while later application services determine how those artifacts are produced and moved through the workflow.

## Cross-Model Validation

- Individual Pydantic models can validate only information available inside their own boundaries.

- Relationships between domain models therefore require a separate cross-model validation layer.

- Cross-model validation protects reference integrity across `CandidateProfile`, `JobSpec`, `EvidenceMap`, `CVContentPlan`, and `CVDraft`.

- Validation progresses beyond checking whether IDs exist: it also verifies that evidence is approved for a requirement, claims are eligible, draft claims stay within their content-plan boundaries, and canonical candidate facts are not altered.

- Candidate-profile-to-content-plan validation checks that planned experience and education content references real canonical candidate entities.

- Evidence-map validation checks that assessments correspond to the requirements in the current `JobSpec`.

- Content-plan validation checks references, evidence alignment, and claim eligibility.

- Draft validation checks plan references, approved requirement/evidence boundaries, and canonical candidate information.

- Validation errors were initially represented as `list[str]` to establish behavior with minimal abstraction.

- As validation became a subsystem, raw strings were replaced with structured `ValidationIssue` objects containing stable codes, stages, severities, references, and human-readable messages.

- Individual validators return `list[ValidationIssue]`.

- `ValidationReport` aggregates validation issues and exposes `is_valid` as the application-level decision about whether processing may continue.

- Stable validation codes are preferable to tests that depend on exact human-readable error wording.

- Structured validation results can later support logging, debugging, reporting, and targeted LLM retry behavior without parsing error strings.

## Artifact Persistence

- Intermediate pipeline artifacts are persisted as JSON so stages can be inspected, tested, and debugged independently.

- `json_store.py` provides generic typed serialization and deserialization for Pydantic models.

- A generic type parameter preserves the concrete Pydantic model type through the reusable loader.

- `model_validate_json()` reconstructs the requested Pydantic model while rerunning its validation rules.

- Invalid JSON and schema-invalid JSON fail rather than silently producing partially valid artifacts.

- `ArtifactPaths` centralizes filesystem-layout policy.

- `ArtifactStore` provides an application-friendly facade over path generation and JSON persistence.

- Persistence responsibilities are separated into:
  - `json_store` — how models are serialized and deserialized
  - `ArtifactPaths` — where artifacts are stored
  - `ArtifactStore` — which domain model belongs at which location

- `CandidateProfile` is treated as a relatively stable global artifact, while job-specific artifacts are stored under individual run directories.

- The per-run structure keeps `JobSpec`, `EvidenceMap`, `CVContentPlan`, `CVDraft`, and validation results associated with the same application attempt.

- Persisting intermediate artifacts makes failures inspectable instead of hiding all intermediate state inside one large pipeline function.

## Test Factories and Pytest Fixtures

- Test factories create coherent domain data that can be reused across tests.

- `make_valid_pipeline()` provides a complete, mutually consistent `CandidateProfile`, `JobSpec`, `EvidenceMap`, `CVContentPlan`, and `CVDraft`.

- A valid baseline can then be modified to create a specific invalid condition without rebuilding every object manually.

- Factories are particularly useful for complex domain objects with many required nested fields.

- Pytest fixtures serve a different purpose from factories.

- A useful distinction is:
  - factories create domain/test data
  - fixtures provide reusable dependencies or test environment setup

- The `artifact_store` fixture uses pytest's `tmp_path` fixture so persistence tests operate in an isolated temporary filesystem.

- Pytest fixtures use function scope by default, which prevents mutable test state from unintentionally leaking between tests.

- Existing tests do not need to be rewritten purely to use factories; factories should be introduced where they reduce meaningful duplication.

- `model_copy(update=...)` is useful for creating targeted variants of valid test objects, but updates should be used carefully because they do not necessarily rerun complete Pydantic validation.

## Testing at Different Architectural Levels

- Tests should target the responsibility of the component being tested.

- Domain tests verify model invariants and domain rules.

- Cross-model validation tests verify relationships between independently valid artifacts.

- Persistence tests verify serialization, filesystem policy, and artifact loading/saving.

- Application-service tests verify orchestration decisions such as validation, persistence, and stopping after failure.

- Higher-level application tests should not repeat every validator rule that already has focused unit tests.

- A representative invalid case is usually sufficient to prove that an application service handles validation failure correctly.

- Testing the same rule repeatedly at every layer creates unnecessary duplication and makes the suite harder to maintain.

- End-to-end application tests are valuable for verifying that independently tested components are correctly connected.

## Application Layer vs Domain Layer

- The domain layer defines what the application's information means and what valid domain objects look like.

- The application layer coordinates how those domain objects are produced, validated, persisted, and passed between stages.

- Domain models should not need to know which LLM provider, filesystem implementation, or orchestration strategy is used.

- Application services implement use cases rather than redefining domain rules.

- A useful distinction is:
  - domain layer — what valid information looks like
  - application layer — what the program does with that information

- For example, detecting an invalid evidence relationship belongs to validation, while deciding not to invoke the planner after that failure belongs to application orchestration.

## Ports and Adapters

- The application should not depend directly on a specific LLM provider, API, local model, or retrieval technology.

- Stable application-facing interfaces are defined as ports using Python `Protocol`.

- The current application ports are:
  - `JobAnalyzer`
  - `EvidenceMatcher`
  - `CVPlanner`
  - `CVWriter`

- A port defines what the application needs without defining how that behavior is implemented.

- Concrete implementations behind those interfaces are adapters.

- Possible adapters can include:
  - deterministic test implementations
  - local LLM implementations
  - external API implementations
  - retrieval implementations using the Professional Portfolio
  - future providers without changes to the core application workflow

- This architecture places unstable or external implementation details behind stable application boundaries.

- The concept is similar to scientific instrumentation software depending on a stable instrument interface while a device-specific driver handles communication with the actual hardware.

## Protocol and Structural Typing

- Python `Protocol` can describe required behavior without forcing implementing classes to inherit from it.

- A fake class used in a test can satisfy `CVWriter` simply by providing a compatible `write()` method.

- This is structural typing: compatibility is determined by the shape and behavior of the object rather than by explicit inheritance.

- Protocols allow mypy to verify that injected implementations respect the interface expected by the application.

- Protocols are particularly useful for dependencies whose implementations may change while the application-facing contract remains stable.

## Dependency Injection

- Application services receive dependencies as function parameters rather than constructing concrete implementations internally.

- For example, the pipeline receives objects satisfying `JobAnalyzer`, `EvidenceMatcher`, `CVPlanner`, and `CVWriter`.

- The application therefore does not decide whether those objects are fake test implementations, local models, API clients, or other adapters.

- This pattern is dependency injection.

- Dependency injection reduces coupling between application logic and infrastructure.

- It also makes testing simpler because deterministic fakes can replace expensive, slow, or unpredictable external dependencies.

- The same principle applies to `ArtifactStore`, which is passed into services rather than created inside every function.

## Application Stage Services

- Each major pipeline stage is implemented as an independent application service.

- `analyze_and_store_job()` coordinates job analysis and `JobSpec` persistence.

- `match_validate_and_store_evidence()` coordinates evidence matching, validation, and conditional persistence.

- `plan_validate_and_store_content()` coordinates CV planning, validation, and conditional persistence.

- `write_validate_and_store_draft()` coordinates CV writing, validation, and conditional persistence.

- Each service has a narrow responsibility and can be tested independently.

- The common stage pattern is:
  - produce a structured domain artifact
  - validate the relevant contracts
  - persist the artifact only if valid
  - return the artifact and/or validation result to the caller

- Keeping stages independent makes it easier to replace one implementation without redesigning the rest of the pipeline.

## CVWriter Boundary

- `CVWriter` deliberately does not receive the raw job posting or `JobSpec`.

- By the time writing begins, the job has already been interpreted through job analysis, evidence matching, and content planning.

- The writer receives:
  - `CandidateProfile`
  - `EvidenceMap`
  - `CVContentPlan`

- The writer's responsibility is therefore to produce strong final wording from approved information rather than independently deciding what the job requires.

- This creates an architectural guardrail against unsupported claims and unnecessary reinterpretation of the original posting.

- The content plan acts as a writing sandbox defining what may be communicated and which evidence supports it.

## Pipeline Orchestration

- Individual application services know how to execute one stage; the pipeline orchestrator knows how the complete workflow progresses.

- The orchestrator controls:
  - execution order
  - data passed between stages
  - validation checkpoints
  - stop conditions
  - final returned results

- The current application flow is:

  `Job text -> JobAnalyzer -> JobSpec -> EvidenceMatcher -> EvidenceMap -> CVPlanner -> CVContentPlan -> CVWriter -> CVDraft`

- Orchestration is separate from stage implementation so that individual services remain independently testable.

- The pipeline can operate with deterministic fake implementations during tests and with real Codex adapters during V1 execution, without changing the application orchestration.

## Fail-Fast Pipeline Behavior

- Invalid intermediate artifacts must not be allowed to propagate into downstream stages.

- The pipeline therefore stops when an intermediate validation report is invalid.

- For example, an invalid `EvidenceMap` prevents both `CVPlanner` and `CVWriter` from running.

- Valid earlier artifacts remain available for debugging, while invalid downstream artifacts are not persisted.

- A validation report is persisted to explain why the pipeline stopped.

- Fail-fast behavior prevents later components from reasoning from information that has already violated an application contract.

- Stopping at clear validation gates also creates a future location for targeted retry or repair logic.

## Fake Adapters and Test Doubles

- The complete application workflow can be tested without calling an actual AI model.

- Fake implementations return predetermined valid or invalid domain objects.

- A fake does not need to realistically simulate an LLM; its purpose is to isolate the application workflow from the external dependency.

- Fake adapters allow deterministic testing of questions such as:
  - Was the correct stage invoked?
  - Was the previous artifact passed forward?
  - Was validation performed?
  - Was valid output persisted?
  - Did the pipeline stop after an invalid stage?

- `FailIfCalled` test doubles deliberately raise `AssertionError` if a stage that should have been skipped is invoked.

- This verifies workflow control directly rather than only inferring it from missing output files.

- Real LLM quality and prompt behavior should later be tested separately from the deterministic application-orchestration tests.

# Learning Notes — Professional Portfolio, Codex, and Real Pipeline Integration

## Application Pipeline Milestone

* The AI-independent application skeleton remains the foundation of the system, but the V1 pipeline is no longer limited to fake adapters.

* The four main application ports remain:

  * `JobAnalyzer`

  * `EvidenceMatcher`

  * `CVPlanner`

  * `CVWriter`

* Real Codex-backed adapters now satisfy those same ports:

  * `CodexJobAnalyzer`

  * `CodexEvidenceMatcher`

  * `CodexCVPlanner`

  * `CodexCVWriter`

* Because the application layer depends on ports rather than concrete implementations, replacing fake adapters with real Codex adapters did not require redesigning the pipeline.

* This provides a practical example of why ports, dependency injection, and structural typing were introduced before the AI integration existed.

* The same application services and validation gates are used whether a stage is backed by a fake test implementation or by Codex.

* The V1 content pipeline has now been exercised using a real Nord Quantique job posting and the real Professional Portfolio.

* A real, job-specific `CVDraft` was successfully produced, validated, and persisted.

---

## Professional Portfolio Loading vs Retrieval

* Portfolio loading and job-specific retrieval are different responsibilities.

* Loading answers:

  > What documents constitute the candidate evidence corpus?

* Retrieval or matching answers:

  > Which evidence from that corpus supports this specific job requirement?

* For V1, the portfolio-loading layer does not perform semantic search, ranking, embeddings, or vector retrieval.

* `MarkdownPortfolioLoader` deterministically loads curated non-empty Markdown documents from approved evidence directories.

* An allowlist of evidence directories is preferable to loading every Markdown file and maintaining an expanding blacklist.

* This prevents repository documentation, AI instructions, changelogs, and unrelated files from entering the evidence corpus.

* README files and empty Markdown documents are excluded because they do not provide useful candidate evidence.

* Nested Markdown discovery is supported where appropriate.

* Stable repository-relative identifiers are generated using POSIX-style paths so provenance remains consistent across operating systems.

* Deterministic document ordering improves reproducibility, debugging, and AI-context construction.

---

## PortfolioDocument and PortfolioContext

* `PortfolioDocument` represents one source document supplied to evidence matching.

* It contains:

  * `source_id`

  * `content`

* `PortfolioContext` represents the collection of portfolio documents supplied to an Evidence Matcher operation.

* These are supporting data contracts rather than major persisted pipeline artifacts.

* They prevent the portfolio from being passed to the AI as one anonymous block of text.

* Stable `source_id` values provide the connection:

  `PortfolioDocument.source_id -> SourceItem.source_document`

* This allows generated evidence to remain traceable to the exact Markdown file from which it originated.

---

## Provenance Validation

* Prompt instructions alone are not sufficient to guarantee provenance.

* A model may return structurally valid JSON while citing a document that was never supplied.

* The application therefore validates `EvidenceMap` source references against the actual `PortfolioContext`.

* A portfolio source cited by generated evidence must correspond to a real `PortfolioDocument.source_id`.

* This converts provenance from a prompt-level request into a deterministic software rule.

* A useful distinction is:

  * schema validation: is the output structurally an `EvidenceMap`?

  * cross-model provenance validation: does the cited source actually exist in the supplied corpus?

* Provenance validation should not be weakened merely because an AI-generated source appears semantically plausible.

---

## Real Portfolio Smoke Testing

* Synthetic unit tests cannot reveal every assumption about real data.

* The Markdown loader initially passed all unit tests but the first real smoke test loaded fewer documents than expected because the local portfolio directory had been renamed from `03-projets` to `03-projects`.

* The real local portfolio was also newer than the uploaded reference ZIP and contained previously empty skill documents that had since been populated.

* This demonstrated the value of testing software against the actual operational data before integrating downstream systems.

* The current local Professional Portfolio contains 35 curated non-empty Markdown documents used by the V1 Evidence Matcher.

* The local portfolio is the operational source of truth when it differs from an older reference ZIP.

---

## Full-Context Retrieval Baseline

* The V1 retrieval decision was deliberately tested empirically before introducing more complex RAG infrastructure.

* The complete curated 35-document Professional Portfolio was supplied to Codex as context for Evidence Matching.

* Codex successfully produced a structured and useful `EvidenceMap`.

* The output drew evidence from multiple source categories, including:

  * skills

  * projects

  * experiences

  * code-audit documentation

* Codex also preserved important limitations rather than automatically turning all related experience into strong claims.

* The successful experiment supports continuing with full-context Markdown for V1.

* Embeddings, vector databases, semantic indexes, and ranking systems should therefore not be introduced merely because they are common RAG technologies.

* They become justified only if later empirical testing demonstrates a concrete problem such as context limits, latency, cost, or retrieval-quality degradation.

---

## Codex CLI as a V1 AI Backend

* Codex CLI is used through the existing ChatGPT account rather than through a separately billed API integration for the current V1 workflow.

* The selected V1 execution mechanism is non-interactive `codex exec`.

* Important CLI capabilities include:

  * structured JSON output using `--output-schema`

  * final-result persistence using `--output-last-message`

  * `--sandbox read-only`

  * ephemeral sessions

  * stdin input using `-`

* Sending the prompt through stdin is particularly important because the real portfolio is far too large to safely pass as a Windows command-line argument.

* Codex does not need filesystem access to the Professional Portfolio during Evidence Matching because Python already loads the portfolio and places the evidence into the prompt.

* The Codex process can therefore remain read-only for these structured reasoning stages.

---

## Reusable CodexStructuredRunner

* The first Codex adapter contained execution details directly inside the Evidence Matcher.

* Once the same execution mechanism was clearly required for four AI stages, the common behavior was extracted into `CodexStructuredRunner`.

* This was an appropriate abstraction because actual duplication and repeated future use were already demonstrated.

* `CodexStructuredRunner` owns provider-specific execution concerns:

  * JSON Schema creation

  * Codex-compatible schema transformation

  * temporary schema files

  * temporary result files

  * subprocess execution

  * sandbox selection

  * ephemeral execution

  * UTF-8 encoding

  * error handling

  * Pydantic reconstruction of the result

* Task-specific adapters now remain focused on their own domain responsibility.

* For example:

  `CodexJobAnalyzer`

  builds a job-analysis prompt and requests a `JobSpec`.

  `CodexEvidenceMatcher`

  builds an evidence-matching prompt and requests an `EvidenceMap`.

* This is a practical example of separating reusable infrastructure from domain-specific policy.

---

## Generic Structured AI Execution

* `CodexStructuredRunner.run()` is generic over Pydantic model types.

* Conceptually:

  `run(prompt, JobSpec) -> JobSpec`

  `run(prompt, EvidenceMap) -> EvidenceMap`

  `run(prompt, CVContentPlan) -> CVContentPlan`

  `run(prompt, CVDraft) -> CVDraft`

* The generic type parameter allows mypy to preserve the concrete output type.

* A single structured-execution mechanism can therefore serve multiple AI stages without losing type information.

* This is an example where generics provide direct practical value rather than being abstraction for its own sake.

---

## Pydantic JSON Schema vs Provider Schema Constraints

* A valid Pydantic-generated JSON Schema is not automatically guaranteed to be accepted by every structured-output provider.

* Codex rejected the original `EvidenceMap.model_json_schema()` because its structured-output implementation requires every object property to appear in the schema's `required` array.

* Pydantic normally omits fields with defaults from `required`.

* For example, a Python field such as:

  `breadth: list[str] = Field(default_factory=list)`

  is optional from Pydantic's construction perspective.

* Codex structured output instead expects the field to be explicitly returned, for example as an empty list.

* The domain model should not be distorted merely to satisfy one AI provider.

* Provider-specific schema compatibility therefore belongs in the provider adapter/infrastructure layer.

* The Codex runner recursively converts Pydantic schemas into the stricter form required by Codex.

* This preserves a clean boundary:

  domain model

  -> general Pydantic semantics

  -> provider adapter

  -> provider-compatible output schema

* This experience demonstrates that “supports JSON Schema” does not necessarily mean “supports every valid JSON Schema feature.”

---

## Windows Encoding and External Processes

* The synthetic Codex smoke tests initially worked because they contained only simple ASCII text.

* The real Professional Portfolio exposed a Windows encoding assumption when Unicode characters were passed to Codex through stdin.

* `subprocess.run(..., text=True)` may use a platform-default text encoding unless one is explicitly specified.

* The portfolio contains real UTF-8 content such as accented characters and typographic symbols.

* The subprocess boundary was therefore changed to:

  `encoding="utf-8"`

* Explicit encoding is preferable to silently replacing unsupported characters.

* Real-world integration data can expose operating-system assumptions that synthetic tests do not reveal.

---

## Unit Tests vs Real Integration Smoke Tests

* Unit tests for Codex adapters should not make real Codex calls.

* Normal pytest execution must remain:

  * fast

  * deterministic

  * offline from the AI provider

  * independent of account usage

* `monkeypatch` is used to replace external execution boundaries during unit tests.

* After `CodexStructuredRunner` was extracted, the test boundary became cleaner.

* Runner tests verify:

  * command construction

  * schema transformation

  * UTF-8 handling

  * result parsing

  * CLI error behavior

* Adapter tests verify:

  * task-specific prompt construction

  * the requested Pydantic output model

  * propagation of the structured result

* Real smoke tests separately verify that:

  * authentication works

  * Codex accepts the real schema

  * the CLI executes successfully

  * the AI produces plausible real outputs

* Unit tests and smoke tests therefore answer different questions and should not be conflated.

---

## Prompt Design and Deterministic Validation

* Structured output does not guarantee semantically valid application behavior.

* During the first real Nord Quantique pipeline run, Codex produced a schema-valid `CVContentPlan` that violated three evidence-alignment rules.

* Two plan items referenced job requirements using evidence scenarios that were semantically related but were not explicitly approved for those requirements in `EvidenceMap`.

* Another plan item targeted a machine-learning requirement whose Evidence Assessment had:

  * no approved scenario matches

  * `match_strength="unsupported"`

  * `claim_eligibility="none"`

* The planning validation gate rejected the plan and prevented `CVWriter` from running.

* This demonstrated the practical value of the previously designed deterministic validation architecture.

* The correct response was not to weaken the validator.

* Instead, the planner prompt was changed to explicitly mirror the deterministic software contract.

* The strengthened instruction requires:

  * every targeted requirement to have claim eligibility;

  * every targeted requirement to have at least one approved scenario match;

  * each planned item's evidence references to include at least one scenario explicitly approved for every requirement it targets.

* After that prompt correction, the real Nord Quantique plan passed with zero validation issues.

* This provides an important engineering lesson:

  > Prompts should communicate the same contract that deterministic validators enforce.

* AI output should be treated as untrusted structured input until deterministic application rules accept it.

---

## Persisted Artifacts and Stage-Level Recovery

* Persisting intermediate artifacts became valuable during the first real pipeline failure.

* `JobSpec` and `EvidenceMap` had already passed validation and were persisted.

* The invalid `CVContentPlan` was correctly not persisted.

* After correcting the planner prompt, there was no need to rerun Job Analysis or Evidence Matching.

* The saved valid `JobSpec` and `EvidenceMap` were reused to rerun only the planning stage.

* After planning passed, the Writer was run directly from the saved artifacts.

* This demonstrates why intermediate artifacts are more than debugging convenience.

* They enable:

  * targeted retries

  * faster iteration

  * reduced AI execution

  * reproducibility

  * inspection of stage boundaries

* Fail-fast validation plus intermediate persistence provides a simple form of resumable pipeline execution.

---

## Real CandidateProfile

* `CandidateProfile` is intentionally much smaller than the full Professional Portfolio.

* It stores stable canonical information such as:

  * identity

  * contact information

  * education

  * experiences

  * languages

* Skills, projects, technical accomplishments, limitations, and detailed evidence remain in the Professional Portfolio rather than being duplicated into `CandidateProfile`.

* This preserves the architectural distinction:

  `CandidateProfile`

  -> canonical stable facts

  `Professional Portfolio`

  -> rich evidence used for job-specific matching

* A real local `candidate_profile.json` has now been constructed, validated through Pydantic, persisted through `ArtifactStore`, reloaded, and verified through a round trip.

* Runtime candidate data and generated artifacts are excluded from Git.

---

## Real CodexJobAnalyzer

* `CodexJobAnalyzer` converts raw job-posting text into a structured `JobSpec`.

* Job Analysis remains candidate-independent.

* The analyzer should describe what the employer asks for rather than modifying its interpretation based on what the candidate happens to know.

* Real testing showed that Codex could successfully distinguish:

  * core responsibilities

  * required qualifications

  * preferred qualifications

  * experience expectations

  * education requirements

  * explicit source text

* Employer wording is preserved through `source_text`, maintaining provenance back to the original posting.

---

## Real CodexEvidenceMatcher

* `CodexEvidenceMatcher` receives both the validated `JobSpec` and the complete `PortfolioContext`.

* The matcher is responsible for identifying which documented evidence supports each requirement.

* It remains separate from filesystem access.

* It does not know how portfolio files were discovered.

* The matcher produced nuanced real results rather than simply labeling every related capability as a match.

* Unsupported requirements remained explicitly unsupported.

* Capability assessment and requirement match remained separate.

* This preserves the distinction between:

  > What the candidate has demonstrated.

  and:

  > How strongly that demonstrated capability satisfies this job requirement.

---

## Real CodexCVPlanner

* `CodexCVPlanner` receives:

  * `CandidateProfile`

  * `JobSpec`

  * `EvidenceMap`

* It decides what the CV should emphasize before the Writer produces final wording.

* Real planning for the Nord Quantique role emphasized:

  * scientific Python

  * instrumentation software

  * hardware automation

  * quantitative system characterization

  * multidisciplinary R&D

  * sustained technical ownership

* The planner also recorded prohibited implications such as:

  * commercial production-software experience

  * unsupported quantum-processor calibration experience

  * mature CI/CD practices

  * formal staff management

* This demonstrates why planning and writing are separate stages.

* The plan acts as a claim boundary and strategy document rather than leaving all content decisions to the final Writer.

---

## Real CodexCVWriter

* `CodexCVWriter` receives:

  * `CandidateProfile`

  * `EvidenceMap`

  * `CVContentPlan`

* It does not receive or reinterpret the raw job posting.

* Its responsibility is to turn the approved plan into concise CV wording.

* The first real Nord Quantique `CVDraft` included:

  * targeted professional summary

  * grouped technical skills

  * selected research experiences

  * evidence-backed experience bullets

  * education

  * languages

  * claim-level provenance

* The real draft passed all existing draft validation gates with zero issues.

* This confirms that the complete structured content-generation path is now operational on real data.

---

## Real End-to-End Content Pipeline Milestone

* The V1 content pipeline has now successfully processed a real current job posting.

* The tested workflow was:

  Real Nord Quantique job posting

  -> `CodexJobAnalyzer`

  -> validated `JobSpec`

  -> real 35-document Professional Portfolio

  -> `CodexEvidenceMatcher`

  -> validated `EvidenceMap`

  -> `CodexCVPlanner`

  -> validated `CVContentPlan`

  -> `CodexCVWriter`

  -> validated `CVDraft`

* The first planning attempt failed semantic validation, demonstrating that the safeguards were meaningful rather than theoretical.

* The failure was isolated, diagnosed, and corrected without rerunning previously valid upstream stages.

* The final real `CVContentPlan` and `CVDraft` both passed with zero validation issues.

* This marks completion of the structured content-generation portion of V1.

---

## Current Learning Phase: Deterministic Document Rendering

* The next problem is no longer AI reasoning.

* The next problem is converting an already validated `CVDraft` into a professional document.

* The intended boundary is:

  `CVDraft`

  -> deterministic renderer

  -> LaTeX source

  -> compiled PDF

* The renderer should control presentation rather than content strategy.

* Rendering concerns include:

  * page layout

  * typography

  * spacing

  * section hierarchy

  * page length

  * column structure

  * dates and alignment

* Separating Writer and Renderer allows the same validated content to be rendered through different templates without asking the AI to rewrite the CV.

* For V1, one reliable LaTeX template is preferable to a generalized rendering framework.

* The immediate success criterion is:

  Real job posting

  -> trustworthy evidence

  -> validated tailored content

  -> professional PDF

  -> usable for a real job application

* Additional RAG sophistication, CI/GitHub, packaging, alternative providers, richer CLI workflows, and retrieval experiments remain useful learning opportunities after the first usable V1 is complete.

## CV Rendering Lessons

### Rendering is distinct from content generation

`CVDraft` should describe CV content and provenance; the renderer should decide
how that structured information is presented.

This allowed presentation-specific transformations such as:

- `January 2011–December 2014` → `2011–2014` for education display;
- `native_or_bilingual` → `Native or bilingual`;
- compact degree labels such as `B.Eng.` and `B.Sc.`.

The canonical source data remains unchanged.

### Jinja2 and LaTeX syntax conflict

Default Jinja delimiters conflict with LaTeX syntax. The renderer therefore
uses custom delimiters:

- block: `((* ... *))`
- variable: `((( ... )))`
- comment: `((# ... #))`

This keeps the LaTeX template readable without escaping normal LaTeX braces.

### Provider output and presentation should remain separate

The Writer can generate structured values and concise CV content, while the
renderer handles purely visual/display transformations. Presentation fixes
should not be pushed into canonical candidate data or evidence.

### Avoid coupling background geometry to content geometry

The first sidebar implementation used a `\colorbox` containing a fixed-height
minipage. Because the box was unbreakable, adding content caused the entire
sidebar to move to page 2.

The better solution was to use `paracol`'s column background independently
from the naturally sized sidebar content.

General lesson:

> Decorative page geometry should not determine the size or pagination
> behavior of semantic content containers.

### Real-data rendering exposes issues fake data does not

The renderer looked correct with partial content, but the first complete real
CV exposed:

- excessive Education/Languages vertical usage;
- raw enum-like language values;
- canonical contact-data mistakes;
- fixed-height sidebar pagination failure;
- overly verbose skill wording.

Rendering against a real application is therefore part of system validation,
not merely visual polish.

### V1 layout principle

Once the renderer produces a stable, readable one-page CV, further gains
should come from improving content selection and wording rather than repeated
micro-adjustments to page geometry.