from cv_generator.application.pipeline import validate_and_store_draft
from cv_generator.persistence.artifact_store import ArtifactStore
from tests.factories import make_cv_draft, make_valid_pipeline


def test_invalid_draft_saves_report_but_not_draft(
    artifact_store: ArtifactStore,
) -> None:

    pipeline = make_valid_pipeline()

    bad_draft = make_cv_draft(
        full_name="Wrong Name",
    )

    report = validate_and_store_draft(
        "RUN-001",
        pipeline.candidate_profile,
        pipeline.job_spec,
        pipeline.evidence_map,
        pipeline.content_plan,
        bad_draft,
        artifact_store,
    )

    assert not report.is_valid
    assert artifact_store.paths.validation_report("RUN-001").exists()
    assert not artifact_store.paths.cv_draft("RUN-001").exists()

def test_valid_draft_saves_report_and_draft(
    artifact_store: ArtifactStore,
) -> None:
    pipeline = make_valid_pipeline()

    report = validate_and_store_draft(
        "RUN-001",
        pipeline.candidate_profile,
        pipeline.job_spec,
        pipeline.evidence_map,
        pipeline.content_plan,
        pipeline.cv_draft,
        artifact_store,
    )

    assert report.is_valid
    assert artifact_store.paths.validation_report("RUN-001").exists()
    assert artifact_store.paths.cv_draft("RUN-001").exists()
    assert artifact_store.load_cv_draft("RUN-001") == pipeline.cv_draft

