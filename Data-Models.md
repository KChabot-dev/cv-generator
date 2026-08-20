# Data Models

This document defines the conceptual structure of the major data objects exchanged by the CV Generator.

It describes what information each object must represent and the relationships between objects.

The exact Pydantic classes, field types, enums, validators, and serialization rules will be defined during implementation.

The five primary domain models are:

```text
CandidateProfile
JobSpec
EvidenceMap
CVContentPlan
CVDraft
```

---

# Cross-Model Principles

## Stable Identifiers

Entities that must be referenced by later pipeline stages should receive stable identifiers.

Conceptually:

```text
CandidateProfile entities
    EXP-001
    EDU-001

JobSpec
    REQ-001

EvidenceMap
    SCEN-001

CVContentPlan
    PLAN-001

CVDraft
    CLAIM-001
```

These identifiers allow later stages to reference existing information rather than copying and reinterpreting it.

The exact identifier format may change during implementation.

---

## Reference Integrity

References between models must point to valid existing entities.

For example:

```text
REQ-006
   ↓
SCEN-012
SCEN-014
   ↓
PLAN-008
   ↓
CLAIM-011
```

Validation should detect broken references.

---

## Missing Information

The models should distinguish:

```text
known value
unknown value
not applicable
inferred value
```

Missing information should not automatically be filled through AI inference.

---

## Validated Objects

Objects produced by semantic AI transformations may exist conceptually in unvalidated and validated states.

For example:

```text
JobSpec
    ↓
validation
    ↓
Validated JobSpec
```

and:

```text
EvidenceMap
    ↓
validation
    ↓
Validated Evidence Map
```

This distinction does not necessarily require separate Python classes.

The exact implementation may use validation status, wrapper objects, pipeline state, or another mechanism.

---

# 1. CandidateProfile

## Purpose

`CandidateProfile` contains canonical candidate information that should remain factually consistent across CV versions.

It represents stable information retrieved from the Professional Portfolio and should not be unnecessarily regenerated or interpreted by AI.

It remains independent from a specific job application.

---

## Candidate Identity

The profile should be able to represent:

- full name;
- professional location;
- email address;
- phone number;
- professional links such as LinkedIn or GitHub.

Not every field must necessarily appear on every generated CV.

Conceptually:

```text
CandidateIdentity
├── full_name
├── location
├── email
├── phone
└── professional_links[]
```

---

## Education

Each canonical education entry should have a stable identifier.

Conceptually:

```text
EducationRecord
├── id
├── degree
├── field
├── institution
├── location
├── start_date
├── end_date
└── status
```

Possible identifiers:

```text
EDU-001
EDU-002
```

The identifier allows later stages to select or reference an education record without rewriting its factual contents.

---

### Date Precision

Canonical career dates must preserve the precision available in the source information.

A date may therefore contain:

* a year only, such as `2018`;
* a year and month, such as `2018-09`.

The system must not invent a month or day when the source documentation only establishes a year.

Date-order validation should reject demonstrably impossible ranges while preserving ambiguity when incomplete dates do not establish an exact ordering.

## Experience Metadata

Each professional or research experience should contain canonical metadata.

Conceptually:

```text
ExperienceRecord
├── id
├── role_title
├── organization
├── location
├── start_date
└── end_date
```

Possible identifiers:

```text
EXP-001
EXP-002
```

Detailed accomplishments and tailored descriptions do not belong in the canonical experience record.

Those come from validated professional evidence.

---

## Languages

Each language entry should represent:

```text
LanguageRecord
├── language
└── proficiency
```

Proficiency should only be recorded when documented or deliberately defined as canonical candidate information.

---

## Additional Canonical Information

The model may later include other stable information required for CV generation.

Examples might include:

- credentials;
- certifications;
- stable project metadata;
- publication metadata;
- presentation metadata.

These should only be added when implementation demonstrates that keeping them in the CandidateProfile is useful.

The CandidateProfile should not become a duplicate of the entire Professional Portfolio.

---

## Conceptual Structure

```text
CandidateProfile
│
├── identity
│   ├── full_name
│   ├── location
│   ├── email
│   ├── phone
│   └── professional_links[]
│
├── education[]
│   └── EducationRecord
│       ├── id
│       ├── degree
│       ├── field
│       ├── institution
│       ├── location
│       ├── start_date
│       ├── end_date
│       └── status
│
├── experiences[]
│   └── ExperienceRecord
│       ├── id
│       ├── role_title
│       ├── organization
│       ├── location
│       ├── start_date
│       └── end_date
│
└── languages[]
    └── LanguageRecord
        ├── language
        └── proficiency
```

---

## Design Rules

`CandidateProfile` should:

- remain independent from a particular job application;
- provide a single source of truth for stable facts;
- preserve the original factual meaning of the Professional Portfolio;
- distinguish missing information from inferred information;
- use stable identifiers for canonical entities referenced downstream;
- avoid storing tailored CV wording;
- avoid duplicating the entire Professional Portfolio;
- be copied into later objects deterministically wherever practical.

---

# 2. JobSpec

## Purpose

`JobSpec` is the structured representation of a job posting.

It captures what the employer is asking for while preserving enough information to trace each interpretation back to the original posting.

`JobSpec` describes the target position independently from the candidate.

It must not contain conclusions about whether the candidate satisfies the requirements.

---

## Job Metadata

The model should represent general information about the position when available.

Conceptually:

```text
JobMetadata
├── title
├── company
├── location
├── work_arrangement
├── employment_type
├── compensation
├── travel
└── other_constraints
```

Possible information includes:

- job title;
- company;
- location;
- remote, hybrid, or on-site status;
- employment type;
- compensation;
- travel expectations;
- other relevant employment constraints.

Absence of information should remain explicit rather than being inferred.

---

## Job Requirements

Employer expectations should generally be represented as individual `JobRequirement` objects.

