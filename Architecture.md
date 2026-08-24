# Architecture

## System Overview

The CV Generator transforms a job posting and the Professional Portfolio into a tailored, evidence-based CV in PDF format.

### Inputs

- Job posting
- Professional Portfolio

### Primary Output

- Tailored CV in PDF format

The Professional Portfolio serves two distinct purposes:

1. **Evidence source** — documented skills, experiences, projects, accomplishments, code audits, and supporting material used to determine what can truthfully be claimed.

2. **Canonical candidate data** — stable factual information such as name, contact information, education, official titles, organizations, dates, professional links, and languages.

These two types of information should not be treated in the same way.

Canonical information should normally be retrieved deterministically.

Professional evidence may require semantic interpretation, aggregation, and validation.

---

# High-Level Pipeline

```text
                         PROFESSIONAL PORTFOLIO
                           /               \
                          /                 \
                         ↓                   ↓
                Candidate Profile       Evidence Source
                         │                   │
                         │                   │
JOB POSTING              │                   │
    ↓                    │                   │
Job Analysis             │                   │
    ↓                    │                   │
JobSpec                  │                   │
    ↓                    │                   │
JobSpec Validation       │                   │
    ↓                    │                   │
Validated JobSpec        │                   │
    │                    │                   │
    └──────────────→ Evidence Matching ←─────┘
                         ↓
                Candidate Evidence Map
                         ↓
                Evidence Validation
                         ↓
                Validated Evidence Map
                         ↓
                    CV Planning
                         ↑
                         │
                 Candidate Profile
                         │
                         ↓
                  CV Content Plan
                         ↓
                    CV Writing
                         ↓
                Tailored CV Content
                         ↓
Candidate Profile ─→ CV Draft Assembly
                         ↑
                         │
                  CV Content Plan
                         ↓
                Structured CV Draft
                         ↓
                CV Draft Validation
                         ↓
                 Validated CV Draft
                         ↓
                    Render Adapter
                         ↓
                      Renderer
                         ↓
                      CV PDF
                         ↓
               Document Validation
                         ↓
                     FINAL CV
```

The pipeline separates:

- understanding the employer;
- identifying candidate evidence;
- determining what capability the combined evidence actually demonstrates;
- comparing that demonstrated capability with individual job requirements;
- deciding what deserves space in the CV;
- writing targeted professional content;
- inserting canonical candidate information;
- validating factual fidelity;
- rendering and validating the final document.

Each stage has a specific responsibility and should not perform work that belongs to another stage.

---

# Relationship to Data Models

This document describes:

> how the system is organized and how information moves through it.

`Data-Models.md` describes:

> what the major structured objects contain.

The major domain objects are:

```text
CandidateProfile
JobSpec
EvidenceMap
CVContentPlan
CVDraft
```

Their detailed conceptual structures should not be duplicated unnecessarily in this architecture document.

The exact Pydantic implementation will be defined in the Python code.

---

# 0. Candidate Profile

```text
Professional Portfolio
        ↓
Candidate Profile Extraction / Loading
        ↓
CandidateProfile
```

## Purpose

Provide a single source of truth for stable factual candidate information.

This may include:

- name;
- contact information;
- professional location;
- professional links;
- education and credentials;
- official experience titles;
- organizations;
- employment or research dates;
- languages;
- other stable information required by CV generation.

The Candidate Profile should remain independent from a specific job application.

It may be updated when the Professional Portfolio changes, but it should not need to be recreated from scratch for every application.

## Design Principle

Stable facts should be retrieved rather than regenerated whenever possible.

For example:

```text
CandidateProfile
    ↓
official title
organization
dates
    ↓
CVDraft
```

is preferable to:

```text
CandidateProfile
    ↓
AI rewrites factual information
    ↓
CVDraft
```

AI may transform presentation when necessary, but must not alter the underlying factual meaning.

---

# 1. Job Analysis

```text
Job Posting
    ↓
Job Analyzer
    ↓
JobSpec
    ↓
JobSpec Validation Gate
    ↓
Validated JobSpec
```

## Input

The original unstructured job posting.

