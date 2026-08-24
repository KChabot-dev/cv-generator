from cv_generator.application.cv_planning import (
    plan_validate_and_store_content,
)
from cv_generator.application.cv_writing import (
    write_validate_and_store_draft,
)
from cv_generator.application.evidence_matching import (
    match_validate_and_store_evidence,
)
from cv_generator.application.job_analysis import analyze_and_store_job
from cv_generator.application.ports import (
    CVPlanner,
    CVWriter,
    EvidenceMatcher,
    JobAnalyzer,
)
from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.draft import CVDraft
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.job import JobSpec
from cv_generator.domain.planning import CVContentPlan
from cv_generator.domain.portfolio import PortfolioContext
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

def run_pipeline(
    *,
    run_id: str,
    job_text: str,
    candidate_profile: CandidateProfile,
    portfolio_context: PortfolioContext,
    analyzer: JobAnalyzer,
    matcher: EvidenceMatcher,
    planner: CVPlanner,
    writer: CVWriter,
    store: ArtifactStore,
) -> tuple[CVDraft | None, ValidationReport]:
    job_spec = analyze_and_store_job(
        run_id,
        job_text,
        analyzer,
        store,
    )

    evidence_map, evidence_report = match_validate_and_store_evidence(
        run_id,
        job_spec,
        portfolio_context,
        matcher,
        store,
    )

    if not evidence_report.is_valid:
        store.save_validation_report(run_id, evidence_report)
        return None, evidence_report

    content_plan, planning_report = plan_validate_and_store_content(
        run_id,
        candidate_profile,
        job_spec,
        evidence_map,
        planner,
        store,
    )

    if not planning_report.is_valid:
        store.save_validation_report(run_id, planning_report)
        return None, planning_report

    cv_draft, draft_report = write_validate_and_store_draft(
        run_id,
        candidate_profile,
        evidence_map,
        content_plan,
        writer,
        store,
    )

    store.save_validation_report(run_id, draft_report)

    if not draft_report.is_valid:
        return None, draft_report

    return cv_draft, draft_report