Conceptually:

```text
JobRequirement
├── id
├── category
├── description
├── priority
├── expected_level
├── experience_requirement
├── explicitness
├── source_text
├── source_location
└── interpretation_notes
```

A requirement may represent:

- technical skill;
- software-engineering practice;
- responsibility;
- domain knowledge;
- education;
- professional experience;
- collaboration or communication expectation;
- leadership expectation;
- language requirement;
- other relevant qualification.

---

## Requirement Identifier

Each requirement should receive a stable identifier.

For example:

```text
REQ-001
REQ-002
REQ-003
```

This allows later stages to operate requirement by requirement.

Conceptually:

```text
JobSpec
   ↓
REQ-007
   ↓
EvidenceMap
   ↓
CVContentPlan
   ↓
CVDraft
```

---

## Requirement Category

Preliminary categories may include:

```text
TECHNICAL_SKILL
SOFTWARE_PRACTICE
RESPONSIBILITY
DOMAIN_KNOWLEDGE
EDUCATION
EXPERIENCE
COLLABORATION
LEADERSHIP
LANGUAGE
OTHER
```

The taxonomy should remain limited to distinctions that provide practical downstream value.

Categories may be changed after testing real job postings.

---

## Requirement Priority

The model should preserve how strongly the employer presents the requirement.

Preliminary concepts may include:

```text
REQUIRED
PREFERRED
CORE_RESPONSIBILITY
ADVANTAGEOUS
UNSPECIFIED
```

The system must not convert wording such as:

```text
"preferred"
"an asset"
"nice to have"
```

into a mandatory requirement.

Likewise, absence of explicit priority should not automatically become `REQUIRED`.

---

## Expected Proficiency

When the posting explicitly communicates an expected proficiency level, the model should preserve it.

Possible source wording may include:

- familiarity;
- working knowledge;
- strong proficiency;
- advanced expertise.

For example:

```text
Posting:
"Experience with Python."

Expected level:
UNSPECIFIED
```

rather than:

```text
Expected level:
ADVANCED
```

Proficiency should not be invented simply because the AI believes a role sounds senior.

---

## Experience Requirements

When the posting associates an amount or type of experience with a requirement, that relationship should remain attached to the requirement.

For example:

```text
"3+ years of professional Python development"
```

should preserve:

```text
Python development
        +
3+ years
        +
professional context
```

rather than storing `3+ years` as an unrelated global value.

Experience requirements may include:

- minimum years;
- preferred years;
- professional context;
- academic context;
- research context;
- qualitative experience expectations.

---

## Explicit Information and Inference

The model should distinguish directly supported information from AI interpretation.

Example:

```text
Posting:
"5+ years developing production software"

Explicit:
- 5+ years
- production software development

Possible interpretation:
- likely experienced or senior-level role
```

The explicit facts and the interpretation must not have the same evidentiary status.

Useful inference may be retained for diagnostics or planning when appropriate, but downstream matching should remain grounded primarily in explicit employer requirements.

---

## Source Grounding

Every significant requirement should remain traceable to the original posting.

Conceptually:

```text
REQ-004
│
├── description:
│   Automated software testing
│
├── priority:
│   REQUIRED
│
└── source_text:
    "Develop and maintain automated unit and integration tests."
```

Where practical, `source_location` may identify the posting section or another location marker.

Source grounding allows the JobSpec Validation Gate to compare interpretation with original text.

---

## Interpretation Notes

Short internal notes may explain non-obvious interpretations.

They are diagnostic metadata and are not part of the final CV.

They must not substitute for source evidence.

---

## Validation

The generated object initially represents:

```text
JobSpec
```

After the JobSpec Validation Gate:

```text
Validated JobSpec
```

Validation should distinguish:

```text
structurally valid
        ≠
semantically correct
```

For example, Pydantic may accept:

```text
expected_level = ADVANCED
```

while semantic validation correctly rejects it because the posting merely states:

```text
"Experience with Python."
```

---

## Conceptual Structure

```text
JobSpec
│
├── job_metadata
│   ├── title
│   ├── company
│   ├── location
│   ├── work_arrangement
│   ├── employment_type
│   ├── compensation
│   ├── travel
│   └── other_constraints
│
└── requirements[]
    └── JobRequirement
        ├── id
        ├── category
        ├── description
        ├── priority
        ├── expected_level
        ├── experience_requirement
        ├── explicitness
        ├── source_text
        ├── source_location
        └── interpretation_notes
```

---

## Design Rules

`JobSpec` should:

- describe the employer rather than the candidate;
- preserve requirements individually;
- distinguish required from preferred information;
- avoid inventing proficiency;
- preserve experience requirements with the capability they qualify;
- distinguish explicit information from inference;
- maintain provenance to the original posting;
- represent missing information explicitly rather than guessing;
- provide stable requirement identifiers;
- remain suitable for requirement-by-requirement Evidence Matching.

---

# 3. EvidenceMap

## Purpose

`EvidenceMap` connects validated job requirements with documented candidate evidence.

It should answer:

> What relevant evidence exists, what capability does that evidence collectively demonstrate, how well does that capability satisfy each employer requirement, and what are we safely allowed to claim?

The EvidenceMap must not invent candidate capabilities.

It should preserve enough information for:

- CV planning;
- claim validation;
- debugging;
- traceability;
- regression evaluation;
- skill-gap analysis;
- interview preparation.

---

## Overall Structure

Distinct evidence scenarios should be represented once and referenced by requirement assessments.

Conceptually:

```text
EvidenceMap
│
├── scenarios[]
│   └── EvidenceScenario
│
└── assessments[]
    └── EvidenceAssessment
```

This avoids duplicating the same real experience every time it supports another requirement.

---

# Evidence Scenarios

## Purpose

