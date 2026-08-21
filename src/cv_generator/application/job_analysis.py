from cv_generator.application.ports import JobAnalyzer
from cv_generator.domain.job import JobSpec
from cv_generator.persistence.artifact_store import ArtifactStore


def analyze_and_store_job(
    run_id: str,
    job_text: str,
    analyzer: JobAnalyzer,
    store: ArtifactStore,
) -> JobSpec:
    job_spec = analyzer.analyze(job_text)

    store.save_job_spec(
        run_id,
        job_spec,
    )

    return job_spec