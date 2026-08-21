from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactPaths:
    root: Path

    @property
    def candidate_profile(self) -> Path:
        return self.root / "candidate_profile.json"

    def run_directory(self, run_id: str) -> Path:
        return self.root / "runs" / run_id

    def job_spec(self, run_id: str) -> Path:
        return self.run_directory(run_id) / "job_spec.json"

    def evidence_map(self, run_id: str) -> Path:
        return self.run_directory(run_id) / "evidence_map.json"

    def content_plan(self, run_id: str) -> Path:
        return self.run_directory(run_id) / "cv_content_plan.json"

    def cv_draft(self, run_id: str) -> Path:
        return self.run_directory(run_id) / "cv_draft.json"

    def validation_report(self, run_id: str) -> Path:
        return self.run_directory(run_id) / "validation_report.json"