## Purpose

Transform the posting into a structured representation of what the employer is actually asking for.

The Job Analyzer should identify information such as:

- role information;
- responsibilities;
- technical requirements;
- software-engineering practices;
- domain knowledge;
- education requirements;
- experience requirements;
- collaboration expectations;
- language requirements;
- employment constraints;
- required versus preferred qualifications;
- explicitly stated proficiency expectations;
- source evidence from the original posting.

Individual employer expectations should be represented as identifiable job requirements so that later stages can evaluate them independently.

## Output

`JobSpec`

After validation:

`Validated JobSpec`

## JobSpec Validation

The JobSpec Validation Gate verifies both structural validity and semantic fidelity.

Validation may include:

- schema validation;
- required-field checks;
- source traceability;
- deterministic rules;
- semantic comparison against the original posting.

The validator should detect problems such as:

- omitted important requirements;
- invented requirements;
- required qualifications being converted into preferred ones or vice versa;
- invented proficiency levels;
- distorted experience requirements;
- unsupported interpretation.

For example:

```text
Posting:
"Experience with Python"

Invalid interpretation:
"Advanced Python expertise required"
```

A structurally valid object is not automatically a semantically valid interpretation.

Because errors introduced here propagate through the rest of the pipeline, JobSpec semantic validation is a mandatory V1 trust boundary.

---

# 2. Evidence Matching

```text
Validated JobSpec
        +
Professional Portfolio Evidence
        ↓
Evidence Matcher
        ↓
Candidate Evidence Map
        ↓
Evidence Validation Gate
        ↓
Validated Evidence Map
```

## Inputs

### Validated JobSpec

The validated representation of employer requirements.

### Professional Portfolio Evidence

Curated professional evidence including:

- skills;
- professional and research experience;
- projects;
- technical accomplishments;
- scientific work;
- software-development experience;
- publications and presentations when relevant;
- code audits;
- documented autonomy or responsibility;
- other supporting professional evidence.

The strategy used to provide portfolio context to the matcher is defined separately in `Decisions.md`.

---

## Purpose

Determine what documented candidate evidence corresponds to each relevant employer requirement.

The matching stage must answer more than:

> Can I find one related sentence?

It should determine:

> What distinct evidence scenarios exist, what capability do they collectively demonstrate, and how well does that demonstrated capability satisfy this specific requirement?

---

# 2.1 Evidence Collection

For each relevant job requirement, the Evidence Matcher should search for all materially relevant evidence rather than stopping after the first plausible correspondence.

Conceptually:

```text
Job Requirement
        ↓
Relevant Portfolio Material
        ↓
Distinct Evidence Scenarios
```

For example:

```text
Requirement:
OpenCV experience

Possible evidence scenarios:
- interactive ROI-selection tool;
- mask and contour processing;
- thresholding workflows;
- image/video I/O;
- scientific visualization.
```

A single requirement may therefore be supported by several distinct experiences.

---

# 2.2 Evidence Scenario Grouping

Multiple portfolio documents may describe the same underlying work.

For example:

```text
Skills document
Project document
Code audit
README
```

may all describe one implementation.

These references should not automatically be counted as independent evidence.

Conceptually:

```text
Several source references
        ↓
same real activity
        ↓
One Evidence Scenario
```

Multiple sources may increase confidence that the scenario is well documented, but they must not artificially increase demonstrated breadth or depth.

This prevents double counting.

---

# 2.3 Capability Assessment

After relevant evidence scenarios have been identified, the system should determine what capability they collectively demonstrate.

Important dimensions include:

```text
depth
breadth
repetition
autonomy
context
confidence
```

These dimensions must remain conceptually separate.

For example:

```text
Several basic OpenCV uses
        ↓
Depth: BASIC
Breadth: MODERATE
Repetition: HIGH
Confidence: HIGH
```

should not automatically become:

```text
Depth: ADVANCED
```

Repeated use increases evidence of familiarity and confidence, but does not necessarily increase technical sophistication.

Likewise, a single technically substantial scenario may demonstrate more depth than several trivial scenarios.

