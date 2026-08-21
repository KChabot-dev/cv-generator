import cv_generator.domain.candidate as candidate
import cv_generator.domain.evidence as evidence
import cv_generator.domain.job as job
import cv_generator.domain.planning as planning
from cv_generator.application.cv_planning import (
    plan_validate_and_store_content,
)
from cv_generator.persistence.artifact_store import ArtifactStore
from tests.factories import (
    make_candidate_profile,
    make_content_plan,
    make_evidence_map,
    make_job_spec,
)


class FakeCVPlanner:
    def __init__(self, result: planning.CVContentPlan) -> None:
        self.result = result

    def plan(
        self,
        candidate_profile: candidate.CandidateProfile,
        job_spec: job.JobSpec,
        evidence_map: evidence.EvidenceMap,
    ) -> planning.CVContentPlan:
        return self.result

def test_valid_content_plan_is_validated_and_persisted(
    artifact_store: ArtifactStore,
) -> None:
    candidate_profile = make_candidate_profile()
    job_spec = make_job_spec()
    evidence_map = make_evidence_map()
    expected_plan = make_content_plan()

    planner = FakeCVPlanner(expected_plan)

    content_plan, report = plan_validate_and_store_content(
        "RUN-001",
        candidate_profile,
        job_spec,
        evidence_map,
        planner,
        artifact_store,
    )

    assert report.is_valid
    assert content_plan == expected_plan
    assert (
        artifact_store.load_content_plan("RUN-001")
        == expected_plan
    )

def test_invalid_content_plan_is_not_persisted(
    artifact_store: ArtifactStore,
) -> None:
    candidate_profile = make_candidate_profile()
    job_spec = make_job_spec()
    evidence_map = make_evidence_map()

    invalid_plan = planning.CVContentPlan(
        application_target=planning.ApplicationTarget(
            job_title="Scientific Software Engineer",
            company="Example Company",
            job_spec_reference="JOB-001",
        ),
        document_strategy=planning.DocumentStrategy(
            primary_positioning="Scientific software engineer",
        ),
        planned_items=[
            planning.PlannedContentItem(
                id="PLAN-001",
                target_section=planning.CVSection.EXPERIENCE,
                content_type=planning.ContentType.EXPERIENCE_BULLET,
                source_entity_ref="EXP-001",
                requirement_refs=["REQ-999"],
                evidence_refs=["SCEN-999"],
                purpose="Demonstrate relevant experience.",
                priority=planning.PlanningPriority.HIGH,
                inclusion_status=planning.InclusionStatus.INCLUDE,
            )
        ],
    )

    planner = FakeCVPlanner(invalid_plan)

    content_plan, report = plan_validate_and_store_content(
        "RUN-001",
        candidate_profile,
        job_spec,
        evidence_map,
        planner,
        artifact_store,
    )

    assert content_plan == invalid_plan
    assert not report.is_valid

    assert [issue.code for issue in report.issues] == [
        "planning.unknown_requirement",
        "planning.unknown_evidence_scenario",
    ]

    assert not artifact_store.paths.content_plan(
        "RUN-001"
    ).exists()