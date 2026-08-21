from pathlib import Path

import pytest

from cv_generator.persistence.artifact_paths import ArtifactPaths
from cv_generator.persistence.artifact_store import ArtifactStore


@pytest.fixture
def artifact_store(tmp_path: Path) -> ArtifactStore:
    return ArtifactStore(
        paths=ArtifactPaths(root=tmp_path)
    )