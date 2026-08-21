from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.draft import CVDraft
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.job import JobSpec
from cv_generator.domain.planning import CVContentPlan
from cv_generator.persistence.artifact_store import ArtifactStore
from cv_generator.validation.cross_model import validate_pipeline_contracts
from cv_generator.validation.result import ValidationReport


def validate_and_store_draft(
    run_id: str,
    candidate_profile: CandidateProfile,
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
    cv_draft: CVDraft,
    store: ArtifactStore,
) -> ValidationReport:
    report = validate_pipeline_contracts(
        candidate_profile,
        job_spec,
        evidence_map,
        content_plan,
        cv_draft,
    )

    store.save_validation_report(run_id, report)

    if report.is_valid:
        store.save_cv_draft(run_id, cv_draft)

    return report