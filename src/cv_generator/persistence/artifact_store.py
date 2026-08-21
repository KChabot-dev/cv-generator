from dataclasses import dataclass

from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.draft import CVDraft
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.job import JobSpec
from cv_generator.domain.planning import CVContentPlan
from cv_generator.persistence.artifact_paths import ArtifactPaths
from cv_generator.persistence.json_store import load_json, save_json
from cv_generator.validation.result import ValidationReport


@dataclass(frozen=True)
class ArtifactStore:
    paths: ArtifactPaths

    def save_candidate_profile(self, profile: CandidateProfile) -> None:
        save_json(profile, self.paths.candidate_profile)

    def load_candidate_profile(self) -> CandidateProfile:
        return load_json(
            CandidateProfile,
            self.paths.candidate_profile,
        )

    def save_job_spec(self, run_id: str, job_spec: JobSpec) -> None:
        save_json(
            job_spec,
            self.paths.job_spec(run_id),
        )

    def load_job_spec(self, run_id: str) -> JobSpec:
        return load_json(
            JobSpec,
            self.paths.job_spec(run_id),
        )

    def save_evidence_map(
        self,
        run_id: str,
        evidence_map: EvidenceMap,
    ) -> None:
        save_json(
            evidence_map,
            self.paths.evidence_map(run_id),
        )

    def load_evidence_map(self, run_id: str) -> EvidenceMap:
        return load_json(
            EvidenceMap,
            self.paths.evidence_map(run_id),
        )

    def save_content_plan(
        self,
        run_id: str,
        content_plan: CVContentPlan,
    ) -> None:
        save_json(
            content_plan,
            self.paths.content_plan(run_id),
        )

    def load_content_plan(self, run_id: str) -> CVContentPlan:
        return load_json(
            CVContentPlan,
            self.paths.content_plan(run_id),
        )

    def save_cv_draft(
        self,
        run_id: str,
        cv_draft: CVDraft,
    ) -> None:
        save_json(
            cv_draft,
            self.paths.cv_draft(run_id),
        )

    def load_cv_draft(self, run_id: str) -> CVDraft:
        return load_json(
            CVDraft,
            self.paths.cv_draft(run_id),
        )

    def save_validation_report(
        self,
        run_id: str,
        report: ValidationReport,
    ) -> None:
        save_json(
            report,
            self.paths.validation_report(run_id),
        )

    def load_validation_report(
        self,
        run_id: str,
    ) -> ValidationReport:
        return load_json(
            ValidationReport,
            self.paths.validation_report(run_id),
        )