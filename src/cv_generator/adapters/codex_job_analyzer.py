from cv_generator.adapters.codex_runner import CodexStructuredRunner
from cv_generator.domain.job import JobSpec


class CodexJobAnalyzer:
    def __init__(self, executable: str = "codex.cmd") -> None:
        self.runner = CodexStructuredRunner(
            executable=executable
        )

    def analyze(
        self,
        job_text: str,
    ) -> JobSpec:
        prompt = _build_prompt(job_text)

        return self.runner.run(
            prompt,
            JobSpec,
        )


def _build_prompt(job_text: str) -> str:
    return f"""
You are the Job Analysis stage of a CV generation system.

Your task is to convert the supplied job posting into a structured JobSpec
matching the provided JSON Schema.

Analyze only the job posting. Do not consider any candidate profile,
portfolio, resume, or assumed candidate capabilities.

Rules:

1. Extract the job metadata from the posting without inventing missing facts.
2. Identify the meaningful technical skills, software practices,
   responsibilities, domain knowledge, education, experience,
   collaboration, leadership, language requirements, and other
   qualifications expressed by the employer.
3. Create one requirement for each distinct meaningful requirement or
   responsibility. Avoid duplicate requirements that express the same idea.
4. Assign requirement IDs sequentially as REQ-001, REQ-002, REQ-003, and so
   on, following the order in which the requirements are most naturally
   identified from the posting.
5. Classify priority conservatively from the employer's wording:
   required, preferred, core responsibility, advantageous, or unspecified.
6. Distinguish explicit requirements from inferred requirements.
   Use inferred only when the implication is strong and useful for CV
   tailoring. Do not turn speculative assumptions into requirements.
7. For every requirement, source_text must contain the actual wording from
   the job posting that supports the requirement. Do not invent source text.
8. Use source_location when a meaningful posting section can be identified;
   otherwise use null.
9. Use interpretation_notes when clarification is useful, especially for an
   inferred requirement. Otherwise use null.
10. Determine expected_level only from evidence in the posting. If the level
    is not supported by the text, use unspecified.
11. Populate experience_requirement only when the posting provides a
    meaningful experience expectation such as years, context, or a
    qualitative experience requirement. Otherwise use null.
12. Preserve distinctions such as required versus preferred qualifications
    rather than merging them.
13. Do not infer proficiency, years of experience, work arrangement,
    compensation, travel, or other metadata that the posting does not state.
14. Return every field required by the output schema. Use empty lists when
    there are no list values and null for nullable fields when the posting
    provides no supported value.

JOB POSTING:

--- BEGIN JOB POSTING ---
{job_text}
--- END JOB POSTING ---
""".strip()