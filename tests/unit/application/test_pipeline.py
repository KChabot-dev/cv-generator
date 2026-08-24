import pytest

from cv_generator.application.pipeline import validate_and_store_draft
from cv_generator.persistence.artifact_store import ArtifactStore
from tests.factories import make_cv_draft, make_valid_pipeline
from cv_generator.application.pipeline import run_pipeline
from cv_generator.domain import candidate, draft, evidence, job, planning
from cv_generator.persistence.artifact_store import ArtifactStore
from tests.factories import make_valid_pipeline


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

class FakeJobAnalyzer:
    def __init__(self, result: job.JobSpec) -> None:
        self.result = result

    def analyze(self, job_text: str) -> job.JobSpec:
        return self.result


class FakeEvidenceMatcher:
    def __init__(self, result: evidence.EvidenceMap) -> None:
        self.result = result

    def match(self, job_spec: job.JobSpec) -> evidence.EvidenceMap:
        return self.result


class FakeCVPlanner:
    def __init__(self, result: planning.CVContentPlan) -> None:
        self.result = result

    def plan(
        self,
        candidate_profile: candidate.CandidateProfile,
        job_spec: job.JobSpec,
        evidence_map: evidence.EvidenceMap,
    ) -> planning.CVContentPlan:
        return self.result


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

def test_run_pipeline_completes_valid_end_to_end_run(
    artifact_store: ArtifactStore,
) -> None:
    pipeline = make_valid_pipeline()

    cv_draft, report = run_pipeline(
        run_id="RUN-001",
        job_text="Synthetic scientific software engineer posting",
        candidate_profile=pipeline.candidate_profile,
        analyzer=FakeJobAnalyzer(pipeline.job_spec),
        matcher=FakeEvidenceMatcher(pipeline.evidence_map),
        planner=FakeCVPlanner(pipeline.content_plan),
        writer=FakeCVWriter(pipeline.cv_draft),
        store=artifact_store,
    )

    assert report.is_valid
    assert cv_draft == pipeline.cv_draft

    assert artifact_store.load_job_spec("RUN-001") == pipeline.job_spec
    assert artifact_store.load_evidence_map("RUN-001") == pipeline.evidence_map
    assert artifact_store.load_content_plan("RUN-001") == pipeline.content_plan
    assert artifact_store.load_cv_draft("RUN-001") == pipeline.cv_draft
    assert artifact_store.load_validation_report("RUN-001").is_valid

class FailIfCalledPlanner:
    def plan(
        self,
        candidate_profile: candidate.CandidateProfile,
        job_spec: job.JobSpec,
        evidence_map: evidence.EvidenceMap,
    ) -> planning.CVContentPlan:
        raise AssertionError("Planner should not have been called")


class FailIfCalledWriter:
    def write(
        self,
        candidate_profile: candidate.CandidateProfile,
        evidence_map: evidence.EvidenceMap,
        content_plan: planning.CVContentPlan,
    ) -> draft.CVDraft:
        raise AssertionError("Writer should not have been called")

def test_run_pipeline_stops_after_invalid_evidence(
    artifact_store: ArtifactStore,
) -> None:
    pipeline = make_valid_pipeline()

    invalid_job_spec = pipeline.job_spec.model_copy(
        update={
            "requirements": [
                pipeline.job_spec.requirements[0].model_copy(
                    update={"id": "REQ-999"}
                )
            ]
        }
    )

    cv_draft, report = run_pipeline(
        run_id="RUN-001",
        job_text="Synthetic scientific software engineer posting",
        candidate_profile=pipeline.candidate_profile,
        analyzer=FakeJobAnalyzer(invalid_job_spec),
        matcher=FakeEvidenceMatcher(pipeline.evidence_map),
        planner=FailIfCalledPlanner(),
        writer=FailIfCalledWriter(),
        store=artifact_store,
    )

    assert cv_draft is None
    assert not report.is_valid

    assert [issue.code for issue in report.issues] == [
        "evidence.unknown_requirement",
        "evidence.missing_assessment",
    ]

    assert artifact_store.load_job_spec("RUN-001") == invalid_job_spec
    assert artifact_store.load_validation_report("RUN-001") == report

    with pytest.raises(FileNotFoundError):
        artifact_store.load_evidence_map("RUN-001")

    with pytest.raises(FileNotFoundError):
        artifact_store.load_content_plan("RUN-001")

    with pytest.raises(FileNotFoundError):
        artifact_store.load_cv_draft("RUN-001")