import pytest

import cv_generator.domain.planning as planning
from cv_generator.adapters.codex_cv_planner import CodexCVPlanner
from tests.factories import make_valid_pipeline


def test_codex_cv_planner_builds_prompt_and_requests_content_plan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = make_valid_pipeline()

    received_prompt = ""
    received_model_type: type[planning.CVContentPlan] | None = None

    def fake_run(
        prompt: str,
        model_type: type[planning.CVContentPlan],
    ) -> planning.CVContentPlan:
        nonlocal received_prompt, received_model_type

        received_prompt = prompt
        received_model_type = model_type

        return pipeline.content_plan

    planner = CodexCVPlanner(
        executable="codex-test"
    )

    monkeypatch.setattr(
        planner.runner,
        "run",
        fake_run,
    )

    content_plan = planner.plan(
        pipeline.candidate_profile,
        pipeline.job_spec,
        pipeline.evidence_map,
    )

    assert content_plan == pipeline.content_plan
    assert received_model_type is planning.CVContentPlan

    assert pipeline.candidate_profile.identity.full_name in received_prompt
    assert pipeline.job_spec.requirements[0].id in received_prompt
    assert pipeline.evidence_map.scenarios[0].id in received_prompt