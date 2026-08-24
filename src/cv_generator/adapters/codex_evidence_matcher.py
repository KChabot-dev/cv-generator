from cv_generator.adapters.codex_runner import CodexStructuredRunner
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
        job_spec: JobSpec,
        portfolio_context: PortfolioContext,
    ) -> EvidenceMap:
        prompt = _build_prompt(
            job_spec,
            portfolio_context,
        )

        return self.runner.run(
            prompt,
            EvidenceMap,
        )


def _build_prompt(
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

Rules:

1. Assess every requirement in the JobSpec.
2. Use only evidence contained in the supplied portfolio documents.
3. Do not invent candidate experience, skills, responsibilities, outcomes,
   proficiency, or evidence.
4. Every source_document value must exactly match one of the supplied
   SOURCE DOCUMENT identifiers.
5. supporting_text must be grounded in the cited source document.
6. Reuse evidence scenarios when the same documented experience supports
   multiple job requirements.
7. Distinguish direct, partial, weak, and unsupported matches conservatively.
8. If the portfolio does not support a requirement, mark it unsupported
   rather than inferring or exaggerating capability.
9. Respect documented limitations and autonomy levels.
10. Use the exact requirement IDs supplied by the JobSpec.
11. Return every field required by the output schema. Use empty lists when
    there are no list values and null for nullable fields when no value is
    supported by the portfolio.

VALIDATED JOB SPEC:

{job_spec.model_dump_json(indent=2)}

PROFESSIONAL PORTFOLIO:

{portfolio_documents}
""".strip()