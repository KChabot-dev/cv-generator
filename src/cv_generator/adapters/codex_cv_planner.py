from cv_generator.adapters.codex_runner import CodexStructuredRunner
from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.job import JobSpec
from cv_generator.domain.planning import CVContentPlan


class CodexCVPlanner:
    def __init__(self, executable: str = "codex.cmd") -> None:
        self.runner = CodexStructuredRunner(
            executable=executable
        )

    def plan(
        self,
        candidate_profile: CandidateProfile,
        job_spec: JobSpec,
        evidence_map: EvidenceMap,
    ) -> CVContentPlan:
        prompt = _build_prompt(
            candidate_profile,
            job_spec,
            evidence_map,
        )

        return self.runner.run(
            prompt,
            CVContentPlan,
        )


def _build_prompt(
    candidate_profile: CandidateProfile,
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
) -> str:
    return f"""
You are the CV Planning stage of a CV generation system.

Your task is to produce a structured CVContentPlan for the supplied
application.

You are planning what the CV should contain. Do not write the final CV prose.

Use only:
- canonical candidate facts from CandidateProfile,
- job requirements from JobSpec,
- approved evidence and claim limits from EvidenceMap.

Rules:

1. Build a CV strategy targeted to the supplied job.
2. Prioritize requirements marked required or core responsibility when
   supported by strong candidate evidence.
3. Use only requirement IDs that exist in JobSpec.
4. Use only evidence scenario IDs that exist in EvidenceMap.
5. A requirement may appear in requirement_refs for an included or optional
   planned item only if its EvidenceAssessment has at least one
   scenario_match and its claim_eligibility is not "none". Requirements with
   no scenario_matches or claim_eligibility="none" must not be targeted by
   included or optional content.
6. Respect claim_eligibility, allowed_claim_scope, limitations, and missing
   elements from EvidenceMap. Do not plan stronger claims than the evidence
   supports.
7. Reuse strong evidence across multiple relevant requirements when useful,
   without creating unnecessary duplicate content.
8. Give every planned content item a unique sequential ID such as PLAN-001,
   PLAN-002, and so on.
9. For experience entries or experience bullets, source_entity_ref must
   exactly match an experience ID from CandidateProfile.
10. For education entries, source_entity_ref must exactly match an education
    ID from CandidateProfile.
11. For content types that do not correspond to a CandidateProfile entity,
    source_entity_ref may be null.
12. For EVERY requirement_ref on an included or optional planned item, at
    least one evidence_ref on that SAME planned item must exactly match a
    scenario_ref listed in that requirement's
    EvidenceAssessment.scenario_matches. Do not use a scenario merely because
    it seems semantically related. Use only scenarios explicitly approved for
    that requirement in EvidenceMap.
13. When one planned item targets multiple requirements, verify the evidence
    relationship separately for each requirement. The item's evidence_refs
    must collectively contain at least one explicitly approved scenario for
    every requirement_ref.
14. Use notable_omissions when there is a useful reason to record why a
    candidate entity was intentionally left out.
15. Plan a concise professional CV appropriate for the role. Prefer relevance
    over completeness.
16. primary_positioning should summarize how the candidate should be
    positioned for this specific role without inventing a new professional
    identity.
17. highest_priority_requirements and secondary_requirements must use exact
    JobSpec requirement IDs.
18. prohibited_implications should explicitly capture claims that the writer
    must avoid when the evidence has meaningful limitations.
19. Return every field required by the output schema. Use empty lists when
    there are no list values and null for nullable fields when no supported
    value exists.

CANDIDATE PROFILE:

{candidate_profile.model_dump_json(indent=2)}

JOB SPEC:

{job_spec.model_dump_json(indent=2)}

EVIDENCE MAP:

{evidence_map.model_dump_json(indent=2)}
""".strip()