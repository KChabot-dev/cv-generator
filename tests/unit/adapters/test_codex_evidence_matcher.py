import pytest

import cv_generator.domain.evidence as evidence
import cv_generator.domain.portfolio as portfolio
from cv_generator.adapters.codex_evidence_matcher import CodexEvidenceMatcher
from tests.factories import make_evidence_map, make_job_spec


def make_portfolio_context() -> portfolio.PortfolioContext:
    return portfolio.PortfolioContext(
        documents=[
            portfolio.PortfolioDocument(
                source_id="skills.md",
                content="# Scientific software development",
            )
        ]
    )


def test_codex_evidence_matcher_builds_prompt_and_requests_evidence_map(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job_spec = make_job_spec()
    portfolio_context = make_portfolio_context()
    expected_evidence_map = make_evidence_map()

    received_prompt = ""
    received_model_type: type[evidence.EvidenceMap] | None = None

    def fake_run(
        prompt: str,
        model_type: type[evidence.EvidenceMap],
    ) -> evidence.EvidenceMap:
        nonlocal received_prompt, received_model_type

        received_prompt = prompt
        received_model_type = model_type

        return expected_evidence_map

    matcher = CodexEvidenceMatcher(
        executable="codex-test"
    )

    monkeypatch.setattr(
        matcher.runner,
        "run",
        fake_run,
    )

    evidence_map = matcher.match(
        job_spec,
        portfolio_context,
    )

    assert evidence_map == expected_evidence_map
    assert received_model_type is evidence.EvidenceMap

    assert job_spec.requirements[0].id in received_prompt
    assert "skills.md" in received_prompt
    assert "# Scientific software development" in received_prompt