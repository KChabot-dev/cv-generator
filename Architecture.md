# Architecture

## System Overview

The CV Generator transforms a job posting and the Professional Portfolio into a tailored, evidence-based CV in PDF format.

### Inputs

* Job posting
* Professional Portfolio

### Output

* Tailored CV in PDF format

The Professional Portfolio serves two distinct purposes:

1. **Evidence source** — documented skills, experiences, projects, accomplishments, and supporting material used to determine what can truthfully be claimed.
2. **Canonical candidate data** — stable factual information such as name, contact information, education, official titles, organizations, dates, and languages.

These two types of information should not be treated in the same way.

---

## High-Level Pipeline

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
Validated JobSpec        │                   │
    │                    │                   │
    └──────────────→ Evidence Matching ←─────┘
                         ↓
                Validated Evidence Map
                         ↓
                    CV Planning
                         ↓
                  CV Content Plan
                         ↓
                     CV Writing
                         ↓
                Tailored CV Content
                         ↓
Candidate Profile ─→ CV Draft Assembly
                         ↓
                Structured CV Draft
                         ↓
                CV Draft Validation
                         ↓
                 Validated CV Draft
                         ↓
                Document Rendering
                         ↓
                   Validated PDF
                         ↓
                     FINAL CV
```

The pipeline separates:

* understanding the job;
* identifying supporting evidence;
* deciding what should appear in the CV;
* writing targeted professional content;
* inserting canonical candidate information;
* validating factual fidelity;
* rendering the final document.

Each stage has a specific responsibility and should not perform work that belongs to another stage.

---

## 1. Job Analysis

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

### Purpose

Transform the unstructured job posting into a structured representation of what the employer is looking for.

The `JobSpec` may contain information such as:

* role information;
* responsibilities;
* required and preferred skills;
* expected proficiency when explicitly supported;
* domain knowledge;
* education and experience requirements;
* collaboration expectations;
* employment constraints.

### Validation

The JobSpec Validation Gate verifies that the structured data is valid and remains grounded in the original posting.

Validation may include:

* deterministic schema checks;
* source traceability;
* confidence rules;
* semantic comparison of the generated JobSpec against the original job posting.

The system should not infer requirements or skill levels that are not supported by the posting.

---

## 2. Evidence Matching

```text
Validated JobSpec
        +
Professional Portfolio
        ↓
Evidence Matcher
        ↓
Candidate Evidence Map
        ↓
Evidence Validation Gate
        ↓
Validated Evidence Map
```

### Purpose

Determine which documented experiences, skills, projects, and accomplishments from the Professional Portfolio support each relevant job requirement.

Every proposed match must remain traceable to its source in the portfolio.

### Evidence Strength

Evidence can be classified according to predefined rules, for example:

```text
STRONG
PARTIAL
WEAK
UNSUPPORTED
```

These classifications determine how strongly the evidence may later be represented in the CV.

A relevant but indirect capability must not be transformed into experience with a specific technology or responsibility that is not documented.

The system must be allowed to return `UNSUPPORTED` when no adequate evidence exists.

### Validation

The Evidence Validation Gate is one of the most important safeguards in the system.

It verifies that proposed matches genuinely follow from the documented portfolio evidence and applies the defined evidence thresholds and claim rules.

Semantic review may be used here because evaluating whether two professional capabilities genuinely correspond can require judgment.

---

## 3. CV Content Generation

### 3.1 CV Planning

```text
Validated JobSpec
        +
Validated Evidence Map
        +
Candidate Profile
        ↓
CV Planner
        ↓
CV Content Plan
```

### Purpose

Decide what should appear in the CV and how the available space should be prioritized.

The planner determines:

* which experiences should be included;
* which projects should be included;
* which skills should be emphasized;
* which evidence items should support each section;
* which job requirements deserve the most attention;
* which canonical candidate information is relevant to the document;
* which valid but low-relevance information should be omitted.

The planner may only use evidence from the Validated Evidence Map when planning tailored claims.

The resulting plan should preserve references to the evidence supporting each selected item.

---

### 3.2 CV Writing

```text
CV Content Plan
        +
Approved Evidence
        ↓
CV Writer
        ↓
