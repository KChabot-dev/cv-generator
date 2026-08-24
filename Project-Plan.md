## Current Phase

Document Generation / V1 Completion

The AI-independent architecture is now connected to the real Professional
Portfolio and real Codex adapters.

The content-generation pipeline has been exercised on a real Nord Quantique
job posting and successfully produced a validated, persisted `CVDraft`.

Current objective:

CVDraft
→ deterministic LaTeX rendering
→ compiled PDF
→ first usable tailored CV
→ test V1 on additional real job postings

The immediate priority remains completing a usable V1 for real job
applications before adding nonessential infrastructure or more advanced RAG
techniques.


## Completed

### Architecture and Design

- High-level CV generation pipeline
- Core data contracts
- Stable identifier strategy
- Missing-information handling
- Validation-gate architecture
- Evidence matching and claim-boundary design
- AI-provider-independent application ports
- Professional Portfolio full-context V1 access strategy
- Provider-specific AI execution isolated behind adapters
- Separation between structured CV content and document rendering


### Project Bootstrap

- Python 3.13 project
- uv dependency management
- Pydantic v2
- pytest
- Ruff
- mypy
- src-layout package structure
- Local Git workflow
- Codex CLI installation and ChatGPT-account authentication


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

- `PortfolioDocument`
  - stable portfolio source identifier
  - Markdown content

- `PortfolioContext`
  - collection of curated portfolio documents supplied to evidence matching


### Domain Testing

- Validation behavior
- Important failure modes
- Internal reference integrity
- JSON serialization/deserialization round trips
- Ruff, mypy, and pytest quality checks


### Cross-Model Validation

- `JobSpec` ↔ `EvidenceMap` requirement completeness and reference validation
- `PortfolioContext` ↔ `EvidenceMap` source-provenance validation
- `EvidenceMap` ↔ `CVContentPlan` reference and evidence-alignment validation
- Claim-eligibility enforcement
- `CVContentPlan` ↔ `CVDraft` plan-reference and claim-boundary validation
- `CandidateProfile` ↔ `CVDraft` canonical-fact validation
- Structured `ValidationIssue` model
- `ValidationReport` aggregation
- Pipeline-wide validation gates
- Aggregate valid and invalid pipeline tests
- Stop-on-validation-failure behavior verified on real AI output


### Intermediate Artifact Persistence

- Generic typed JSON save/load
- Automatic parent-directory creation
- Invalid JSON/schema handling
- Stable artifact directory layout
- Global `CandidateProfile` persistence
- Per-run `JobSpec`, `EvidenceMap`, `CVContentPlan`, `CVDraft`, and
  `ValidationReport`
- Original job posting retained with real runs
- `ArtifactStore` facade
- Filesystem persistence tests
- Real canonical `candidate_profile.json` created and validated


## Application Services — Completed

Implemented:

- AI-provider-independent application ports using `Protocol`
  - `JobAnalyzer`
  - `EvidenceMatcher`
  - `CVPlanner`
  - `CVWriter`

- Job analysis orchestration and persistence
- Evidence matching, validation, and persistence
- CV content planning, validation, and persistence
- CV draft writing, validation, and persistence
- CandidateProfile-to-CVContentPlan source-reference validation
- End-to-end pipeline orchestration
- Pipeline stop-on-validation-failure behavior
- End-to-end happy-path and failure-path tests
- Shared test factories and `ArtifactStore` fixture


### Professional Portfolio Integration — Completed for V1

Implemented:

- `MarkdownPortfolioLoader`
- Explicit curated evidence-directory allowlist
- Recursive Markdown discovery
- README exclusion
- Empty-document exclusion
- Stable repository-relative source identifiers
- Deterministic document ordering
- UTF-8 portfolio loading
- Missing-root handling
- Portfolio provenance supplied to `EvidenceMatcher`
- Portfolio source-reference validation against generated `EvidenceMap`

The current local Professional Portfolio contains 35 curated non-empty Markdown
documents used by the V1 Evidence Matcher.

The full-context strategy was tested successfully on the real portfolio.
Codex produced a structured `EvidenceMap` using evidence across skills,
projects, experiences, and code-audit documents.

No embeddings, vector database, or job-specific retrieval-ranking system is
required for V1 based on the current empirical result.


