## Current Phase

V1 Validation / Real Application Testing

The complete CV-generation pipeline is now operational on the first real
application case.

The system has successfully transformed a real Nord Quantique job posting and
the real Professional Portfolio into:

Job posting

→ validated `JobSpec`

→ provenance-aware `EvidenceMap`

→ validated `CVContentPlan`

→ validated `CVDraft`

→ deterministic LaTeX rendering

→ compiled one-page PDF CV

The immediate objective is now to refine the first generated CV where useful
and exercise the complete workflow on additional real job postings.

Repeated applications will be used to identify which remaining limitations are
systematic enough to justify additional automation, validation, repair logic,
or retrieval complexity.

The priority remains starting real job applications with a usable V1 rather
than adding infrastructure before an observed need exists.


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
  - canonical candidate-entity provenance through `source_entity_refs`
  - separation between portfolio-document provenance and candidate-entity
    ownership
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
- `EvidenceMap` scenario-to-canonical-entity provenance validation during
  planning
- `EvidenceMap` ↔ `CVContentPlan` experience-ownership validation preventing
  evidence from one candidate experience from being transferred to another
- `EvidenceMap` ↔ `CVContentPlan` reference and evidence-alignment validation
- Claim-eligibility enforcement
- `CVContentPlan` ↔ `CVDraft` plan-reference and claim-boundary validation
- `CandidateProfile` ↔ `CVDraft` canonical-fact validation
- Structured `ValidationIssue` model
- `ValidationReport` aggregation
- Pipeline-wide validation gates
- Aggregate valid and invalid pipeline tests
- Stop-on-validation-failure behavior verified on real AI output
- Experience/evidence provenance mismatch detected deterministically before
  CV writing


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
- `CandidateProfile` supplied to `EvidenceMatcher` so generated evidence
  scenarios can reference canonical candidate entity IDs
- CV content planning, validation, and persistence
- CV draft writing, validation, and persistence
- CandidateProfile-to-CVContentPlan source-reference validation
- EvidenceScenario-to-CVContentPlan entity-provenance validation
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
- Canonical `CandidateProfile` entity identifiers supplied alongside portfolio
  evidence
- Evidence scenarios can distinguish where evidence was documented from which
  canonical candidate experience or education record it belongs to
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

Prompt constraints were refined during the first real application to mirror
important domain and cross-model contracts, including:

- unsupported requirements cannot retain scenario matches;
- requirement references on planned content must have explicitly approved
  supporting evidence;
- evidence from one canonical candidate experience must not be reassigned to
  another experience;
- quantitative and technical facts must retain their original meaning when
  compressed for CV use.

These prompt constraints improve generation reliability, while deterministic
domain and cross-model validation remains responsible for enforcing critical
invariants.

### Real-World Integration Validation

The complete V1 workflow has been tested using a real current job posting:

`Senior Software Developer (level 3) – Calibration & Device Intelligence`

at Nord Quantique.

Successful real stages:

Job posting

→ `CodexJobAnalyzer`

→ validated `JobSpec`

Real Professional Portfolio + canonical `CandidateProfile`

→ `CodexEvidenceMatcher`

→ validated provenance-aware `EvidenceMap`

Validated `JobSpec` + `EvidenceMap` + `CandidateProfile`

→ `CodexCVPlanner`

→ validated `CVContentPlan`

Validated plan + evidence + canonical profile

→ `CodexCVWriter`

→ validated `CVDraft`

Validated `CVDraft`

→ `LaTeXCVRenderer`

→ LuaLaTeX/latexmk

→ usable one-page PDF CV

The real application run exposed several important failure modes and validated
the layered safety architecture.

First, an AI-generated content plan contained requirement/evidence-alignment
violations. The planning validation gate rejected the plan and prevented
invalid downstream writing.

A later planning experiment exposed a more important provenance problem:
undergraduate LabVIEW and instrumentation evidence could be considered highly
relevant to the target job and incorrectly transferred by the planner into the
graduate-research experience.

The architecture was strengthened by:

- adding `source_entity_refs` to `EvidenceScenario`;
- supplying `CandidateProfile` to `EvidenceMatcher`;
- distinguishing portfolio-document provenance from canonical candidate-entity
  ownership;
- adding deterministic planning validation that verifies an experience item
  uses evidence attributable to that same candidate experience.

The regenerated real `EvidenceMap` correctly attributed:

