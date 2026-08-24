from cv_generator.application.ports import EvidenceMatcher
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.job import JobSpec
from cv_generator.domain.portfolio import PortfolioContext
from cv_generator.persistence.artifact_store import ArtifactStore
from cv_generator.validation.cross_model import (
    validate_evidence_map_against_job_spec,
    validate_evidence_sources_against_portfolio,
)
from cv_generator.validation.result import ValidationIssue, ValidationReport


def match_validate_and_store_evidence(
    run_id: str,
    job_spec: JobSpec,
    portfolio_context: PortfolioContext,
    matcher: EvidenceMatcher,
    store: ArtifactStore,
) -> tuple[EvidenceMap, ValidationReport]:
    evidence_map = matcher.match(
        job_spec,
        portfolio_context,
    )

    issues: list[ValidationIssue] = []

    issues.extend(
        validate_evidence_map_against_job_spec(
            job_spec,
            evidence_map,
        )
    )
    issues.extend(
        validate_evidence_sources_against_portfolio(
            portfolio_context,
            evidence_map,
        )
    )

    report = ValidationReport(issues=issues)

    if report.is_valid:
        store.save_evidence_map(
            run_id,
            evidence_map,
        )

    return evidence_map, report