An `EvidenceScenario` represents one distinct real-world use, project activity, accomplishment, implementation, or professional situation.

Conceptually:

```text
EvidenceScenario
├── id
├── summary
├── source_items[]
├── technical_details
├── context
├── autonomy_level
├── outcome
├── limitations[]
└── notes
```

---

## Evidence Scenario Identifier

Each distinct scenario should receive a stable identifier.

For example:

```text
SCEN-001
SCEN-002
SCEN-003
```

The same scenario can support several job requirements without being duplicated.

For example:

```text
SCEN-014
   ├── supports REQ-003
   ├── supports REQ-007
   └── supports REQ-009
```

---

## Source Items

A scenario may be supported by several portfolio sources.

Conceptually:

```text
SourceItem
├── source_document
├── source_section
├── supporting_text
└── source_type
```

Possible source types may include:

```text
SKILL
EXPERIENCE
PROJECT
CODE_AUDIT
PUBLICATION
PRESENTATION
EDUCATION
OTHER
```

Every important scenario must remain traceable to actual portfolio evidence.

---

## Avoiding Double Counting

Several documents may describe the same underlying work.

For example:

```text
Scientific-Image-Processing.md
Project-Pipeline.md
Code-Evidence-by-Skills.md
```

might all document the same OpenCV ROI-selection implementation.

These should normally become:

```text
Multiple SourceItems
        ↓
One EvidenceScenario
```

rather than:

```text
Three documents
        ↓
Three independent experiences
```

Multiple supporting sources may increase confidence in documentation.

They must not automatically increase:

- depth;
- breadth;
- repetition.

---

## Scenario Details

Where supported, an EvidenceScenario should preserve enough detail to reconstruct:

```text
What was done?
Why was it done?
Which tools were used?
What technical work was involved?
What was performed independently?
What constraints existed?
What outcome resulted?
What are the boundaries of the experience?
```

These details support both CV validation and later interview preparation.

---

# Evidence Assessments

## Purpose

An `EvidenceAssessment` evaluates one `JobRequirement`.

There should normally be an assessment for each extracted job requirement so that unsupported requirements remain observable.

Conceptually:

```text
EvidenceAssessment
├── requirement_id
├── scenario_refs[]
├── scenario_relevance[]
├── capability_assessment
├── requirement_match
└── assessment_notes
```

The assessment references existing `EvidenceScenario` objects rather than redefining them.

---

## Scenario Relevance

Not every referenced scenario relates equally strongly to a requirement.

Each scenario-to-requirement relationship should preserve its relevance.

Preliminary categories may include:

```text
DIRECT
RELATED
CONTEXTUAL
```

### DIRECT

The scenario explicitly demonstrates the requested capability or a clearly equivalent capability.

### RELATED

The scenario demonstrates a meaningful transferable capability but not the exact requested capability.

### CONTEXTUAL

The scenario contributes useful context but does not independently establish the requested capability.

The exact technical representation may use a small relationship object rather than parallel arrays.

For example:

```text
ScenarioMatch
├── scenario_ref
├── relevance
└── notes
```

This will be decided during Pydantic modelling.

---

# Capability Assessment

After relevant scenarios are identified, the system should determine what they collectively demonstrate.

Conceptually:

```text
CapabilityAssessment
├── depth
├── breadth
├── repetition
├── autonomy
├── context
├── confidence
└── capability_summary
```

These dimensions must remain conceptually distinct.

---

## Capability Depth

Depth represents sophistication of demonstrated work.

Preliminary levels might include:

```text
BASIC
WORKING
ADVANCED
```

These labels and their interpretation require calibration during testing.

Depth should reflect what was actually done rather than how many times a technology appears.

For example:

```text
Five distinct basic OpenCV uses
```

may justify:

```text
Depth: BASIC
Repetition: HIGH
Confidence: HIGH
```

but not automatically:

```text
Depth: ADVANCED
```

---

## Capability Breadth

Breadth describes the range of distinct aspects demonstrated.

For example:

```text
OpenCV evidence:
- image I/O
- ROI interaction
- masks
- contours
- thresholding
- video processing
- visualization
```

may establish broad practical exposure even when no individual task is advanced.

Breadth and depth must remain separate.

---

## Repetition

Repetition represents repeated use across genuinely distinct scenarios.

Repeated use can strengthen evidence that a capability is practically established.

However:

```text
repetition
≠
depth
```

Several beginner-level applications remain beginner-level unless the actual work demonstrates increasing sophistication.

---

## Autonomy

The capability assessment should preserve documented responsibility.

Possible concepts may include:

```text
INDEPENDENT
COLLABORATIVE
CONTRIBUTED
ASSISTED
EXPLORATORY
LED
```

The exact representation may need to support multiple autonomy levels when evidence scenarios differ.

The system must not infer stronger autonomy than the source supports.

---

## Context

Context preserves information necessary to interpret the capability.

Examples include:

```text
scientific research
academic project
production environment
exploratory analysis
experimental instrumentation
reusable research software
collaborative development
```

The exact representation may eventually support multiple contexts rather than a single value.

---

## Confidence

Confidence describes how strongly the documentation establishes that the candidate genuinely demonstrated the capability.

It may be influenced by:

- detailed source material;
- code-audit evidence;
- multiple independent scenarios;
- consistent descriptions across sources;
- explicit documentation of implementation or responsibility.

Confidence must not be confused with depth.

For example:

```text
Depth: BASIC
Confidence: VERY HIGH
```

is valid.

---

## Capability Summary

The assessment should produce a concise internal summary of the demonstrated capability.

For example:

```text
Independent practical OpenCV experience across multiple scientific
image-processing tasks, including interactive ROI selection, masks,
contours, thresholding, visualization, and image/video I/O.
```

The capability summary describes the candidate evidence before deciding whether it satisfies the specific employer requirement.

---

# Requirement Match

