import cv_generator.domain.evidence as evidence
import cv_generator.domain.job as job
from cv_generator.application.evidence_matching import (
    match_validate_and_store_evidence,
)
from cv_generator.persistence.artifact_store import ArtifactStore
from tests.factories import make_evidence_map, make_job_spec

class FakeEvidenceMatcher:
    def __init__(self, result: evidence.EvidenceMap) -> None:
        self.result = result
        self.received_job_spec: job.JobSpec | None = None

    def match(
        self,
        job_spec: job.JobSpec,
    ) -> evidence.EvidenceMap:
        self.received_job_spec = job_spec
        return self.result

def test_valid_evidence_is_matched_validated_and_persisted(
    artifact_store: ArtifactStore,
) -> None:
    job_spec = make_job_spec()
    expected_evidence_map = make_evidence_map()

    matcher = FakeEvidenceMatcher(
        expected_evidence_map
    )

    evidence_map, report = match_validate_and_store_evidence(
        "RUN-001",
        job_spec,
        matcher,
        artifact_store,
    )

    assert matcher.received_job_spec == job_spec
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