The capability assessment therefore evaluates the nature of the work rather than simply counting occurrences.

---

# 2.4 Requirement Matching

Once the candidate capability has been characterized, it is compared with the specific employer requirement.

Conceptually:

```text
Demonstrated Capability
        +
Job Requirement
        ↓
Requirement Match
```

A preliminary match classification is:

```text
STRONG
PARTIAL
WEAK
UNSUPPORTED
```

### STRONG

The demonstrated capability directly satisfies the requirement or a clearly equivalent expectation.

### PARTIAL

Meaningful portions of the requirement are supported, but important elements remain undocumented.

### WEAK

A conceptual relationship exists, but representing the requested capability as direct experience would be misleading.

### UNSUPPORTED

No adequate documented evidence supports the requirement.

The system must be allowed to return `UNSUPPORTED`.

---

## Same Evidence, Different Requirement

Match strength is application-specific.

For example:

```text
Demonstrated capability:
Working practical OpenCV experience in scientific image processing.
```

Employer A:

```text
"Familiarity with OpenCV"
```

may produce:

```text
STRONG
```

while Employer B:

```text
"Advanced OpenCV expertise for real-time
object detection and tracking"
```

may produce:

```text
PARTIAL
or
WEAK
```

The candidate evidence has not changed.

The employer requirement has.

---

# 2.5 Claim Boundaries

Evidence strength and CV claim permission are related but are not identical.

For example:

```text
STRONG
→ direct wording may generally be allowed

PARTIAL
→ conservative related wording may be allowed
→ unsupported elements must remain excluded

WEAK
→ normally should not support a direct claim

UNSUPPORTED
→ must not generate a claim
```

A partial match should explicitly preserve:

- matched elements;
- missing elements;
- allowed claim scope;
- important limitations.

For example:

```text
Requirement:
Production-grade Python software

Supported:
Scientific Python software development
Reusable analysis workflows

Not documented:
Production deployment

Allowed claim:
Scientific Python software development

Not allowed:
Production software engineering experience
```

The planner and writer may improve relevance and wording, but they may not cross this boundary.

---

# 2.6 Evidence Validation

The Evidence Validation Gate is one of the most important semantic safeguards in the system.

It should validate two different judgments.

## Capability Validation

Does the evidence actually justify the capability assessment?

Examples:

- Are the evidence scenarios real and source-grounded?
- Were several documents incorrectly counted as several independent experiences?
- Was depth exaggerated?
- Was breadth exaggerated?
- Was autonomy exaggerated?
- Does the evidence really establish the stated capability?
- Was relevant contradictory or limiting evidence ignored?

## Requirement-Match Validation

Given the demonstrated capability, was its correspondence with the employer requirement assessed correctly?

Examples:

- Is `STRONG` justified?
- Are unsupported requirement elements explicitly preserved?
- Was related experience incorrectly converted into direct experience?
- Are claim boundaries conservative enough?
- Was an unsupported technology inferred?

Only after these semantic judgments are validated does the output become:

`Validated Evidence Map`

CV Planning must consume the validated version rather than the raw Candidate Evidence Map.

---

# 3. CV Planning

```text
Validated JobSpec
        +
Validated Evidence Map
        +
CandidateProfile
        ↓
CV Planner
        ↓
CVContentPlan
```

## Purpose

Determine what should appear in this specific CV and how limited document space should be allocated.

The planner answers:

> What should the CV communicate?

It does not yet answer:

> What is the final polished wording?

---

## Planner Responsibilities

The planner may determine:

- which experiences should appear;
- which projects should appear;
- which skills deserve emphasis;
- which evidence scenarios support each planned item;
- which employer requirements deserve the most attention;
- which sections should appear;
- section ordering;
- relative content priority;
- approximate space allocation;
- which canonical information is relevant;
- which valid but low-value information should be omitted.

Planning should consider:

```text
Employer relevance
        +
Evidence quality
        +
Candidate differentiation
        +
Available CV space
```

A valid piece of experience does not automatically deserve space.

---

## Planning Boundaries

The planner may:

- prioritize strong and relevant evidence;
- combine related evidence when factual meaning is preserved;
- emphasize supported transferable capabilities;
- omit low-relevance information;
- allow one strong accomplishment to address several employer requirements.

The planner may not:

- introduce new evidence;
- upgrade validated capability depth;
- upgrade evidence strength;
- transform indirect experience into direct experience;
- introduce undocumented technologies;
- introduce unsupported outcomes or metrics;
- use `UNSUPPORTED` evidence to justify CV content;
- cross the allowed claim boundaries defined by the Evidence Map.

---

## Output

`CVContentPlan`

Each significant planned content item should remain traceable to:

- relevant job requirements;
- validated evidence scenarios;
- its intended purpose;
- its relative priority;
- its allowed claim scope.

This lets the system later answer:

> Why did this content deserve space in this CV?

---

## Planning Validation

A separate semantic AI reviewer is not assumed to be necessary in V1.

Initial validation should use structural and deterministic checks such as:

- referenced requirements exist;
- referenced evidence scenarios exist;
- unsupported evidence is not selected;
- claim boundaries remain consistent with the Validated Evidence Map;
- canonical references exist;
- planned sections and content types are valid.

If testing demonstrates recurring strategic planning errors that cannot be caught through these checks, semantic planning review may be added later.

---

# 4. CV Writing

```text
CVContentPlan
        +
Validated Evidence Map
        ↓
CV Writer
        ↓
Tailored CV Content
```

## Purpose

Transform approved content decisions into concise, effective professional CV language.

The writer answers:

> How should the approved material be expressed?

It should not independently decide what evidence is true.

---

## Writer Responsibilities

The writer may generate:

- professional summary wording;
- experience bullets;
- project descriptions;
- accomplishment statements;
- targeted skills wording.

The writer may improve:

- clarity;
- concision;
- relevance;
- professional tone;
- emphasis.

The writer may synthesize several approved evidence scenarios into one concise statement when all important elements remain supported.

---

## Writing Boundary

The guiding rule is:

> The writer may improve wording, but not reality.

The writer may not:

- invent technologies;
- invent responsibilities;
- invent outcomes;
- invent numerical metrics;
- increase capability depth;
- exaggerate autonomy;
- convert academic or research context into undocumented production experience;
- exceed allowed claim scope;
- introduce significant unplanned claims.

The writer should receive approved evidence rather than independently searching the entire Professional Portfolio.

---

# 5. CV Draft Assembly

```text
Tailored CV Content
        +
CandidateProfile
        +
CVContentPlan
        ↓
CV Draft Assembly
        ↓
CVDraft
```

## Purpose

Combine application-specific writing with canonical candidate information to create the complete structured CV.

This stage should be primarily deterministic.

For example:

```text
Canonical data:

Graduate Researcher
Université de Sherbrooke
2018–2026

        +

Tailored content:

Developed Python-based scientific
image-processing workflows...

        ↓

Complete experience entry
```

Canonical information should not be unnecessarily regenerated or reinterpreted.

---

## Output

`CVDraft`

The CVDraft contains the complete structured content intended for the final CV while remaining independent from the rendering technology.

Significant tailored claims should preserve traceability to:

```text
CV Claim
    ↓
CVContentPlan item
    ↓
Validated Evidence Scenario(s)
    ↓
Job Requirement(s)
```

Canonical facts follow their own source path through `CandidateProfile`.

---

# 6. CV Draft Validation

```text
CVDraft
    ↓
CV Draft Validation Gate
    ↓
Validated CVDraft
```

## Purpose

Verify that writing and assembly preserved the approved factual meaning.

This is a mandatory semantic trust boundary because language generation can introduce subtle factual exaggeration even when the evidence supplied to the writer was correct.

---

## Canonical Fact Validation

Check that canonical information remains consistent with `CandidateProfile`.

Examples:

- names;
- contact information;
- role titles;
- organizations;
- dates;
- degrees;
- institutions;
- credentials;
- languages.

Where practical, these checks should be deterministic.

---

## Evidence Fidelity Validation

Check that significant tailored statements remain supported by their referenced evidence.