After the candidate capability is characterized, it is compared with the employer requirement.

Conceptually:

```text
RequirementMatch
├── match_strength
├── matched_elements[]
├── missing_elements[]
├── claim_eligibility
├── allowed_claim_scope
└── match_notes
```

This is distinct from Capability Assessment.

---

## Match Strength

Preliminary classifications are:

```text
STRONG
PARTIAL
WEAK
UNSUPPORTED
```

### STRONG

The demonstrated capability directly satisfies the employer requirement or a clearly equivalent expectation.

### PARTIAL

Meaningful portions are supported, but important elements remain undocumented.

### WEAK

A conceptual relationship exists, but representing the requested capability as direct experience would be misleading.

### UNSUPPORTED

No adequate documented capability supports the requirement.

---

## Same Capability, Different Requirement

Match strength depends on:

```text
Demonstrated Capability
        +
Specific Employer Requirement
```

For example:

```text
Demonstrated capability:
Working practical OpenCV experience in scientific image processing.
```

Requirement A:

```text
"Familiarity with OpenCV"
```

may produce:

```text
STRONG
```

Requirement B:

```text
"Advanced OpenCV expertise for real-time object detection and tracking"
```

may produce:

```text
PARTIAL
or
WEAK
```

The evidence has not changed.

The employer requirement has.

---

## Matched Elements

The assessment should identify supported portions of the employer requirement.

For example:

```text
Requirement:
Advanced OpenCV-based object detection and tracking

Matched:
- OpenCV
- image processing
- masks
- contours
```

---

## Missing Elements

Unsupported portions should remain explicit.

For example:

```text
Missing:
- object detection implementation
- tracking implementation
- real-time computer-vision pipeline
```

This prevents related experience from silently becoming direct experience.

---

## Claim Eligibility

Match strength and claim permission are related but are not identical.

A preliminary relationship is:

```text
STRONG
→ direct claim generally allowed

PARTIAL
→ conservative related claim may be allowed
→ unsupported elements remain excluded

WEAK
→ normally not eligible for a direct claim

UNSUPPORTED
→ no claim allowed
```

The exact rules should be calibrated using real applications.

---

## Allowed Claim Scope

The assessment should explicitly preserve the factual boundary the CV may use.

Example:

```text
Requirement:
Production-grade Python software development

Demonstrated capability:
Scientific Python software development and reusable analysis workflows

Match:
PARTIAL

Allowed claim scope:
Scientific Python software development and reusable analysis workflows

Not supported:
Production deployment or production-grade software experience
```

This boundary is passed downstream rather than rediscovered by the planner or writer.

---

# Unsupported Requirements

Unsupported requirements should remain represented.

For example:

```text
REQ-012

scenario_refs:
[]

capability_assessment:
None

requirement_match:
UNSUPPORTED

claim_eligibility:
NONE
```

This supports:

- hallucination prevention;
- job-fit analysis;
- recurring skill-gap analysis;
- future upskilling decisions.

---

# Evidence Validation

The generated EvidenceMap passes through a mandatory Evidence Validation Gate.

The validator evaluates two distinct semantic judgments.

## Capability Validation

Questions may include:

```text
Do the referenced scenarios exist?

Do the sources actually support those scenarios?

Were several descriptions of the same work double-counted?

Does the evidence really justify the assigned depth?

Does the evidence justify the claimed breadth?

Does documented responsibility justify the autonomy assessment?

Were limitations ignored?
```

## Requirement-Match Validation

Questions may include:

```text
Does the demonstrated capability satisfy this requirement?

Is STRONG / PARTIAL / WEAK / UNSUPPORTED justified?

Were missing requirement elements preserved?

Was related experience incorrectly converted into direct experience?

Are claim boundaries appropriate?
```

Only after validation does the object become:

```text
Validated Evidence Map
```

---

# Interview-Preparation Value

The EvidenceMap remains a factual evidence model.

It should not contain interview questions, STAR answers, or coaching.

However, its scenarios should preserve enough factual context to generate those artifacts later.

Conceptually:

```text
Validated JobSpec
        +
Validated Evidence Map
        +
Submitted CV
        ↓
Interview Preparation
```

This makes evidence traceability useful beyond CV generation.

---

## Conceptual Structure

```text
EvidenceMap
│
├── scenarios[]
│   └── EvidenceScenario
│       ├── id
│       ├── summary
│       ├── source_items[]
│       ├── technical_details
│       ├── context
│       ├── autonomy_level
│       ├── outcome
│       ├── limitations[]
│       └── notes
│
└── assessments[]
    └── EvidenceAssessment
        ├── requirement_id
        ├── scenario_matches[]
        │   └── ScenarioMatch
        │       ├── scenario_ref
        │       ├── relevance
        │       └── notes
        │
        ├── capability_assessment
        │   ├── depth
        │   ├── breadth
        │   ├── repetition
        │   ├── autonomy
        │   ├── context
        │   ├── confidence
        │   └── capability_summary
        │
        ├── requirement_match
        │   ├── match_strength
        │   ├── matched_elements[]
        │   ├── missing_elements[]
        │   ├── claim_eligibility
        │   ├── allowed_claim_scope
        │   └── match_notes
        │
        └── assessment_notes
```

---

## Design Rules

`EvidenceMap` should:

- evaluate job requirements individually;
- collect all materially relevant evidence rather than stopping at the first match;
- represent distinct real scenarios once;
- allow one scenario to support several requirements;
- group multiple sources describing the same underlying work;
- avoid double counting;
- distinguish depth, breadth, repetition, autonomy, context, and confidence;
- prevent repeated basic evidence from becoming advanced capability automatically;
- characterize candidate capability before determining requirement match;
- preserve provenance to the Professional Portfolio;
- explicitly represent unsupported requirements;
- distinguish requirement match from claim permission;
- preserve missing elements and factual boundaries;
- retain enough factual detail for future interview preparation;
- provide the planner with validated evidence without requiring it to rediscover the portfolio.

