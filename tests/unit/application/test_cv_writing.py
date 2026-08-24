import pytest

from cv_generator.application.cv_writing import write_validate_and_store_draft
from cv_generator.domain import candidate, draft, evidence, planning
from cv_generator.persistence.artifact_store import ArtifactStore
from tests.factories import make_cv_draft, make_valid_pipeline


class FakeCVWriter:
    def __init__(self, result: draft.CVDraft) -> None:
        self.result = result

    def write(
        self,
        candidate_profile: candidate.CandidateProfile,
        evidence_map: evidence.EvidenceMap,
        content_plan: planning.CVContentPlan,
    ) -> draft.CVDraft:
        return self.result


def test_valid_draft_is_written_validated_and_persisted(
    artifact_store: ArtifactStore,
) -> None:
    pipeline = make_valid_pipeline()
    writer = FakeCVWriter(pipeline.cv_draft)

    cv_draft, report = write_validate_and_store_draft(
        "RUN-001",
        pipeline.candidate_profile,
        pipeline.evidence_map,
        pipeline.content_plan,
        writer,
        artifact_store,
    )

    assert report.is_valid
    assert cv_draft == pipeline.cv_draft
    assert artifact_store.load_cv_draft("RUN-001") == pipeline.cv_draft


def test_invalid_draft_is_not_persisted(
    artifact_store: ArtifactStore,
) -> None:
    pipeline = make_valid_pipeline()
    invalid_draft = make_cv_draft(full_name="Wrong Candidate")
    writer = FakeCVWriter(invalid_draft)

    _, report = write_validate_and_store_draft(
        "RUN-001",
        pipeline.candidate_profile,
        pipeline.evidence_map,
        pipeline.content_plan,
        writer,
        artifact_store,
    )

    assert not report.is_valid
    assert [issue.code for issue in report.issues] == [
        "draft.header_name_mismatch"
    ]

    with pytest.raises(FileNotFoundError):
        artifact_store.load_cv_draft("RUN-001")