Tailored CV Content
```

### Purpose

Transform the approved CV Content Plan into concise and effective professional CV language.

The writer is primarily responsible for content that requires language or targeting decisions, such as:

* professional summary;
* experience bullets;
* project descriptions;
* accomplishment statements;
* skill emphasis.

The writer may improve wording and presentation but may not modify the underlying reality.

The writer should not unnecessarily regenerate stable factual information such as:

* candidate name;
* contact information;
* degree names;
* institutions;
* official experience titles;
* organizations;
* dates;
* languages.

Those values come from the `Candidate Profile`.

---

### 3.3 CV Draft Assembly

```text
Tailored CV Content
        +
Candidate Profile
        +
CV Content Plan
        ↓
CV Draft Assembly
        ↓
Structured CV Draft
```

### Purpose

Combine tailored AI-generated content with canonical candidate information to create the complete structured CV.

This stage should primarily be deterministic.

For example, it may combine:

```text
Canonical data:
Graduate Researcher
Université de Sherbrooke
2018–2026

        +

Tailored content:
Developed Python-based scientific image-processing workflows...

        ↓

Complete experience entry
```

The assembly stage should not reinterpret or rewrite factual candidate information.

---

### 3.4 CV Draft Validation

```text
Structured CV Draft
        ↓
CV Draft Validation Gate
        ↓
Validated CV Draft
```

### Purpose

Ensure that the writer and assembly process preserved the factual meaning of the approved content and canonical candidate data.

The validator must detect statements that:

* introduce unsupported information;
* increase the strength of a claim beyond the approved evidence;
* change the meaning of the source evidence;
* invent technologies, responsibilities, metrics, outcomes, or expertise levels;
* exaggerate autonomy or responsibility;
* create misleading implications by combining otherwise true statements;
* modify canonical facts such as titles, organizations, dates, education, or credentials.

Every significant CV statement should remain traceable to one or more validated evidence items.

---

## 4. Document Generation

```text
Validated CV Draft
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

### Render Adapter

The Render Adapter converts the internal CV representation into the format expected by the selected rendering system.

This isolates the internal CV-generation pipeline from the specific rendering technology.

### Renderer

The renderer transforms the approved structured CV content into the final formatted PDF.

The renderer is responsible for presentation, not content selection or writing.

### Document Validation

The final validation stage verifies the generated document rather than the truthfulness of its content.

It may check:

* text extraction;
* missing or duplicated content;
* page count;
* formatting problems;
* character encoding;
* page breaks;
* other rendering or ATS-related issues.

---

## Canonical Data Principle

Stable factual candidate information should have a single source of truth.

The system should not ask an AI model to recreate information that can instead be retrieved deterministically.

The `Candidate Profile` represents this canonical information.

It may contain:

* name;
* contact information;
* location;
* professional links;
* education and credentials;
* official experience titles;
* organizations;
* employment or research dates;
* languages;
* other stable factual information required by the CV.

The Candidate Profile may be created or updated when the Professional Portfolio changes, but it should not need to be regenerated independently for every job application.

AI should only transform canonical information when transformation is genuinely required, and must never alter its underlying factual meaning.

---

## Validation Principle

Validation should occur as close as practical to the transformation that may introduce an error.

However, validation does **not** automatically require another AI call.

Depending on the problem, a validation gate may use:

```text
deterministic rules
schema validation
source/provenance checks
confidence thresholds
semantic AI review
document-level checks
```

AI-based review should primarily be used when the decision requires semantic judgment that cannot be reliably expressed as deterministic rules.

---

## Traceability Principle

The system should maintain a traceable chain from the final CV back to the original evidence.

```text
Job Requirement
      ↓
Validated Portfolio Evidence
      ↓
CV Content Plan
      ↓
CV Statement
      ↓
Final PDF
```

Canonical factual information follows a separate traceability path:

```text
Professional Portfolio
      ↓
Candidate Profile
      ↓
Structured CV Draft
      ↓
Final PDF
```

This traceability makes it possible to determine where an error was introduced and prevents unsupported claims or incorrect factual information from silently entering the final CV.

---

## Design Principle: Minimal Necessary Complexity