### Codex Integration — Completed for V1

Implemented:

- Codex CLI installed locally
- Authentication through the existing ChatGPT account
- Non-interactive execution using `codex exec`
- `CodexStructuredRunner`
  - generic Pydantic-model output support
  - Pydantic JSON Schema generation
  - Codex-compatible strict-schema transformation
  - temporary schema and result files
  - read-only sandbox
  - ephemeral Codex sessions
  - prompt input through stdin
  - explicit UTF-8 subprocess encoding
  - structured error handling
  - Pydantic validation of returned JSON

Real AI adapters:

- `CodexJobAnalyzer`
- `CodexEvidenceMatcher`
- `CodexCVPlanner`
- `CodexCVWriter`

Each adapter contains task-specific prompt logic while reusing the common
Codex execution layer.

Unit tests use mocked runner/subprocess boundaries so the normal pytest suite
does not invoke real Codex calls.


### Real-World Integration Validation

The system has been tested using a real current job posting:

`Senior Software Developer (level 3) – Calibration & Device Intelligence`
at Nord Quantique.

Successful real stages:

Job posting
→ `CodexJobAnalyzer`
→ validated `JobSpec`

Real Professional Portfolio
→ `CodexEvidenceMatcher`
→ validated `EvidenceMap`

Validated `JobSpec` + `EvidenceMap` + `CandidateProfile`
→ `CodexCVPlanner`
→ validated `CVContentPlan`

Validated plan + evidence + canonical profile
→ `CodexCVWriter`
→ validated `CVDraft`

The first real pipeline run also demonstrated the value of the validation
architecture:

- the initial AI-generated content plan contained three evidence-alignment
  violations;
- the planning validation gate rejected the plan and prevented downstream CV
  writing;
- the planner instructions were tightened to mirror the deterministic
  evidence-alignment contract;
- the planner was rerun using the already-persisted `JobSpec` and
  `EvidenceMap`;
- the corrected plan passed with zero validation issues;
- the resulting real `CVDraft` also passed all draft validation gates with
  zero issues and was persisted.

This provides an empirical demonstration that structured AI output alone is
not sufficient and that deterministic validation gates are necessary.


### Current Pipeline

Job posting text

→ `CodexJobAnalyzer`

→ `JobSpec`

→ `MarkdownPortfolioLoader`

→ `PortfolioContext`

→ `CodexEvidenceMatcher`

→ `EvidenceMap`

→ `CodexCVPlanner`

→ `CVContentPlan`

→ `CodexCVWriter`

→ `CVDraft`

Each structured stage is validated before downstream processing.

Intermediate artifacts are persisted locally for inspection, debugging, and
reuse when a downstream stage must be rerun.


## Next Phase — Document Generation / V1 Completion

Goal:

Convert a validated `CVDraft` into a professional, usable PDF CV and complete
the first working V1.

Immediate tasks:

1. Verify the available local LaTeX compiler/toolchain.
2. Define one deterministic V1 CV layout/template.
3. Implement a LaTeX renderer for `CVDraft`.
4. Generate a `.tex` document from the real Nord Quantique draft.
5. Compile the document to PDF.
6. Review content density, page length, readability, and visual hierarchy.
7. Make only the rendering/content adjustments required for a usable V1.
8. Run the complete workflow on several additional real job postings.
9. Confirm that the generated CVs remain grounded, relevant, and practical
   for real applications.

V1 success criterion:

Real job posting
→ trustworthy portfolio evidence
→ tailored and validated CV content
→ rendered usable PDF
→ fast enough to repeat for actual job applications


## After V1 / Continued Upskilling

Once the first usable CV-generator workflow is complete and job applications
have started, continue improving the project incrementally.

Potential follow-up work:

- GitHub remote repository
- CI with Ruff, mypy, and pytest
- improved command-line interface
- simplified job-posting input workflow
- automated run naming and application tracking
- improved opportunity-fit reporting
- additional rendering templates
- prompt evaluation and regression cases
- stronger provenance validation where useful
- selective portfolio retrieval if full-context performance later becomes a
  demonstrated limitation
- embeddings or vector retrieval only if empirical evaluation justifies them
- experimentation with additional LLM/provider integrations
- packaging and distribution improvements
- broader test coverage and integration tests