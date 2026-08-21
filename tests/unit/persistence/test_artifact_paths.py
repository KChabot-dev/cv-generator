from pathlib import Path

from cv_generator.persistence.artifact_paths import ArtifactPaths


def test_candidate_profile_path_is_global() -> None:
    paths = ArtifactPaths(root=Path("artifacts"))

    assert paths.candidate_profile == Path(
        "artifacts/candidate_profile.json"
    )


def test_run_artifact_paths_share_run_directory() -> None:
    paths = ArtifactPaths(root=Path("artifacts"))

    assert paths.job_spec("RUN-001") == Path(
        "artifacts/runs/RUN-001/job_spec.json"
    )

    assert paths.evidence_map("RUN-001") == Path(
        "artifacts/runs/RUN-001/evidence_map.json"
    )

    assert paths.content_plan("RUN-001") == Path(
        "artifacts/runs/RUN-001/cv_content_plan.json"
    )

    assert paths.cv_draft("RUN-001") == Path(
        "artifacts/runs/RUN-001/cv_draft.json"
    )