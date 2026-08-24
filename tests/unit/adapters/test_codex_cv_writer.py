import pytest

import cv_generator.domain.draft as draft
from cv_generator.adapters.codex_cv_writer import CodexCVWriter
from tests.factories import make_valid_pipeline


def test_codex_cv_writer_builds_prompt_and_requests_cv_draft(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = make_valid_pipeline()

    received_prompt = ""
    received_model_type: type[draft.CVDraft] | None = None

    def fake_run(
        prompt: str,
        model_type: type[draft.CVDraft],
    ) -> draft.CVDraft:
        nonlocal received_prompt, received_model_type

        received_prompt = prompt
        received_model_type = model_type

        return pipeline.cv_draft

    writer = CodexCVWriter(
        executable="codex-test"
    )

    monkeypatch.setattr(
        writer.runner,
        "run",
        fake_run,
    )

    cv_draft = writer.write(
        pipeline.candidate_profile,
        pipeline.evidence_map,
        pipeline.content_plan,
    )

    assert cv_draft == pipeline.cv_draft
    assert received_model_type is draft.CVDraft

    assert pipeline.candidate_profile.identity.full_name in received_prompt
    assert pipeline.evidence_map.scenarios[0].id in received_prompt
    assert pipeline.content_plan.planned_items[0].id in received_prompt