The architecture should contain only components that address a distinct problem or failure mode.

New validation layers, AI reviewers, frameworks, or services should be introduced when testing demonstrates a need for them rather than being added automatically.

The objective is to build a reliable and understandable system without unnecessary complexity.

---

# Data Flow Between Components

Each major component receives a defined input and produces a defined output.

At this stage, the architecture describes the **meaning of the data being exchanged**, not its exact technical representation.

The precise schemas and Python models will be defined later.

---

## 0. Candidate Profile

### Input

Professional Portfolio.

### Output

`Candidate Profile`

The Candidate Profile contains canonical candidate information that should remain consistent across CV versions.

It may contain:

* name and contact information;
* location;
* professional links;
* education and credentials;
* official experience titles;
* organizations;
* employment or research dates;
* languages;
* other stable factual information required by CVs.

This information should not be unnecessarily regenerated by AI for each application.

---

## 1. Job Analysis

### Input

Raw job posting.

This is the original job description provided to the system before interpretation or transformation.

It may contain:

* job title;
* company information;
* responsibilities;
* required qualifications;
* preferred qualifications;
* technical skills;
* education requirements;
* experience requirements;
* location or travel constraints;
* other relevant information from the posting.

### Output

`JobSpec`

The `JobSpec` is a structured representation of what the employer is asking for.

It should preserve enough information for later stages to distinguish between:

* role information;
* responsibilities;
* required skills;
* preferred skills;
* education and experience requirements;
* domain knowledge;
* collaboration or communication expectations;
* employment constraints;
* requirement priority or importance;
* explicitly stated proficiency expectations;
* supporting evidence from the original job posting.

After validation, the output becomes:

`Validated JobSpec`

---

## 2. Evidence Matching

### Inputs

`Validated JobSpec`

The validated structured representation of the employer's requirements.

Professional Portfolio

The Professional Portfolio is the source of truth for documented professional evidence, including:

* skills;
* professional and research experience;
* projects;
* technical accomplishments;
* scientific work;
* software-development experience;
* publications and presentations when relevant;
* documented levels of autonomy or responsibility;
* supporting evidence from code audits or other source material.

### Output

`Candidate Evidence Map`

The Candidate Evidence Map links relevant job requirements to documented evidence from the Professional Portfolio.

For each requirement, the Evidence Matcher should identify:

* the requirement being evaluated;
* relevant portfolio evidence;
* the source or sources of that evidence;
* the nature of the correspondence;
* the strength of the evidence;
* limitations or missing elements;
* whether the evidence supports a direct CV claim.

A requirement does not need to have matching evidence.

The system must be able to explicitly represent that no adequate evidence was found.

### Evidence Strength

A preliminary classification is:

* `STRONG`
* `PARTIAL`
* `WEAK`
* `UNSUPPORTED`

`STRONG` indicates that the portfolio directly documents the requested skill, responsibility, or a clearly equivalent capability.

`PARTIAL` indicates that the portfolio demonstrates a closely related capability, but some aspect of the employer's requirement is not directly documented.

`WEAK` indicates that there is some conceptual relationship, but representing the requirement as direct experience would be misleading.

`UNSUPPORTED` indicates that no adequate documented evidence exists.

### Claim Eligibility

Evidence strength and CV claim strength are related but are not identical.

For example:

* `STRONG` evidence may support direct wording.
* `PARTIAL` evidence may support related or transferable wording, but must not introduce undocumented technologies or experience.
* `WEAK` evidence may be useful for internal analysis but should normally not support a direct CV claim.
* `UNSUPPORTED` evidence must not generate a CV claim.

The exact thresholds and rules will be defined during implementation design.

### Provenance

Every proposed correspondence must remain traceable to its source in the Professional Portfolio.

```text
Job Requirement
    ↓
Portfolio Evidence
    ↓
Source File or Document
    ↓
Evidence Classification
```

### Validation

The `Candidate Evidence Map` passes through an Evidence Validation Gate.

The validator verifies that:

* the proposed evidence actually exists;
* the evidence has not been distorted;
* the correspondence is reasonable;
* the assigned evidence strength follows the defined rules;
* missing technologies, responsibilities, or expertise have not been inferred;
* indirect experience has not been represented as direct experience.