---

# 4. CVContentPlan

## Purpose

`CVContentPlan` defines the content strategy for one job application.

It determines:

> Given the validated employer requirements and validated candidate evidence, what deserves space in this CV?

Its primary inputs are:

```text
Validated JobSpec
        +
Validated Evidence Map
        +
CandidateProfile
```

The EvidenceMap determines what is supportable.

The CVContentPlan determines what is strategically worth communicating.

---

## Separation Between Planning and Writing

Planning answers:

> What should this CV communicate?

Writing later answers:

> How should the approved information be expressed?

Example:

```text
Planning decision:
Include OpenCV experience prominently in EXP-001.

Purpose:
Address REQ-006.

Evidence:
SCEN-012
SCEN-014
SCEN-017

Allowed scope:
Independent practical OpenCV use for scientific image processing.

Emphasize:
ROI tools, masks, contours, image/video processing.

Do not imply:
Object detection or tracking experience.
```

The planner does not need to produce the final polished bullet.

---

## Overall Structure

Conceptually:

```text
CVContentPlan
├── application_target
├── document_strategy
├── section_plan[]
├── planned_items[]
├── notable_omissions[]
└── planning_notes
```

---

## Application Target

Conceptually:

```text
ApplicationTarget
├── job_title
├── company
└── job_spec_reference
```

`job_title` and `company` may be repeated for human readability even when the authoritative source is the referenced JobSpec.

---

## Document Strategy

Conceptually:

```text
DocumentStrategy
├── target_length
├── primary_positioning
├── highest_priority_requirements[]
├── secondary_requirements[]
└── emphasis_notes
```

---

## Target Length

The planner may define a target such as:

```text
1 page
2 pages
```

This is a planning constraint rather than a guarantee of rendered pagination.

Rendering tests may later influence the rule.

---

## Primary Positioning

The planner may preserve a concise internal statement describing how the candidate should be positioned for this role.

Example:

```text
Scientific software developer with strong experience building
Python-based analysis workflows for experimental imaging and
time-series data.
```

This is strategic metadata.

It does not automatically become final CV text.

---

## Requirement Prioritization

Not every employer requirement deserves equal space.

Priority should consider factors such as:

```text
Employer importance
        +
Candidate evidence
        +
Role relevance
        +
Differentiation
        +
Available space
```

A partial match to a core responsibility may deserve more attention than a strong match to an insignificant nice-to-have.

---

# Section Plan

The planner determines which sections should appear and their intended order.

Conceptually:

```text
SectionPlan
├── section
├── order
├── purpose
└── importance
```

Possible sections include:

```text
SUMMARY
SKILLS
EXPERIENCE
PROJECTS
EDUCATION
PUBLICATIONS
PRESENTATIONS
LANGUAGES
```

Section selection should remain application-specific.

---

# Planned Content Items

The central planning object is `PlannedContentItem`.

Conceptually:

```text
PlannedContentItem
├── id
├── target_section
├── content_type
├── source_entity_ref
├── requirement_refs[]
├── evidence_refs[]
├── purpose
├── priority
├── inclusion_status
├── emphasis[]
├── allowed_claim_scope
├── prohibited_implications[]
├── length_guidance
└── planning_notes
```

---

## Planned Item Identifier

Each item should receive an identifier such as:

```text
PLAN-001
PLAN-002
```

This enables:

```text
REQ-006
   ↓
SCEN-012
SCEN-014
   ↓
PLAN-008
   ↓
CLAIM-011
```

---

## Source Entity Reference

Where applicable, the plan should reference a stable canonical entity.

For example:

```text
PLAN-011

target_section:
EXPERIENCE

source_entity_ref:
EXP-001
```

rather than using only:

```text
"Graduate Researcher — Université de Sherbrooke"
```

This prevents content from being attached to the wrong experience.

For projects or other entities not represented in CandidateProfile, the reference may point to another stable portfolio or evidence entity.

Exact reference rules will be defined during implementation.

---

## Requirement References

A planned item may address one or several employer requirements.

For example:

```text
requirement_refs:
- REQ-003
- REQ-007
```

The planner should avoid duplicating the same accomplishment merely because it addresses several requirements.

---

## Evidence References

Every significant tailored item should identify the validated scenarios that support it.

For example:

```text
evidence_refs:
- SCEN-012
- SCEN-014
```

The planner should not independently rediscover evidence from the Professional Portfolio.

---

## Purpose

Each planned item should explain why it deserves space.

Example:

```text
Purpose:
Demonstrate hands-on scientific Python development and automated
analysis workflow experience relevant to REQ-002 and REQ-005.
```

This is useful for debugging planning quality.

It lets the system ask:

> Why did the planner include this?

---

## Priority

Preliminary priorities may include:

```text
CRITICAL
HIGH
MEDIUM
LOW
```

Priority may later help resolve space constraints.

For example:

```text
CV too long
    ↓
review LOW-priority items first
```

rather than removing content arbitrarily.

---

## Inclusion Status

Possible values may include:

```text
INCLUDE
OPTIONAL
OMIT
```

However, the planner should not be required to create `OMIT` records for every unused item in the entire Professional Portfolio.

Omissions should be retained when they are strategically meaningful.

For example:

```text
Publication X considered
        ↓
OMIT
        ↓
Reason:
Low relevance and insufficient space
```

This distinguishes intentional omission from accidental omission without turning the plan into a complete inventory of everything not selected.

---

## Notable Omissions

The plan may optionally maintain a small collection of important content that was explicitly considered and omitted.

Conceptually:

```text
NotableOmission
├── source_entity_ref
├── reason
└── notes
```

This may replace or complement `OMIT` planned items if testing shows that structure to be cleaner.

