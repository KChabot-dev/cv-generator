from cv_generator.application.ports import CVWriter
from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.draft import CVDraft
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.planning import CVContentPlan
from cv_generator.persistence.artifact_store import ArtifactStore
from cv_generator.validation.cross_model import (
    validate_draft_against_candidate_profile,
    validate_draft_plan_alignment,
    validate_draft_plan_references,
)
from cv_generator.validation.result import ValidationIssue, ValidationReport


def write_validate_and_store_draft(
    run_id: str,
    candidate_profile: CandidateProfile,
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
    writer: CVWriter,
    store: ArtifactStore,
) -> tuple[CVDraft, ValidationReport]:
    cv_draft = writer.write(
        candidate_profile,
        evidence_map,
        content_plan,
    )

    issues: list[ValidationIssue] = []
    issues.extend(
        validate_draft_plan_references(
            content_plan,
            cv_draft,
        )
    )
    issues.extend(
        validate_draft_plan_alignment(
            content_plan,
            cv_draft,
        )
    )
    issues.extend(
        validate_draft_against_candidate_profile(
            candidate_profile,
            cv_draft,
        )
    )

    report = ValidationReport(issues=issues)

    if report.is_valid:
        store.save_cv_draft(run_id, cv_draft)

    return cv_draft, report