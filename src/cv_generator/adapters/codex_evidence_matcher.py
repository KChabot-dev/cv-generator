from cv_generator.adapters.codex_runner import CodexStructuredRunner
from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.job import JobSpec
from cv_generator.domain.portfolio import PortfolioContext


class CodexEvidenceMatcher:
    def __init__(self, executable: str = "codex.cmd") -> None:
        self.runner = CodexStructuredRunner(
            executable=executable
        )

    def match(
        self,
        candidate_profile: CandidateProfile,
        job_spec: JobSpec,
        portfolio_context: PortfolioContext,
    ) -> EvidenceMap:
        prompt = _build_prompt(
            candidate_profile,
            job_spec,
            portfolio_context,
        )

        return self.runner.run(
            prompt,
            EvidenceMap,
        )


def _build_prompt(
    candidate_profile: CandidateProfile,
    job_spec: JobSpec,
    portfolio_context: PortfolioContext,
) -> str:
    portfolio_documents = "\n\n".join(
        (
            f"--- SOURCE DOCUMENT: {document.source_id} ---\n"
            f"{document.content}\n"
            f"--- END SOURCE DOCUMENT ---"
        )
        for document in portfolio_context.documents
    )

    return f"""
You are the Evidence Matching stage of a CV generation system.

Your task is to compare the validated job requirements with the candidate's
documented Professional Portfolio and return an EvidenceMap matching the
provided JSON Schema.

Use CandidateProfile to establish the candidate's canonical experience,
education, and other entity IDs. Use the Professional Portfolio as the
evidence source for what the candidate actually did.

Rules:

1. Assess every requirement in the JobSpec.

2. Use only evidence contained in the supplied portfolio documents.

3. Do not invent candidate experience, skills, responsibilities, outcomes,
   proficiency, or evidence.

4. Every source_document value must exactly match one of the supplied
   SOURCE DOCUMENT identifiers.

5. supporting_text must be grounded in the cited source document.

6. Every EvidenceScenario must populate source_entity_refs using only exact
   canonical entity IDs supplied by CandidateProfile when the evidence can be
   attributed to those entities.

7. source_entity_refs represent which canonical candidate entities the
   scenario actually belongs to. Do not assign an entity merely because the
   scenario would be useful for that experience or for the target job.

8. For evidence documenting work performed during a specific candidate
   experience, include that exact experience ID in source_entity_refs. Never
   transfer evidence from one experience to another.

9. If a scenario is genuinely supported by work spanning multiple canonical
   entities, source_entity_refs may contain multiple exact CandidateProfile
   IDs, but every listed entity must be independently supported by the
   portfolio evidence.

10. If portfolio evidence cannot be reliably attributed to a canonical
    CandidateProfile entity, use an empty source_entity_refs list rather than
    guessing an entity ID.

11. Reuse evidence scenarios when the same documented experience supports
    multiple job requirements.

12. Distinguish direct, partial, weak, and unsupported matches
    conservatively.

13. If the portfolio does not support a requirement, mark it unsupported
    rather than inferring or exaggerating capability.

14. An unsupported requirement has a strict representation:
    - match_strength must be "unsupported",
    - claim_eligibility must be "none",
    - scenario_matches must be an empty list,
    - capability_assessment must be null,
    - allowed_claim_scope must be null.
    Never attach an evidence scenario or capability assessment to an
    unsupported requirement.

15. If scenario_matches contains one or more scenarios, the requirement must
    not be represented as unsupported. Choose the supported match strength
    conservatively from strong, partial, or weak according to the evidence.

16. Respect documented limitations and autonomy levels.

17. Preserve quantitative and technical facts faithfully. Do not alter what
    a number measures, its units, reference value, direction, or experimental
    meaning.

18. Use the exact requirement IDs supplied by the JobSpec.

19. Return every field required by the output schema. Use empty lists when
    there are no list values and null for nullable fields when no value is
    supported by the portfolio.

CANDIDATE PROFILE:

{candidate_profile.model_dump_json(indent=2)}

VALIDATED JOB SPEC:

{job_spec.model_dump_json(indent=2)}

PROFESSIONAL PORTFOLIO:

{portfolio_documents}
""".strip()