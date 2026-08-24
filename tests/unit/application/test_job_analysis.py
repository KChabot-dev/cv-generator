import cv_generator.domain.job as job
from cv_generator.application.job_analysis import analyze_and_store_job
from cv_generator.persistence.artifact_store import ArtifactStore
from tests.factories import make_job_spec


class FakeJobAnalyzer:
    def __init__(self, result: job.JobSpec) -> None:
        self.result = result
        self.received_text: str | None = None

    def analyze(self, job_text: str) -> job.JobSpec:
        self.received_text = job_text
        return self.result

def test_job_analysis_uses_analyzer_and_persists_result(
    artifact_store: ArtifactStore,
) -> None:
    expected_job_spec = make_job_spec()
    analyzer = FakeJobAnalyzer(expected_job_spec)

    job_text = "Scientific Software Engineer job posting"

    result = analyze_and_store_job(
        "RUN-001",
        job_text,
        analyzer,
        artifact_store,
    )

    assert analyzer.received_text == job_text
    assert result == expected_job_spec
    assert artifact_store.load_job_spec("RUN-001") == expected_job_spec