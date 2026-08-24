import cv_generator.domain.evidence as evidence
import cv_generator.domain.job as job
import cv_generator.domain.portfolio as portfolio
from cv_generator.application.evidence_matching import (
    match_validate_and_store_evidence,
)
from cv_generator.persistence.artifact_store import ArtifactStore
from tests.factories import make_evidence_map, make_job_spec


class FakeEvidenceMatcher:
    def __init__(self, result: evidence.EvidenceMap) -> None:
        self.result = result
        self.received_job_spec: job.JobSpec | None = None
        self.received_portfolio_context: portfolio.PortfolioContext | None = None

    def match(
        self,
        job_spec: job.JobSpec,
        portfolio_context: portfolio.PortfolioContext,
    ) -> evidence.EvidenceMap:
        self.received_job_spec = job_spec
        self.received_portfolio_context = portfolio_context
        return self.result


def make_portfolio_context() -> portfolio.PortfolioContext:
    return portfolio.PortfolioContext(
        documents=[
            portfolio.PortfolioDocument(
                source_id="skills.md",
                content="# Example evidence",
            )
        ]
    )


def test_valid_evidence_is_matched_validated_and_persisted(
    artifact_store: ArtifactStore,
) -> None:
    job_spec = make_job_spec()
    portfolio_context = make_portfolio_context()
    expected_evidence_map = make_evidence_map()

    matcher = FakeEvidenceMatcher(
        expected_evidence_map
    )

    evidence_map, report = match_validate_and_store_evidence(
        "RUN-001",
        job_spec,
        portfolio_context,
        matcher,
        artifact_store,
    )

    assert matcher.received_job_spec == job_spec
    assert matcher.received_portfolio_context == portfolio_context
    assert report.is_valid
    assert evidence_map == expected_evidence_map

    assert (
        artifact_store.load_evidence_map("RUN-001")
        == expected_evidence_map
    )


def test_invalid_evidence_is_not_persisted(
    artifact_store: ArtifactStore,
) -> None:
    job_spec = make_job_spec()
    portfolio_context = make_portfolio_context()

    invalid_evidence_map = evidence.EvidenceMap(
        assessments=[
            evidence.EvidenceAssessment(
                requirement_id="REQ-999",
                requirement_match=evidence.RequirementMatch(
                    match_strength=evidence.MatchStrength.UNSUPPORTED,
                    claim_eligibility=evidence.ClaimEligibility.NONE,
                ),
            )
        ]
    )

    matcher = FakeEvidenceMatcher(
        invalid_evidence_map
    )

    evidence_map, report = match_validate_and_store_evidence(
        "RUN-001",
        job_spec,
        portfolio_context,
        matcher,
        artifact_store,
    )

    assert evidence_map == invalid_evidence_map
    assert not report.is_valid

    assert [issue.code for issue in report.issues] == [
        "evidence.unknown_requirement",
        "evidence.missing_assessment",
    ]

    assert not artifact_store.paths.evidence_map(
        "RUN-001"
    ).exists()

def test_evidence_with_unknown_portfolio_source_is_not_persisted(
    artifact_store: ArtifactStore,
) -> None:
    job_spec = make_job_spec()

    portfolio_context = portfolio.PortfolioContext(
        documents=[
            portfolio.PortfolioDocument(
                source_id="skills.md",
                content="# Example evidence",
            )
        ]
    )

    invalid_evidence_map = make_evidence_map()

    invalid_evidence_map.scenarios[0].source_items[0].source_document = (
        "invented.md"
    )

    matcher = FakeEvidenceMatcher(
        invalid_evidence_map
    )

    evidence_map, report = match_validate_and_store_evidence(
        "RUN-001",
        job_spec,
        portfolio_context,
        matcher,
        artifact_store,
    )

    assert evidence_map == invalid_evidence_map
    assert not report.is_valid

    assert [issue.code for issue in report.issues] == [
        "evidence.unknown_source_document"
    ]

    assert not artifact_store.paths.evidence_map(
        "RUN-001"
    ).exists()