The validator should detect statements that:

- introduce unsupported information;
- increase capability depth;
- exaggerate autonomy;
- introduce undocumented technologies;
- invent responsibilities;
- invent results;
- distort context;
- create misleading implications by combining individually true facts.

This requires semantic review.

---

## Planning Fidelity Validation

Check that the writer respected the `CVContentPlan`.

Examples:

- planned important content was not accidentally omitted;
- unsupported new content was not introduced;
- prohibited implications were avoided;
- claim boundaries were preserved;
- content remained associated with the correct experience or project.

---

## Internal Consistency

Check for contradictions or inconsistencies inside the CV.

Examples:

- conflicting dates;
- conflicting titles;
- inconsistent technology names;
- repeated bullets;
- summary claims broader than the supporting experience;
- duplicate or contradictory education information.

---

## Output

`Validated CVDraft`

Only the validated draft should proceed to rendering.

---

# 7. Document Generation

```text
Validated CVDraft
        ↓
Render Adapter
        ↓
Renderer
        ↓
CV PDF
        ↓
Document Validation Gate
        ↓
FINAL CV
```

---

## Render Adapter

The Render Adapter converts the internal CVDraft representation into the representation expected by the selected rendering system.

Conceptually:

```text
Validated CVDraft
        ↓
Render Adapter
        ↓
Renderer-specific structured input
```

This isolates domain logic from rendering technology.

The rest of the CV Generator should not depend directly on RenderCV, Typst, or another renderer.

---

## Renderer

The renderer transforms approved structured content into the formatted PDF.

Its responsibility is presentation rather than:

- evidence selection;
- CV strategy;
- claim generation;
- factual interpretation.

---

## Document Validation

The final validation stage checks the generated document rather than reevaluating the semantic truthfulness of the CV.

Possible checks include:

- successful PDF creation;
- text extraction;
- missing content;
- duplicated content;
- page count;
- unexpected blank pages;
- character encoding;
- page breaks;
- malformed links;
- formatting integrity;
- ATS-readable text.

This stage should initially rely primarily on deterministic document checks rather than another semantic AI reviewer.

---

# Canonical Data Principle

Stable factual candidate information should have a single source of truth.

```text
Professional Portfolio
        ↓
CandidateProfile
        ↓
CVDraft
        ↓
Final PDF
```

The system should not ask an AI model to recreate information that can instead be retrieved deterministically.

AI should transform canonical information only when transformation is genuinely required and must never alter its factual meaning.

---

# Evidence Aggregation Principle

Professional capability should not be inferred from a single arbitrary source occurrence.

The system should:

```text
collect relevant evidence
        ↓
identify distinct real scenarios
        ↓
avoid duplicate counting
        ↓
characterize demonstrated capability
        ↓
compare capability with the requirement
```

Multiple evidence scenarios may strengthen:

- breadth;
- repetition;
- confidence.

They do not automatically strengthen:

- technical depth;
- autonomy;
- professional context.

Evidence aggregation must therefore be semantic rather than simple counting.

---

# Validation Principle

Validation should occur as close as practical to the transformation that may introduce an error.

However, validation does **not** automatically require another AI call.

Depending on the failure mode, a validation gate may use:

```text
Pydantic/schema validation
deterministic rules
source/provenance checks
reference checks
business rules
confidence rules
semantic AI review
document-level checks
```

Semantic AI review should primarily be used when correctness depends on meaning rather than structure.

For V1, the major semantic trust boundaries are:

```text
JobSpec Validation
        ↓
Did we understand the employer correctly?

Evidence Validation
        ↓
Does the candidate evidence really support the requirement?

CV Draft Validation
        ↓
Did the generated CV preserve approved reality?
```

CV Planning should initially use lighter deterministic/reference validation.

Document Validation should initially focus on deterministic PDF integrity.

---

# Traceability Principle

Every significant tailored CV statement should remain traceable through the complete decision chain.

```text
Original Job Posting
        ↓
Job Requirement
        ↓
Validated Evidence Scenario(s)
        ↓
Capability Assessment
        ↓
Requirement Match
        ↓
CVContentPlan Item
        ↓
CV Claim
        ↓
Final PDF
```

