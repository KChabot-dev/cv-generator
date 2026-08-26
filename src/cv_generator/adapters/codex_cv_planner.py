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
   exactly match an experience ID from CandidateProfile. Every accomplishment,
   responsibility, technology, outcome, and evidence scenario used by that
   planned item must be attributable to that same candidate experience.
   Never transfer evidence from one CandidateProfile experience to another,
   even when the evidence is highly relevant to the target job.

10. For education entries, source_entity_ref must exactly match an education
    ID from CandidateProfile.

11. For content types that do not correspond to a CandidateProfile entity,
    source_entity_ref may be null.

12. For EVERY requirement_ref on an included or optional planned item, at
    least one evidence_ref on that SAME planned item must exactly match a
    scenario_ref listed in that requirement's
    EvidenceAssessment.scenario_matches.

    Treat this as a strict lookup constraint, not a semantic judgment.
    Before adding a requirement_ref to a planned item:
    - find that requirement's EvidenceAssessment,
    - read its scenario_matches,
    - verify that at least one of the planned item's evidence_refs appears
      there exactly.

    If none of the item's evidence_refs is explicitly approved for that
    requirement, DO NOT add the requirement_ref. Remove the requirement from
    that planned item rather than substituting evidence that merely seems
    related.

13. When one planned item targets multiple requirements, perform the rule-12
    lookup independently for EACH requirement_ref. Every requirement_ref must
    have its own explicitly approved supporting scenario among that same
    item's evidence_refs. Never attach a requirement to an item simply because
    the item's overall topic, experience, or capability seems relevant.

14. Preserve quantitative and technical facts faithfully when creating
    emphasis, allowed_claim_scope, purpose, and planning notes. You may
    shorten or prioritize facts for CV space, but do not change what a
    number measures, its units, reference value, direction, or experimental
    meaning. If a quantitative fact cannot be shortened without changing its
    meaning, retain the necessary context or omit that detail.

15. Use notable_omissions when there is a useful reason to record why a
    candidate entity was intentionally left out.

16. Plan a concise professional CV appropriate for the role. Treat CV space
    as scarce. Prefer relevance, strength of evidence, and distinctiveness
    over completeness. Supported content does not need to appear merely
    because evidence exists for it.

17. Prefer a one-page CV when the candidate's strongest role-relevant case can
    be presented without omitting critical evidence. Use two pages only when
    genuinely important evidence for required or core job requirements would
    otherwise need to be removed. Set document_strategy.target_length
    accordingly.

18. primary_positioning should summarize how the candidate should be
    positioned for this specific role without inventing a new professional
    identity.

19. highest_priority_requirements and secondary_requirements must use exact
    JobSpec requirement IDs.

20. prohibited_implications should explicitly capture claims that the writer
    must avoid when the evidence has meaningful limitations.

21. Treat the skills section as a compact technical index, not as an inventory
    of everything the candidate can support. Prefer 3 to 4 skill groups and
    approximately 12 to 18 distinct skill labels total when the evidence and
    target role permit it.

22. Prioritize skill content in this order:
    a. direct relevance to highest-priority job requirements,
    b. strength and specificity of supporting evidence,
    c. technical distinctiveness,
    d. information not already obvious from another selected skill.
    Do not include lower-value skills merely to make a group look complete.

23. Prefer concrete technologies, tools, methods, technical domains, and
    clearly recognizable engineering practices in the skills section.
    Collaboration, communication, ownership, adaptability, knowledge transfer,
    and similar capabilities should normally be demonstrated through
    experience bullets unless they are unusually important to the target role.

24. For planned skill items, emphasis must be a ranked shortlist of the
    strongest display-worthy skills, not a dump of all supported concepts.
    Prefer roughly 4 to 6 concise emphasis items per skill group. Combine,
    shorten, or omit overlapping concepts when doing so stays within the
    approved evidence and claim scope.

25. Avoid using multiple skill labels for substantially the same capability.
    For example, do not separately surface several near-duplicate concepts
    such as debugging, root-cause analysis, verification, validation, and
    reliability unless the target job clearly makes those distinctions useful.

26. For the candidate's primary experience, plan approximately 4 to 5
    accomplishment bullets total. For secondary experiences, prefer
    approximately 1 to 3 bullets. Select the strongest evidence rather than
    trying to represent every supported responsibility or accomplishment.

27. An experience_entry planned item establishes that the role should appear
    and may define its overall positioning and claim boundaries. When
    dedicated experience_bullet planned items are also created for that same
    experience, do not use the experience_entry as an additional generic
    accomplishment bullet unless it contributes important non-duplicative
    evidence.

28. Avoid cross-section duplication. Give information a primary purpose:
    - summary positions the candidate,
    - skills index the most relevant capabilities,
    - experience demonstrates those capabilities with evidence and outcomes.
    Repetition across sections is acceptable only when the information is
    critical to the target role and each section adds a distinct function.

29. Use inclusion_status deliberately. "include" means the content deserves
    scarce CV space. Use "optional" for useful secondary material that may be
    dropped for space, and omit supported evidence that does not materially
    improve the application.

30. Return every field required by the output schema. Use empty lists when
    there are no list values and null for nullable fields when no supported
    value exists.

CANDIDATE PROFILE:

{candidate_profile.model_dump_json(indent=2)}

JOB SPEC:

{job_spec.model_dump_json(indent=2)}

EVIDENCE MAP:

{evidence_map.model_dump_json(indent=2)}
""".strip()