After validation, the output becomes:

`Validated Evidence Map`

---

## 3. CV Planning

### Inputs

`Validated JobSpec`

The validated representation of the employer's requirements, priorities, responsibilities, and constraints.

`Validated Evidence Map`

The validated mapping between job requirements and documented evidence from the Professional Portfolio.

`Candidate Profile`

Canonical candidate information that may influence section inclusion and document structure.

### Output

`CV Content Plan`

The CV Content Plan defines the content strategy for the targeted CV before final wording is produced.

It should determine:

* which experiences should be included;
* which projects should be included;
* which skills should be emphasized;
* which evidence items should support each section;
* which job requirements should receive the most attention;
* how much relative emphasis each experience, project, or skill should receive;
* which relevant information should be omitted because of limited space or low relevance;
* the intended purpose of each planned bullet or section.

The planner should optimize the CV for relevance to the target position while remaining strictly within the boundaries established by the Validated Evidence Map.

### Planning Rules

The CV Planner may:

* prioritize stronger and more relevant evidence;
* combine related evidence when doing so preserves its original meaning;
* emphasize transferable capabilities supported by the portfolio;
* omit valid but low-relevance information;
* adapt the relative importance of experiences and projects according to the target role.

The CV Planner may not:

* introduce new evidence;
* upgrade the strength of validated evidence;
* transform indirect experience into direct experience;
* introduce undocumented technologies, responsibilities, results, or expertise;
* use evidence classified as `UNSUPPORTED` to justify CV content.

Evidence classified as `WEAK` should normally remain excluded from direct CV claims unless later rules explicitly allow a conservative use.

### Traceability

Every planned CV item should remain connected to the validated evidence that supports it.

```text
Job Requirement
      ↓
Validated Evidence
      ↓
Planned CV Content
      ↓
Evidence Reference
```

### Planning Report

The planner may also produce an internal planning report explaining major selection decisions.

For example, the report may indicate:

* why a particular experience received high priority;
* which job requirements it supports;
* why another experience was omitted;
* which evidence was selected for a planned bullet;
* which relevant requirements could not be represented because no adequate evidence exists.

The planning report is an internal diagnostic artifact and is not part of the final CV.

### Validation

At this stage, a dedicated AI-based validation step is not assumed to be necessary.

The system should first rely on structural and deterministic checks, such as:

* every planned item references valid evidence;
* no unsupported evidence is selected;
* evidence strength is not modified;
* referenced job requirements exist;
* planned content remains traceable.

If later testing shows that the planner regularly makes poor strategic decisions despite these checks, a semantic planning-review step may be added.

The output of this stage is:

`CV Content Plan`

---

## 4. CV Writing and Draft Assembly

### Inputs

`CV Content Plan`

The approved strategy describing what should appear in the targeted CV.

`Validated Evidence Map`

The approved evidence supporting the tailored content.

`Candidate Profile`

Canonical factual information required to construct the complete document.

### Writer Output

`Tailored CV Content`

The CV Writer transforms approved evidence into professional CV language.

It may generate:

* summary text;
* experience bullets;
* project descriptions;
* accomplishment statements;
* targeted skill wording.

It may improve wording but may not improve reality.

### Draft Assembly

The tailored content is combined with the Candidate Profile to produce:

`Structured CV Draft`

Canonical information should be copied into the draft without unnecessary AI reinterpretation.

### Validation

The Structured CV Draft passes through the CV Draft Validation Gate.

The validator verifies that:

* every significant generated claim is supported by approved evidence;
* no unsupported information was introduced;
* evidence strength was respected;
* source meaning was preserved;
* autonomy or responsibility was not exaggerated;
* canonical candidate information remains correct;
* dates, titles, organizations, education, and credentials were not altered;
* the resulting draft follows the CV Content Plan.

After validation, the output becomes:

`Validated CV Draft`

---

## 5. Document Generation

### Input

`Validated CV Draft`

### Output

Final validated CV in PDF format.

```text
Validated CV Draft
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

The renderer is responsible for presentation rather than content decisions.

The Document Validation Gate verifies the integrity and usability of the generated PDF.