Canonical factual information follows a separate path:

```text
Professional Portfolio
        ↓
CandidateProfile
        ↓
CVDraft
        ↓
Final PDF
```

Traceability provides:

- factual accountability;
- debugging;
- reproducibility;
- regression testing;
- visibility into why content was selected;
- a foundation for interview preparation.

---

# Application Persistence and Interview Preparation

Each generated CV may later lead to an interview.

The system should therefore preserve the application-specific artifacts needed to reconstruct what was submitted and why.

Conceptually, an application may retain:

```text
Original Job Posting
JobSpec
Validated JobSpec
EvidenceMap
Validated EvidenceMap
CVContentPlan
CVDraft
Validated CVDraft
Submitted PDF
```

The exact storage structure is an implementation concern.

The exact PDF submitted to the employer should be preserved rather than relying on future regeneration.

---

## Interview Preparation

Interview preparation is not part of the critical CV-generation pipeline.

It is a downstream capability enabled by the evidence and traceability architecture.

Conceptually:

```text
Validated JobSpec
        +
Validated Evidence Map
        +
Submitted CVDraft / CV
        ↓
Interview Preparation
```

Because evidence scenarios preserve meaningful context, the system should later be able to reconstruct:

- what the candidate actually did;
- why it was done;
- which technologies were used;
- what part was performed independently;
- relevant technical decisions;
- constraints or difficulties;
- outcomes;
- limitations of the experience;
- which CV claim the evidence supports;
- which employer requirement motivated the claim.

Interview questions, STAR answers, and coaching should be derived from this factual evidence rather than stored directly inside the Evidence Map.

---

# Persistence Principle

Major intermediate artifacts should be persisted when they provide practical value.

This supports:

- debugging;
- observability;
- reproducibility;
- isolated testing;
- regression evaluation;
- comparison between model or prompt versions;
- application history;
- interview preparation.

Typical application-specific artifacts may include:

```text
job_spec.json
evidence_map.json
cv_content_plan.json
cv_draft.json
CV.pdf
```

Validated and unvalidated versions may be stored separately when useful for debugging or evaluation.

Exact persistence decisions are documented in `Decisions.md`.

---

# Renderer Independence Principle

Domain models should describe CV meaning rather than renderer syntax.

The internal pipeline should operate on objects such as:

```text
CVDraft
ExperienceEntry
ProjectEntry
SkillGroup
CVClaim
```

rather than directly constructing renderer-specific YAML, Typst, LaTeX, or template commands.

Renderer-specific transformation belongs in the Render Adapter.

This allows the renderer to be replaced without redesigning the evidence, planning, or writing pipeline.

---

# Minimal Necessary Complexity

The architecture should contain only components that address a distinct problem or demonstrated failure mode.

New components should not be added simply because they are common in AI systems.

Examples include:

- additional AI reviewers;
- retrieval frameworks;
- vector databases;
- orchestration frameworks;
- additional validation gates;
- complex provider abstractions.

They should be introduced when:

1. testing demonstrates a concrete need; or
2. they serve a deliberate and useful learning objective without compromising the primary project.

The design principle is:

> Introduce complexity to solve an identified problem, not in anticipation of every possible problem.

The objective is to build a reliable, understandable, testable CV Generator without unnecessary architecture.

### Application Ports

The application layer depends on stable interfaces rather than directly on
LLM providers or retrieval implementations:

- `JobAnalyzer`
- `EvidenceMatcher`
- `CVPlanner`
- `CVWriter`

Concrete implementations are injected into the pipeline.

This allows tests to use deterministic fake adapters while production
implementations can later use local models, APIs, deterministic retrieval,
or other providers without changing the core application workflow.

The CVWriter does not receive the raw JobSpec directly.

The job has already been interpreted through evidence matching and content
planning. The writer therefore operates only from the canonical candidate
profile, approved evidence, and approved content plan.

This limits the writer's ability to independently reinterpret the job
posting or introduce unsupported claims.