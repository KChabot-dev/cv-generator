from cv_generator.application.ports import CVPlanner
from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.job import JobSpec
from cv_generator.domain.planning import CVContentPlan
from cv_generator.persistence.artifact_store import ArtifactStore
from cv_generator.validation.cross_model import (
    validate_content_plan_against_candidate_profile,
    validate_content_plan_claim_eligibility,
    validate_content_plan_evidence_alignment,
    validate_content_plan_references,
)

from cv_generator.validation.result import (
    ValidationIssue,
    ValidationReport,
)


def plan_validate_and_store_content(
    run_id: str,
    candidate_profile: CandidateProfile,
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
    planner: CVPlanner,
    store: ArtifactStore,
) -> tuple[CVContentPlan, ValidationReport]:
    content_plan = planner.plan(
        candidate_profile,
        job_spec,
        evidence_map,
    )

    issues: list[ValidationIssue] = []

    issues.extend(
        validate_content_plan_against_candidate_profile(
            candidate_profile,
            content_plan,
    )
)

    issues.extend(
        validate_content_plan_references(
            job_spec,
            evidence_map,
            content_plan,
        )
    )

    issues.extend(
        validate_content_plan_evidence_alignment(
            evidence_map,
            content_plan,
        )
    )

    issues.extend(
        validate_content_plan_claim_eligibility(
            evidence_map,
            content_plan,
        )
    )

    report = ValidationReport(issues=issues)

    if report.is_valid:
        store.save_content_plan(
            run_id,
            content_plan,
        )

    return content_plan, report