- graduate Python, signal-processing, SPR-platform, biosensor, and
  collaboration evidence to `EXP-001`;
- undergraduate LabVIEW and scientific-instrument-control evidence to
  `EXP-002`;
- education evidence to the corresponding `EDU-*` records.

A subsequent planner run initially produced two requirement/evidence-alignment
violations. These were rejected by the existing deterministic validator.

After tightening the planner instructions to treat approved
requirement/scenario relationships as strict lookup constraints, the next plan
passed with zero validation issues.

The resulting `CVDraft` also passed all draft validation gates with zero
issues.

The final draft was rendered successfully as a professional one-page PDF.

This real integration exercise demonstrated that:

- schema-constrained AI output is useful but not sufficient;
- prompt instructions improve generation reliability but do not guarantee
  correctness;
- critical provenance and cross-stage relationships should be enforced
  deterministically;
- persisted intermediate artifacts make it possible to rerun only the stage
  that requires correction rather than restarting the entire pipeline.


### Current Pipeline

Job posting text

→ `CodexJobAnalyzer`

→ `JobSpec`

→ `MarkdownPortfolioLoader`

→ `PortfolioContext`
`CandidateProfile` + `JobSpec` + `PortfolioContext`
→ `CodexEvidenceMatcher`

→ `EvidenceMap`

→ `CodexCVPlanner`

→ `CVContentPlan`

→ `CodexCVWriter`

→ `CVDraft`

→ `LaTeXCVRenderer`

→ `.tex`

→ LuaLaTeX/latexmk

→ PDF CV

Each structured stage is validated before downstream processing.

Intermediate artifacts are persisted locally for inspection, debugging, and
reuse when a downstream stage must be rerun.


## Next Phase — V1 Validation on Additional Applications

Goal:

Use the complete V1 workflow for real job applications and determine which
remaining limitations are systematic enough to justify additional engineering.

Immediate tasks:

1. Refine the first Nord Quantique CV where useful for content density,
   software-engineering positioning, and readability.

2. Test PDF text extraction and ATS readability.

3. Run the complete workflow on additional real job postings.

4. Compare generated evidence selection, planning, wording, and document
   structure across different target roles.

5. Observe how often AI stages fail deterministic validation during repeated
   use.

6. Add bounded automated repair/retry behavior only if repeated applications
   show that manual reruns are a meaningful workflow limitation.

7. Improve the repeated-application interface, run naming, or LaTeX compilation
   workflow where this provides clear practical value.

8. Begin using generated CVs for real applications while continuing to improve
   the system incrementally.

V1 success criterion:

Real job posting

→ trustworthy portfolio evidence

→ tailored and validated CV content

→ rendered usable PDF

→ fast enough to repeat for actual job applications

This criterion has now been demonstrated once on the Nord Quantique
application. The next objective is to demonstrate repeatability across
additional real postings.

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

- validator-guided AI repair/retry if repeated real applications demonstrate a
  practical need

### CV Rendering — V1 operational

Status: Implemented and validated on the first real job application.

The pipeline can now transform a validated `CVDraft` into a usable one-page
PDF CV through a Jinja2 + LaTeX rendering layer.

Implemented:

- `LaTeXCVRenderer` converts `CVDraft` into a `.tex` document.
- Jinja2 uses custom delimiters to avoid collisions with LaTeX syntax.
- LuaLaTeX/latexmk is used for PDF compilation.
- The template uses a professional two-column layout:
  - left sidebar for contact, skills, education, and languages;
  - main column for profile and work experience.
- Contact information is populated from canonical `CandidateProfile` data.
- Education dates are displayed compactly by year while retaining the more
  precise canonical source values.
- Structured language proficiency values are converted to human-readable
  display labels.
- The sidebar background is implemented using the `paracol` column
  background rather than a fixed-height content box, keeping background
  geometry independent from sidebar content height.
- The first real Nord Quantique CV renders successfully as a one-page PDF.

Current boundary:

The basic V1 renderer/layout is considered operational. Further work should
focus primarily on generated content quality rather than page geometry.

Next:

1. Refine generated content where useful for concision and target-role
   positioning.

2. Reduce undesirable automatic word hyphenation in the rendered CV.

3. Validate PDF text extraction / ATS readability.

4. Exercise the renderer on additional real application drafts.

5. Automate the LaTeX compilation step if useful for the repeated-application
   workflow.