The exact implementation should remain simple initially.

---

## Emphasis

Evidence often supports several aspects of a candidate's experience.

The planner can decide which dimensions are most useful for this application.

Example:

```text
Scenario:
Scientific analysis pipeline

Available evidence:
- Python
- automation
- image processing
- statistical analysis
- experimental research
- visualization
```

For one application:

```text
Emphasize:
- Python
- reusable workflows
- image processing
```

For another:

```text
Emphasize:
- quantitative analysis
- statistics
- experimental interpretation
```

The underlying reality remains unchanged.

---

## Allowed Claim Scope

The planner must inherit claim boundaries from the Validated Evidence Map.

For example:

```text
Allowed:
Scientific Python software development

Not allowed:
Production deployment experience
```

The planner may prioritize or reframe evidence, but it may not expand its factual scope.

---

## Prohibited Implications

Where important, the plan may explicitly retain boundaries that the writer must not cross.

For example:

```text
prohibited_implications:
- object-detection experience
- production deployment
- team leadership
```

These restrictions should normally originate from validated evidence limitations.

---

## Length Guidance

The planner may provide approximate guidance such as:

```text
one concise bullet
two bullets maximum
short skills entry
one-line education entry
```

Exact character budgets should not be introduced unless real rendering tests demonstrate that they are useful.

---

## Canonical Candidate Information

Some CV information is canonical rather than evidence-matched.

Examples include:

- name;
- contact information;
- education;
- official role titles;
- organizations;
- dates.

The planner may decide whether canonical records appear.

It must not rewrite them.

For example:

```text
CandidateProfile:
EXP-001
role_title = Graduate Researcher

Planner:
Include EXP-001

Writer:
Generate tailored accomplishment bullets

Draft:
role_title remains Graduate Researcher
```

---

## Evidence Reuse

One scenario may support several requirements:

```text
SCEN-014
   ├── REQ-003
   ├── REQ-007
   └── REQ-009
```

This does not require repeating the same CV content three times.

The planner should favor concise content that legitimately communicates several relevant strengths.

---

## Planning Validation

Initial Planning Validation should primarily use deterministic and structural checks.

Examples:

```text
Do requirement_refs exist?

Do evidence_refs exist?

Do source_entity_refs exist?

Is a referenced scenario actually associated with the stated requirement?

Is UNSUPPORTED evidence being used?

Does the planned claim scope remain within the EvidenceMap boundary?

Are section references valid?
```

A separate semantic AI reviewer should not be assumed necessary in V1.

If real testing shows recurring strategic planning failures, semantic planning review can be added later.

---

## Interview Traceability

Because planned items retain requirement and evidence references:

```text
CLAIM-011
      ↓
PLAN-008
      ↓
REQ-006
      +
SCEN-012
SCEN-014
```

later interview preparation can reconstruct:

- why the claim appeared;
- which employer need it addressed;
- which real experience supports it;
- what technical details can be discussed;
- which limitations remain important.

---

## Conceptual Structure

```text
CVContentPlan
│
├── application_target
│   ├── job_title
│   ├── company
│   └── job_spec_reference
│
├── document_strategy
│   ├── target_length
│   ├── primary_positioning
│   ├── highest_priority_requirements[]
│   ├── secondary_requirements[]
│   └── emphasis_notes
│
├── section_plan[]
│   └── SectionPlan
│       ├── section
│       ├── order
│       ├── purpose
│       └── importance
│
├── planned_items[]
│   └── PlannedContentItem
│       ├── id
│       ├── target_section
│       ├── content_type
│       ├── source_entity_ref
│       ├── requirement_refs[]
│       ├── evidence_refs[]
│       ├── purpose
│       ├── priority
│       ├── inclusion_status
│       ├── emphasis[]
│       ├── allowed_claim_scope
│       ├── prohibited_implications[]
│       ├── length_guidance
│       └── planning_notes
│
├── notable_omissions[]
└── planning_notes
```

---

## Design Rules

`CVContentPlan` should:

- use validated requirements and evidence;
- avoid rediscovering portfolio evidence;
- decide what deserves CV space before polished writing;
- preserve traceability;
- distinguish factual support from strategic relevance;
- preserve evidence boundaries;
- avoid unnecessary repetition;
- reference canonical entities rather than copying their facts;
- make important omissions observable where useful;
- remain flexible across different role types;
- provide enough guidance for writing without becoming final prose.

---

# 5. CVDraft

## Purpose

`CVDraft` is the complete structured representation of the CV before rendering.

It combines:

```text
canonical candidate information
        +
application-specific CV writing
        +
traceability information
```

It contains the content intended for the final document while remaining independent from the selected renderer.

Conceptually:

```text
CVContentPlan
        +
Validated Evidence Map
        ↓
CV Writing
        ↓
Tailored CV Content
        +
CandidateProfile
        ↓
Draft Assembly
        ↓
CVDraft
        ↓
CV Draft Validation
        ↓
Validated CVDraft
```

---

# Separation Between Writing and Assembly

## CV Writing

The writer may improve:

- wording;
- clarity;
- concision;
- professional tone;
- relevance;
- emphasis.

It must not change:

- factual meaning;
- capability depth;
- responsibility;
- autonomy;
- context;
- quantitative facts;
- claim boundaries;
- canonical information.

---

## Draft Assembly

Draft Assembly combines the tailored writing with canonical records.

For example:

```text
CandidateProfile:
EXP-001
Graduate Researcher
Université de Sherbrooke
2018–2026

        +

Tailored CV claim:
Developed Python-based scientific image-processing workflows...

        ↓

Complete ExperienceEntry
```

This stage should be primarily deterministic.

---

# CV Claims

A `CVClaim` represents a significant tailored statement intended to appear directly in the rendered CV.

Conceptually:

```text
CVClaim
├── id
├── text
├── plan_refs[]
├── requirement_refs[]
├── evidence_refs[]
├── claim_scope
└── validation_notes
```

Examples include:

- experience bullets;
- project bullets;
- meaningful summary statements;
- other tailored factual assertions.

Canonical metadata such as:

```text
Université de Sherbrooke
```

does not need claim-level evidence tracking.

---

## Single Source of Truth for Claim Text

Claim text should not be duplicated in both a rendered bullet and a separate claim registry.

Instead, the rendered content itself should contain the traceable `CVClaim`.

For example:

```text
ExperienceEntry
└── bullets[]
    └── CVClaim
```

rather than:

```text
ExperienceEntry
└── bullets[] = strings

and separately:

claim_registry[]
└── same text repeated again
```

This avoids synchronization errors.

If a global claim index is useful later, it can be derived from the CVDraft rather than becoming a second authoritative copy.

---

## Claim Identifier

Each significant claim should receive a stable identifier.

For example:

```text
CLAIM-001
CLAIM-002
```

This preserves:

```text
REQ-006
   ↓
SCEN-012
SCEN-014
   ↓
PLAN-008
   ↓
CLAIM-011
   ↓
Final PDF
```

---

## Plan References

Each tailored claim should normally identify the plan item that authorized it.

For example:

```text
CLAIM-011

plan_refs:
- PLAN-008
```

This allows validation to ask:

> Was this statement actually planned?

---

## Requirement References

Claims should identify the employer requirements they address when applicable.

For example:

```text
requirement_refs:
- REQ-004
- REQ-009
```

---

## Evidence References

Claims should identify the validated scenarios supporting them.

For example:

```text
evidence_refs:
- SCEN-012
- SCEN-014
- SCEN-017
```

This supports validation and future interview preparation.

---

## Claim Scope

Where useful, the claim should preserve the approved factual boundary.

Example:

```text
Claim:
Developed scientific image-processing workflows using OpenCV.

Allowed scope:
Practical OpenCV use for scientific image processing.

Excluded implication:
Advanced object detection or tracking expertise.
```

If later testing shows `claim_scope` is redundant because the EvidenceMap reference is sufficient, it may be simplified.

---

# Candidate Header

The header should be assembled from canonical information.

Conceptually:

```text
CandidateHeader
├── full_name
├── location
├── email
├── phone
└── professional_links[]
```

The assembly stage may omit irrelevant fields.

It should not rewrite their values.

---

# Professional Summary

When included, the summary contains final application-specific wording.

Conceptually:

```text
ProfessionalSummary
├── text
├── plan_refs[]
├── requirement_refs[]
└── evidence_refs[]
```

A summary may synthesize several validated capabilities.

Because summaries often compress several claims into a small amount of text, they require particularly careful evidence validation.

If implementation shows that summary text is better represented as one or more `CVClaim` objects, the model may be unified accordingly.

---

# CV Sections

The draft should represent the ordered sections intended for rendering.

Conceptually:

```text
CVSection
├── section_type
├── title
├── order
└── entries[]
```

Possible section types include:

```text
SUMMARY
SKILLS
EXPERIENCE
PROJECTS
EDUCATION
PUBLICATIONS
PRESENTATIONS
LANGUAGES
```

The exact set is application-specific.

The renderer should not independently make strategic section-selection decisions.

---

# Experience Entries

Conceptually:

```text
ExperienceEntry
├── canonical_experience_ref
├── role_title
├── organization
├── location
├── start_date
├── end_date
└── bullets[]
    └── CVClaim
```

Fields such as:

```text
role_title
organization
location
dates
```

should normally come directly from the referenced CandidateProfile record.

The tailored bullets come from CV Writing.

---

# Project Entries

Conceptually:

```text
ProjectEntry
├── source_entity_ref
├── project_name
├── context
├── date_or_period
├── technologies[]
└── bullets[]
    └── CVClaim
```

Stable project information should come from documented portfolio records or another canonical source when available.

It should not be invented during writing.

---

# Skills Section

Conceptually:

```text
SkillGroup
├── category
└── skills[]
```

Skills included in the final CV must be supported by validated evidence or another canonical documented source.

A technology must not appear simply because it appears in the job posting.

If implementation requires direct evidence traceability for individual skills, a richer structure may be introduced:

```text
SkillEntry
├── name
└── evidence_refs[]
```

This should only be added if practically useful.

---

# Education Entries

Education should be assembled from CandidateProfile references.

Conceptually:

```text
EducationEntry
├── candidate_profile_ref
├── degree
├── field
├── institution
├── location
├── start_date
├── end_date
└── status
```

Tailoring may affect inclusion or ordering.

It must not modify the credential.

---

# Publications and Presentations

When included, bibliographic information should remain linked to documented portfolio records.

Conceptually:

```text
PublicationEntry
├── source_ref
├── citation
└── optional_context
```

and:

```text
PresentationEntry
├── source_ref
├── title
├── event
├── date
└── location
```

Canonical bibliographic facts should not be regenerated from memory when source information exists.

---

# Evidence-Backed Synthesis

The writer may combine several approved evidence scenarios into one concise claim.

For example:

```text
SCEN-012
→ ROI selection

SCEN-014
→ masks and contours

SCEN-017
→ image/video processing
```

may become:

```text
Developed OpenCV-based scientific image-processing tools for
interactive ROI selection, masking, contour analysis, and
image/video workflows.
```

This is acceptable because the statement remains within the combined evidence.

Synthesis must not introduce unsupported conclusions.

---

# Quantitative Claims

Numerical statements require strong traceability.

Examples include:

```text
20+ scripts
2448 × 2048 images
1 frame per second
60% reduction
3+ years
```

Numbers should only be included when supported by:

- canonical candidate information; or
- validated evidence.

The writer must not:

- round values upward misleadingly;
- invent scale;
- convert qualitative descriptions into unsupported quantities;
- combine unrelated measurements into a misleading result.

