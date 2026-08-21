from pathlib import Path

import cv_generator.domain.candidate as candidate
import cv_generator.domain.job as job
from cv_generator.persistence.artifact_paths import ArtifactPaths
from cv_generator.persistence.artifact_store import ArtifactStore


def test_artifact_store_persists_global_and_run_artifacts(
    tmp_path: Path,
) -> None:
    store = ArtifactStore(
        paths=ArtifactPaths(root=tmp_path)
    )

    profile = candidate.CandidateProfile(
        identity=candidate.CandidateIdentity(
            full_name="Kevin Chabot",
        )
    )

    job_spec = job.JobSpec(
        metadata=job.JobMetadata(
            title="Scientific Software Engineer",
            company="Example Company",
        )
    )

    store.save_candidate_profile(profile)
    store.save_job_spec("RUN-001", job_spec)

    assert store.load_candidate_profile() == profile
    assert store.load_job_spec("RUN-001") == job_spec