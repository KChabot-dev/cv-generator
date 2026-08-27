from cv_generator.adapters.codex_runner import CodexStructuredRunner
from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.draft import CVDraft
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.planning import CVContentPlan


class CodexCVWriter:
    def __init__(self, executable: str = "codex.cmd") -> None:
        self.runner = CodexStructuredRunner(
            executable=executable
        )

    def write(
        self,
        candidate_profile: CandidateProfile,
        evidence_map: EvidenceMap,
        content_plan: CVContentPlan,
    ) -> CVDraft:
        prompt = _build_prompt(
            candidate_profile,
            evidence_map,
            content_plan,
        )

        return self.runner.run(
            prompt,
            CVDraft,
        )


def _build_prompt(
    candidate_profile: CandidateProfile,
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
) -> str:
    return f"""
You are the CV Writing stage of a CV generation system.

Your task is to convert the approved CVContentPlan into a structured CVDraft
matching the provided JSON Schema.

The planning stage has already decided what content is allowed. Do not
redesign the CV strategy.

Use only:
- canonical facts from CandidateProfile,
- approved evidence from EvidenceMap,
- included or optional content authorized by CVContentPlan.

General rules:

1. Follow CVContentPlan closely. Do not introduce content that the plan does
   not authorize.
2. Do not create claims for planned items whose inclusion_status is "omit".
3. Every DraftClaim must reference an existing plan_item_ref from
   CVContentPlan.
4. requirement_refs on a DraftClaim must be a subset of the requirement_refs
   approved by that plan item.
5. evidence_refs on a DraftClaim must be a subset of the evidence_refs
   approved by that plan item.
6. Respect allowed_claim_scope and every prohibited_implication in the
   corresponding plan item.
7. Do not invent candidate facts, employers, dates, locations, degrees,
   skills, tools, outcomes, metrics, responsibilities, seniority, autonomy,
   project facts, or proficiency.
8. Preserve canonical CandidateProfile values exactly for candidate identity,
   experience role titles, organizations, education degrees, fields, and
   institutions.
9. For DraftExperience.source_entity_ref, use the exact CandidateProfile
   experience ID authorized by the plan item.
10. For DraftEducation.source_entity_ref, use the exact CandidateProfile
    education ID authorized by the plan item.
11. Use claim basis "canonical" when a claim comes only from CandidateProfile,
    "evidence" when it comes only from EvidenceMap, and "mixed" when both are
    required.
12. A canonical DraftClaim must contain appropriate source_entity_refs.
13. An evidence DraftClaim must contain appropriate evidence_refs.
14. A mixed DraftClaim must contain both source_entity_refs and evidence_refs.
15. Give claims unique sequential IDs such as CLAIM-001, CLAIM-002, and so on.
16. Every generated DraftClaim must be referenced by at least one visible
    CVDraft element. Do not create orphan claims that appear only in the
    claims list.
17. Professional summary, skill groups, experience bullets, project bullets,
    education entries, publications, presentations, and languages should
    reference the DraftClaim IDs that support their wording.
18. Keep wording concise, specific, professional, and appropriate for a CV.
19. Prefer direct evidence-backed wording over promotional or inflated
    language.
20. Do not claim unsupported technologies or qualifications merely because
    they appear in the target job.
21. application_reference must use the target company and job title from
    CVContentPlan.
22. content_plan_ref should identify the supplied content plan. Use
    "CVContentPlan" unless the supplied plan provides a more specific
    reference.
23. job_spec_ref should use
    CVContentPlan.application_target.job_spec_reference.
24. Return every field required by the output schema. Use empty lists when
    there are no list values and null for nullable fields when no supported
    value exists.

Skill-section presentation rules:

25. Treat skill_groups as a compact, scan-oriented CV section, not as a
    second experience section.
26. Prefer 3 to 4 skill groups when the approved content permits it. Do not
    omit an included planned item solely to meet this target.
27. Keep skill-group labels short and recruiter-scannable, preferably 2 to
    4 words. Preserve the meaning and claim boundaries of the corresponding
    planned content.
28. Keep individual skill strings concise, preferably 1 to 4 words. Favor
    concrete technologies, methods, techniques, and technical domains over
    sentence-like capability descriptions.
29. For collaboration, quality, or workflow capabilities that are approved
    by the plan, express them as compact CV labels rather than narrative
    phrases. For example, prefer "Requirements translation" over
    "Cross-disciplinary requirements translation" when both express the same
    approved scope.
30. Avoid repeating long descriptions that are already demonstrated in
    experience or project bullets. Skill groups should index capabilities;
    experience and project bullets should provide the evidence and context.
31. Prefer roughly 4 to 6 skill strings per group when possible. Prioritize
    the content most relevant to the target role according to CVContentPlan.
32. Do not invent, broaden, or add a technology or skill merely to make a
    skill group look more complete. All existing evidence and plan-boundary
    rules still apply.
33. Skill-group labels must be short but also grammatically natural and
    professionally recognizable. Do not remove conjunctions or punctuation
    merely to shorten a label. For example, prefer
    "Instrumentation & Automation" over "Instrumentation Automation".
34. When combining related skills into a compact label using "/" or "&",
    preserve the meaning and evidence boundaries of the approved plan. Do not
    create a broader composite capability that the evidence does not support.

Experience-section rules:

35. When an experience has both an experience_entry plan item and dedicated
    experience_bullet plan items, use the experience_entry to establish the
    role, organization, dates, overall positioning, and claim boundaries.
    Do not create an additional accomplishment bullet solely from the
    experience_entry.
36. For an experience with dedicated experience_bullet plan items, generate
    bullets from those dedicated items. Do not exceed their number by adding
    a generic role-summary bullet.
37. Order experience bullets by application value rather than mechanically by
    plan-item ID. Prioritize critical items and direct technical
    accomplishments before broader contextual or collaboration evidence when
    their relevance differs.
38. Each experience bullet should communicate one primary accomplishment or
    capability with its strongest useful evidence. Avoid repeating wording
    already used in the professional summary or another bullet. Prefer one
    concise sentence when possible while preserving important technical
    specificity and quantitative results.
39. Treat length_guidance as a real space budget. For a primary experience,
    normally produce about 4 to 5 bullets total; for secondary experiences,
    normally produce about 1 to 3 bullets. Do not add content merely because
    additional evidence exists.

Project-section rules:

40. For every included plan item with target_section "projects" and
    content_type "project_entry", create a corresponding DraftProject.
41. A DraftProject is a standalone project and must not be placed inside a
    DraftExperience merely because its evidence is relevant to an experience.
42. Use a concise project title supported by the approved plan and EvidenceMap.
    Do not invent a project name that is not supported by the supplied data.
43. DraftProject.date_text is optional. Use a supported project date when one
    is available from the approved evidence; otherwise use null rather than
    inventing a date.
44. Generate project bullets according to the project's emphasis,
    allowed_claim_scope, prohibited_implications, and length_guidance.
45. When a project_entry explicitly requests multiple distinct bullets, such
    as one architecture bullet and one validation/testing bullet, represent
    those as separate DraftProject bullets rather than collapsing them into
    one long sentence.
46. Each project bullet must reference the DraftClaim IDs supporting that
    bullet.
47. Project-related DraftClaims must therefore be attached to the matching
    DraftProject bullets and must not remain only in the claims list.
48. Keep project content distinct from employment experience. Do not assign
    source_entity_refs to a project claim unless the approved evidence
    actually requires canonical CandidateProfile entities.
49. Included projects must be represented in CVDraft.projects. Optional
    projects may be included when doing so is consistent with
    document_strategy, planning_notes, and the requested document length.
50. When space is constrained, follow the priorities and explicit omission
    order in CVContentPlan rather than arbitrarily removing a critical
    project.
51. Avoid repeating a project's full technology list if those technologies
    already appear in skill_groups. Use project bullets primarily to show
    architecture, implementation, validation, outcomes, or other concrete
    evidence.
52. Do not turn a personal or independent project into employment history.
    Preserve the distinction between project evidence and canonical
    CandidateProfile experience.

Education and language rules:

53. Build education entries only from education_entry plan items authorized
    by CVContentPlan and the matching canonical CandidateProfile records.
54. Preserve canonical degree, field, institution, and source_entity_ref
    values exactly.
55. For languages, preserve the canonical language and proficiency values from
    CandidateProfile.
56. If a language plan item produces a DraftClaim, attach its claim ID to the
    corresponding DraftLanguage.claim_refs.
57. Do not generate a language DraftClaim that is left unreferenced in the
    visible language section.
58. Keep language presentation concise unless CVContentPlan explicitly
    authorizes supporting narrative.

CANDIDATE PROFILE:

{candidate_profile.model_dump_json(indent=2)}

EVIDENCE MAP:

{evidence_map.model_dump_json(indent=2)}

APPROVED CV CONTENT PLAN:

{content_plan.model_dump_json(indent=2)}
""".strip()