---

# Canonical Facts

Canonical facts should normally enter the CVDraft deterministically.

Examples:

- name;
- contact information;
- official role titles;
- organizations;
- dates;
- degrees;
- institutions;
- credentials;
- language information.

Conceptually:

```text
CandidateProfile
      ↓
Draft Assembly
      ↓
CVDraft
```

rather than:

```text
CandidateProfile
      ↓
AI regenerates facts
      ↓
CVDraft
```

---

# Application Reference

The draft should remain associated with its target application.

Conceptually:

```text
ApplicationReference
├── company
├── job_title
├── job_spec_reference
└── content_plan_reference
```

The references are authoritative.

Copied labels such as company and title may be retained for readability.

---

# Draft Metadata

The draft may preserve practical generation metadata.

Conceptually:

```text
DraftMetadata
├── generated_at
├── version
├── source_plan_reference
└── generation_notes
```

Later implementation may add:

- prompt version;
- model/backend version;
- application identifier;
- pipeline version.

These should only be stored when they provide debugging or reproducibility value.

---

# CV Draft Validation

The CVDraft passes through a mandatory validation stage.

---

## Canonical Fact Validation

Check consistency against CandidateProfile.

Examples:

```text
Correct role title?
Correct organization?
Correct degree?
Correct dates?
Correct contact information?
```

These checks should be deterministic wherever possible.

---

## Evidence Fidelity Validation

Check that significant tailored statements remain supported by their referenced validated evidence.

Questions include:

```text
Does the evidence actually support the claim?

Did the writer add a technology?

Did the writer increase capability depth?

Did the writer exaggerate autonomy?

Did the writer invent an outcome?

Did the writer distort the professional context?

Did the writer introduce an unsupported number?
```

This requires semantic validation.

---

## Planning Fidelity Validation

Check that the writer followed the approved CVContentPlan.

Examples:

```text
Was the claim authorized?

Were important planned items omitted?

Were prohibited implications avoided?

Did the writer introduce unplanned strategic content?

Was content attached to the correct experience or project?
```

---

## Internal Consistency Validation

Examples include:

```text
same role → same dates everywhere

same credential → same institution everywhere

summary → not broader than supporting evidence

duplicate bullets → avoided

technologies → represented consistently
```

---

# Validation Result

Before validation:

```text
CVDraft
```

After validation:

```text
Validated CVDraft
```

Only the validated version should proceed to rendering.

---

# Renderer Independence

The CVDraft should describe document meaning rather than RenderCV, Typst, LaTeX, or other renderer syntax.

For example:

```text
ExperienceEntry
├── role_title
├── organization
├── dates
└── bullets[]
```

rather than renderer-specific fields.

The transformation belongs in:

```text
Validated CVDraft
        ↓
Render Adapter
        ↓
Renderer-specific input
```

---

# Interview Preparation

Because claims maintain requirement, plan, and evidence references, the submitted CV can later support interview preparation.

Conceptually:

```text
Submitted CV
      +
CVDraft
      +
Validated Evidence Map
      +
Validated JobSpec
      ↓
Interview Preparation
```

For each important claim the system can reconstruct:

- which requirement motivated it;
- which evidence supported it;
- what work was actually performed;
- which technical details are available;
- what level of autonomy was documented;
- which limitations remain important;
- which scenarios can support interview answers.

The CVDraft therefore remains part of the persisted application record rather than being only a temporary rendering artifact.

---

# Conceptual Structure

```text
CVDraft
│
├── application_reference
│   ├── company
│   ├── job_title
│   ├── job_spec_reference
│   └── content_plan_reference
│
├── candidate_header
│   ├── full_name
│   ├── location
│   ├── email
│   ├── phone
│   └── professional_links[]
│
├── professional_summary
│
├── sections[]
│   └── CVSection
│       ├── section_type
│       ├── title
│       ├── order
│       └── entries[]
│           └── section-specific entry
│               └── significant tailored statements
│                   └── CVClaim
│                       ├── id
│                       ├── text
│                       ├── plan_refs[]
│                       ├── requirement_refs[]
│                       ├── evidence_refs[]
│                       ├── claim_scope
│                       └── validation_notes
│
└── draft_metadata
```

---

# Design Rules

`CVDraft` should:

- represent the complete CV before rendering;
- contain final application-specific wording;
- remain independent from rendering technology;
- combine canonical data deterministically wherever practical;
- preserve the strategy established by CVContentPlan;
- make significant claims directly traceable;
- avoid duplicating claim text in several structures;
- allow evidence-backed synthesis without unsupported extrapolation;
- preserve claim boundaries established by the EvidenceMap;
- treat quantitative claims conservatively;
- pass semantic and deterministic validation before rendering;
- preserve enough traceability for interview preparation.

---

# Model Relationship Summary

The complete conceptual data flow is:

```text
Professional Portfolio
        ↓
CandidateProfile
```

and:

```text
Job Posting
        ↓
JobSpec
        ↓
Validated JobSpec
        ↓
EvidenceMap
        ↓
Validated Evidence Map
        ↓
CVContentPlan
        ↓
CVDraft
        ↓
Validated CVDraft
        ↓
Rendering
        ↓
Final PDF
```

Traceability across tailored content follows:

```text
Original Job Posting
        ↓
REQ-xxx
        ↓
SCEN-xxx
        ↓
PLAN-xxx
        ↓
CLAIM-xxx
        ↓
Final PDF
```

Canonical information follows:

```text
Professional Portfolio
        ↓
CandidateProfile
        ↓
EXP-xxx / EDU-xxx / canonical record
        ↓
CVDraft
        ↓
Final PDF
```

These relationships form the conceptual basis for the Pydantic implementation.

The models should now be tested through implementation and real job postings rather than expanded indefinitely on paper.