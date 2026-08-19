# Decisions

## D001 — Structured Data Models

### Decision

Use typed Python data models to represent the major objects exchanged between pipeline stages.

Pydantic is the preferred implementation for these models.

Major models are expected to include:

- `CandidateProfile`
- `JobSpec`
- `EvidenceMap`
- `CVContentPlan`
- `CVDraft`

JSON will be used as a serialized representation when intermediate artifacts need to be stored, inspected, tested, or exchanged.

### Rationale

The CV Generator consists of multiple stages that exchange structured information. Explicit models provide clearer contracts between these stages than unstructured dictionaries.

Pydantic provides runtime data validation and can generate structured schemas that integrate directly with OpenAI Structured Outputs.

This allows the same conceptual data contract to be used by both the Python application and AI-generated structured outputs.

### Important Limitation

Schema validation ensures that data has the expected structure and types.

It does not guarantee that AI-generated content is factually or semantically correct.

The validation gates defined in `Architecture.md` remain responsible for verifying evidence, meaning, and business rules.

## D002 — Persist Intermediate Pipeline Artifacts

### Decision

Persist the major structured outputs produced by the CV-generation pipeline as JSON files during development and CV generation.

Expected intermediate artifacts include:

* `job_spec.json`
* `evidence_map.json`
* `cv_content_plan.json`
* `cv_draft.json`

Additional artifacts may be introduced later when they provide useful traceability or diagnostic value.

### Rationale

The pipeline consists of several transformations, and errors should be traceable to the stage that introduced them.

Persisting intermediate artifacts makes it possible to:

* inspect the output of each pipeline stage;
* identify where an incorrect interpretation or claim was introduced;
* test individual stages independently;
* reproduce failures;
* compare outputs after changing prompts, rules, models, or code;
* support regression testing and evaluation;
* maintain traceability between job requirements, portfolio evidence, CV content, and the final document.

JSON is appropriate because the intermediate artifacts are structured machine-readable data rather than narrative documentation.

Pydantic models can be serialized to and reconstructed from JSON, allowing the persisted artifacts to remain aligned with the application's typed data models.

### Important Distinction

JSON files represent the serialized state of structured pipeline data.

Markdown remains the preferred format for human-oriented project documentation such as architecture, decisions, and learning notes.

### Development Principle

Intermediate artifacts are primarily intended to improve observability, debugging, testing, and reproducibility.

If later testing shows that persisting a particular artifact provides no practical value, it does not need to be retained permanently.

## D003 — AI Structured Outputs

### Decision

Use OpenAI Structured Outputs for AI pipeline stages that are expected to produce structured application data.

The expected output structure will be defined using the application's Pydantic models.

### Rationale

Pipeline stages such as Job Analysis, Evidence Matching, CV Planning, and CV Writing need to exchange predictable structured data.

Allowing AI models to invent arbitrary dictionaries or free-form JSON would make downstream processing unreliable.

Structured Outputs allows the application to require AI responses that conform to predefined schemas.

Conceptually:

```text
Pydantic Model
      ↓
Structured Output Schema
      ↓
OpenAI Model
      ↓
Structured Response
      ↓
Pydantic Validation
```

This ensures structural consistency across repeated AI calls and allows downstream pipeline components to rely on known data contracts.

### Important Limitation

Structured Outputs guarantees adherence to the expected structure, not factual or semantic correctness.

A structurally valid output may still contain an incorrect interpretation.

Semantic validation, provenance checks, evidence rules, and other validation mechanisms defined in the architecture remain necessary.

## D004 — Professional Portfolio Access Strategy

### Decision

Use the relevant Professional Portfolio documentation as full-context input to the Evidence Matching stage during the initial implementation.

The Evidence Matcher will receive:

* the `Validated JobSpec`;
* the relevant Markdown documents from the Professional Portfolio;
* document identifiers required to preserve provenance.

A vector database or semantic-retrieval system will not be introduced initially.

### Rationale

Evidence Matching is responsible for determining whether documented candidate experience supports the requirements contained in the `Validated JobSpec`.

Because the Professional Portfolio is currently small enough to fit within the available model context, providing the complete relevant documentation avoids introducing an additional retrieval layer that could fail to surface important evidence.

The initial flow is therefore:

```text
Validated JobSpec
        +
Relevant Professional Portfolio
        ↓
Evidence Matcher
        ↓
Candidate Evidence Map
```

rather than:

```text
Validated JobSpec
        +
Professional Portfolio
        ↓
Chunking
        ↓
Embeddings
        ↓
Vector Database
        ↓
Similarity Retrieval
        ↓
Selected Chunks
        ↓
Evidence Matcher
```

The simpler approach provides several advantages:

* reduces implementation complexity;
* avoids retrieval errors during the initial version;
* allows the model to consider relationships between different skills, experiences, and projects;
* makes Evidence Matching easier to evaluate independently;
* preserves access to evidence that might not appear semantically similar to the wording of the job posting;
* provides a simpler baseline against which more advanced retrieval strategies can later be compared.

### Relevant Portfolio Context

Full-context access does not mean that every file in the repository must be included.

The system should load the curated Professional Portfolio documentation relevant to professional evidence, such as:

* profile information;
* experiences;
* projects;
* skills;
* documented code audits;
* other evidence-oriented Markdown documents.

Raw source code, binary files, and unrelated repository content should not automatically be included.

The curated Markdown documentation remains the primary evidence layer.

### Provenance

Portfolio documents must retain stable identifiers or source references when provided to the Evidence Matcher.

Every proposed evidence match should therefore be traceable back to the document or documents from which it originated.

### Future Evolution

Full-context processing is an initial strategy, not a permanent architectural requirement.

If evaluation later shows that the portfolio becomes:

* too large for efficient full-context processing;
* too expensive to repeatedly process;
* difficult for the model to reason over reliably;
* slow enough to affect practical use;

the access strategy may be replaced or supplemented with retrieval techniques such as:

* keyword search;
* semantic/vector retrieval;
* hybrid retrieval;
* hierarchical summaries;
* selective context construction.

A more complex retrieval system should be introduced only when testing demonstrates that it improves the system over the simpler full-context baseline.

### Design Principle

Do not introduce retrieval infrastructure simply because the application resembles a RAG system.

Use the simplest portfolio-access strategy that reliably exposes the evidence required for accurate matching.

