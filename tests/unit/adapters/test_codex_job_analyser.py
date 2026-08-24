import pytest

import cv_generator.domain.job as job
from cv_generator.adapters.codex_job_analyzer import CodexJobAnalyzer
from tests.factories import make_job_spec


def test_codex_job_analyzer_builds_prompt_and_requests_job_spec(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_job_spec = make_job_spec()

    received_prompt = ""
    received_model_type: type[job.JobSpec] | None = None

    def fake_run(
        prompt: str,
        model_type: type[job.JobSpec],
    ) -> job.JobSpec:
        nonlocal received_prompt, received_model_type

        received_prompt = prompt
        received_model_type = model_type

        return expected_job_spec

    analyzer = CodexJobAnalyzer(
        executable="codex-test"
    )

    monkeypatch.setattr(
        analyzer.runner,
        "run",
        fake_run,
    )

    job_text = """
Scientific Software Engineer

Develop scientific Python software for data analysis.
Experience with collaborative software development is required.
""".strip()

    job_spec = analyzer.analyze(job_text)

    assert job_spec == expected_job_spec
    assert received_model_type is job.JobSpec

    assert "Scientific Software Engineer" in received_prompt
    assert "scientific Python software" in received_prompt
    assert "collaborative software development" in received_prompt