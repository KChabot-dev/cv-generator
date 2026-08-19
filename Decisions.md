# Decisions

## D001 — Structured Data Models

### Decision

Use typed Python data models to represent the major objects exchanged between pipeline stages.

Pydantic is the preferred implementation for these models.

Major models are expected to include:

* `CandidateProfile`
* `JobSpec`
* `EvidenceMap`
* `CVContentPlan`
* `CVDraft`

JSON will be used as a serialized representation when intermediate artifacts need to be stored, inspected, tested, or exchanged.

### Rationale

The CV Generator consists of multiple stages that exchange structured information. Explicit models provide clearer contracts between these stages than unstructured dictionaries.

Pydantic provides runtime data validation and can generate JSON Schemas from the application's data models.

This allows the same conceptual data contracts to be used by the Python application and by AI components that support schema-constrained structured outputs.

### Important Limitation

Schema validation ensures that data has the expected structure and types.

It does not guarantee that AI-generated content is factually or semantically correct.

The validation gates defined in `Architecture.md` remain responsible for verifying evidence, meaning, provenance, and business rules.

---

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

---

## D003 — Schema-Constrained AI Outputs

### Decision

Require AI pipeline stages that produce structured application data to return outputs conforming to predefined schemas.

The application's Pydantic models will define the expected data structures and will be used to generate the corresponding JSON Schemas.

For the initial Codex-based implementation, these schemas will be supplied to Codex when structured output is required.

### Rationale

Pipeline stages such as Job Analysis, Evidence Matching, CV Planning, and CV Writing need to exchange predictable structured data.

Allowing the AI system to invent arbitrary dictionaries, field names, or free-form JSON would make downstream processing unreliable.

Conceptually:

```text
Pydantic Model
      ↓
JSON Schema
      ↓
AI Execution Backend
      ↓
Schema-Constrained Response
      ↓
Pydantic Validation
```

This ensures structural consistency across repeated AI calls and allows downstream components to rely on known data contracts.

It also keeps the application's internal models independent from a specific AI provider or execution mechanism.

### Initial Implementation

The initial implementation will use Codex as the AI execution backend.

Codex can receive a JSON Schema when structured output is required, allowing the application to request results that conform to the application's expected data structure.

The resulting structured response will subsequently be validated by Pydantic before being accepted by the Python application.

### Important Limitation

Schema-constrained output guarantees adherence to the expected structure, not factual or semantic correctness.

For example, the following could be structurally valid:

```text
Skill: Python
Requirement Type: Required
Expected Level: Expert
```

while still being semantically incorrect if the original job posting never stated or implied expert-level proficiency.

The validation gates defined in `Architecture.md` therefore remain responsible for verifying:

* semantic correctness;
* source grounding;
* provenance;
* evidence strength;
* factual fidelity;
* other application-specific rules.

---

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

Raw source code, binary files, generated files, and unrelated repository content should not automatically be included.

The curated Markdown documentation remains the primary evidence layer.

### Provenance

Portfolio documents must retain stable identifiers or source references when provided to the Evidence Matcher.

Every proposed evidence match should therefore be traceable back to the document or documents from which it originated.

Conceptually:

```text
Job Requirement
      ↓
Evidence Match
      ↓
Portfolio Document
      ↓
Supporting Passage
```

The Evidence Matcher should not produce an evidence claim that cannot be associated with identifiable source material.

### Future Evolution

Full-context processing is an initial strategy, not a permanent architectural requirement.

If evaluation later shows that the portfolio becomes:

* too large for efficient full-context processing;
* too resource-intensive or inefficient to repeatedly process;
* difficult for the model to reason over reliably;
* slow enough to affect practical use;

the access strategy may be replaced or supplemented with retrieval techniques such as:

* keyword search;
* semantic/vector retrieval;
* hybrid retrieval;
* hierarchical summaries;
* selective context construction.

A more complex retrieval system should be introduced only when testing demonstrates that it improves the system over the simpler full-context baseline.

### Future Local-LLM Extension

A later version of the project may introduce a local LLM and local retrieval pipeline.

This could provide an opportunity to explore technologies and concepts such as:

* local model inference;
* embeddings;
* semantic retrieval;
* hierarchical document indexing;
* context construction;
* hybrid search;
* local structured outputs;
* evaluation of local models against the Codex-based baseline.

This extension is not required for the initial CV Generator version and should not delay delivery of a usable V1.

### Design Principle

Do not introduce retrieval infrastructure simply because the application resembles a RAG system.

Use the simplest portfolio-access strategy that reliably exposes the evidence required for accurate matching.

More complex retrieval or local-LLM infrastructure should be introduced when it solves a demonstrated problem or provides a clearly defined learning objective.
## D005 — AI Execution Backend

### Decision

Use Codex authenticated through the user's ChatGPT subscription as the primary AI execution backend for the initial version of the CV Generator.

The Python application should access Codex through a dedicated application-level adapter rather than allowing Codex-specific logic to spread throughout the pipeline.

Conceptually:

```text
CV Generator
      ↓
LLM / AI Backend Interface
      ↓
Codex Adapter
      ↓
Codex
```

The initial Codex adapter may use either the official Codex Python SDK or the non-interactive Codex CLI, depending on which provides the simplest reliable support for the required structured-output workflow.

### Authentication

Codex will use ChatGPT-account authentication for normal local operation.

This allows the CV Generator to use Codex within the usage available through the user's ChatGPT subscription rather than requiring usage-based OpenAI API-key billing.

API-key authentication is not a requirement for normal V1 operation.

### Rationale

Separating the AI execution backend from the rest of the application prevents the CV-generation pipeline from depending directly on one execution mechanism.

Pipeline components should request capabilities such as structured generation without needing to know whether the underlying implementation uses:

* the Codex Python SDK;
* `codex exec`;
* a future local LLM;
* another compatible AI backend.

This makes the system easier to test, maintain, and extend.

### Initial Backend Evaluation

Before finalizing the Codex adapter implementation, compare the Codex Python SDK and `codex exec` for the specific needs of the project, including:

* schema-constrained structured output;
* Pydantic integration;
* error handling;
* authentication reuse;
* observability;
* testability;
* implementation complexity.

Prefer the simplest option that satisfies the application's requirements.

### Future Extension

A later `LocalLLMProvider` or equivalent backend may be added without changing the domain-level CV-generation pipeline.

This future backend could support local inference, retrieval, embeddings, and comparison against the Codex-based baseline.

### Design Principle

Pipeline logic should depend on the capabilities required from an AI backend, not directly on provider-specific implementation details.
