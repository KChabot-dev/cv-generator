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

Rules:

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
   or proficiency.
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
16. Professional summary, skill groups, experience bullets, education
    details, publications, and presentations should reference the DraftClaim
    IDs that support their wording.
17. Keep wording concise, specific, professional, and appropriate for a CV.
18. Prefer direct evidence-backed wording over promotional or inflated
    language.
19. Do not claim unsupported technologies or qualifications merely because
    they appear in the target job.
20. application_reference must use the target company and job title from
    CVContentPlan.
21. content_plan_ref should identify the supplied content plan. Use
    "CVContentPlan" unless the supplied plan provides a more specific
    reference.
22. job_spec_ref should use
    CVContentPlan.application_target.job_spec_reference.
23. Return every field required by the output schema. Use empty lists when
    there are no list values and null for nullable fields when no supported
    value exists.

CANDIDATE PROFILE:

{candidate_profile.model_dump_json(indent=2)}

EVIDENCE MAP:

{evidence_map.model_dump_json(indent=2)}

APPROVED CV CONTENT PLAN:

{content_plan.model_dump_json(indent=2)}
""".strip()