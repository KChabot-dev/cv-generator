import cv_generator.domain.candidate as candidate
import cv_generator.domain.common as common
import cv_generator.domain.draft as draft
import cv_generator.domain.evidence as evidence
import cv_generator.domain.job as job
import cv_generator.domain.planning as planning
from cv_generator.validation.cross_model import (
    validate_content_plan_against_candidate_profile,
    validate_content_plan_claim_eligibility,
    validate_content_plan_evidence_alignment,
    validate_content_plan_references,
    validate_draft_against_candidate_profile,
    validate_draft_plan_alignment,
    validate_draft_plan_references,
    validate_evidence_map_against_job_spec,
    validate_pipeline_contracts,
)

import cv_generator.validation.result as result
from tests.factories import (
    make_candidate_profile,
    make_content_plan,
    make_valid_pipeline,
)


def test_evidence_map_reports_missing_and_unknown_requirements() -> None:
    job_spec = job.JobSpec(
        metadata=job.JobMetadata(
            title="Scientific Software Engineer",
            company="Example Company",
        ),
        requirements=[
            job.JobRequirement(
                id="REQ-001",
                category=job.RequirementCategory.TECHNICAL_SKILL,
                description="Python",
                priority=job.RequirementPriority.REQUIRED,
                explicitness=job.RequirementExplicitness.EXPLICIT,
                source_text="Strong Python experience required.",
            ),
            job.JobRequirement(
                id="REQ-002",
                category=job.RequirementCategory.SOFTWARE_PRACTICE,
                description="Testing",
                priority=job.RequirementPriority.REQUIRED,
                explicitness=job.RequirementExplicitness.EXPLICIT,
                source_text="Experience with software testing.",
            ),
        ],
    )

    evidence_map = evidence.EvidenceMap(
        assessments=[
            evidence.EvidenceAssessment(
                requirement_id="REQ-001",
                requirement_match=evidence.RequirementMatch(
                    match_strength=evidence.MatchStrength.UNSUPPORTED,
                    claim_eligibility=evidence.ClaimEligibility.NONE,
                ),
            ),
            evidence.EvidenceAssessment(
                requirement_id="REQ-999",
                requirement_match=evidence.RequirementMatch(
                    match_strength=evidence.MatchStrength.UNSUPPORTED,
                    claim_eligibility=evidence.ClaimEligibility.NONE,
                ),
            ),
        ]
    )

    issues = validate_evidence_map_against_job_spec(
        job_spec,
        evidence_map,
    )

    assert [issue.code for issue in issues] == [
        "evidence.unknown_requirement",
        "evidence.missing_assessment",
    ]

    assert issues[0].references == ["REQ-999"]
    assert issues[1].references == ["REQ-002"]

def test_content_plan_reports_unknown_requirement_and_evidence_refs() -> None:
    job_spec = job.JobSpec(
        metadata=job.JobMetadata(
            title="Scientific Software Engineer",
            company="Example Company",
        ),
        requirements=[
            job.JobRequirement(
                id="REQ-001",
                category=job.RequirementCategory.TECHNICAL_SKILL,
                description="Python",
                priority=job.RequirementPriority.REQUIRED,
                explicitness=job.RequirementExplicitness.EXPLICIT,
                source_text="Strong Python experience required.",
            )
        ],
    )

    source = evidence.SourceItem(
        source_document="skills.md",
        supporting_text="Developed scientific Python workflows.",
        source_type=evidence.SourceType.SKILL,
    )

    evidence_map = evidence.EvidenceMap(
        scenarios=[
            evidence.EvidenceScenario(
                id="SCEN-001",
                summary="Scientific Python development",
                source_items=[source],
            )
        ]
    )

    content_plan = planning.CVContentPlan(
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
                requirement_refs=["REQ-999"],
                evidence_refs=["SCEN-999"],
                purpose="Demonstrate relevant experience.",
                priority=planning.PlanningPriority.HIGH,
                inclusion_status=planning.InclusionStatus.INCLUDE,
            )
        ],
    )

    issues = validate_content_plan_references(
        job_spec,
        evidence_map,
        content_plan,
    )

    assert [issue.code for issue in issues] == [
        "planning.unknown_requirement",
        "planning.unknown_evidence_scenario",
    ]

    assert issues[0].references == ["PLAN-001", "REQ-999"]
    assert issues[1].references == ["PLAN-001", "SCEN-999"]


def test_content_plan_requires_evidence_aligned_with_each_requirement() -> None:
    source = evidence.SourceItem(
        source_document="skills.md",
        supporting_text="Developed scientific Python workflows.",
        source_type=evidence.SourceType.SKILL,
    )

    evidence_map = evidence.EvidenceMap(
        scenarios=[
            evidence.EvidenceScenario(
                id="SCEN-001",
                summary="Python development",
                source_items=[source],
            ),
            evidence.EvidenceScenario(
                id="SCEN-002",
                summary="Unrelated scientific work",
                source_items=[source],
            ),
        ],
        assessments=[
            evidence.EvidenceAssessment(
                requirement_id="REQ-001",
                scenario_matches=[
                    evidence.ScenarioMatch(
                        scenario_ref="SCEN-001",
                        relevance=evidence.ScenarioRelevance.DIRECT,
                    )
                ],
                capability_assessment=evidence.CapabilityAssessment(
                    depth=evidence.CapabilityDepth.WORKING,
                    repetition=evidence.RepetitionLevel.HIGH,
                    confidence=evidence.ConfidenceLevel.HIGH,
                    capability_summary="Practical Python development experience.",
                ),
                requirement_match=evidence.RequirementMatch(
                    match_strength=evidence.MatchStrength.STRONG,
                    claim_eligibility=evidence.ClaimEligibility.DIRECT,
                    allowed_claim_scope="Practical Python development",
                ),
            )
        ],
    )

    content_plan = planning.CVContentPlan(
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
                requirement_refs=["REQ-001"],
                evidence_refs=["SCEN-002"],
                purpose="Demonstrate Python development experience.",
                priority=planning.PlanningPriority.HIGH,
                inclusion_status=planning.InclusionStatus.INCLUDE,
            )
        ],
    )

    issues = validate_content_plan_evidence_alignment(
        evidence_map,
        content_plan,
    )

    assert [issue.code for issue in issues] == [
        "planning.evidence_not_aligned"
    ]

    assert issues[0].references == ["PLAN-001", "REQ-001"]

def test_content_plan_rejects_claim_ineligible_requirement() -> None:
    evidence_map = evidence.EvidenceMap(
        assessments=[
            evidence.EvidenceAssessment(
                requirement_id="REQ-001",
                requirement_match=evidence.RequirementMatch(
                    match_strength=evidence.MatchStrength.UNSUPPORTED,
                    claim_eligibility=evidence.ClaimEligibility.NONE,
                ),
            )
        ]
    )

    content_plan = planning.CVContentPlan(
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
                target_section=planning.CVSection.SKILLS,
                content_type=planning.ContentType.SKILL_ENTRY,
                requirement_refs=["REQ-001"],
                purpose="Potentially address this requirement.",
                priority=planning.PlanningPriority.LOW,
                inclusion_status=planning.InclusionStatus.OPTIONAL,
            )
        ],
    )

    issues = validate_content_plan_claim_eligibility(
        evidence_map,
        content_plan,
    )

    assert [issue.code for issue in issues] == [
        "planning.claim_not_eligible"
    ]

    assert issues[0].references == ["PLAN-001", "REQ-001"]

def test_omitted_content_may_reference_claim_ineligible_requirement() -> None:
    evidence_map = evidence.EvidenceMap(
        assessments=[
            evidence.EvidenceAssessment(
                requirement_id="REQ-001",
                requirement_match=evidence.RequirementMatch(
                    match_strength=evidence.MatchStrength.UNSUPPORTED,
                    claim_eligibility=evidence.ClaimEligibility.NONE,
                ),
            )
        ]
    )

    content_plan = planning.CVContentPlan(
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
                target_section=planning.CVSection.SKILLS,
                content_type=planning.ContentType.SKILL_ENTRY,
                requirement_refs=["REQ-001"],
                purpose="Explicitly omit unsupported content.",
                priority=planning.PlanningPriority.LOW,
                inclusion_status=planning.InclusionStatus.OMIT,
            )
        ],
    )

    assert validate_content_plan_claim_eligibility(
        evidence_map,
        content_plan,
    ) == []

def test_draft_reports_unknown_plan_item_reference() -> None:
    content_plan = planning.CVContentPlan(
        application_target=planning.ApplicationTarget(
            job_title="Scientific Software Engineer",
            company="Example Company",
            job_spec_reference="JOB-001",
        ),
        document_strategy=planning.DocumentStrategy(
            primary_positioning="Scientific software engineer",
        ),
    )

    cv_draft = draft.CVDraft(
        application_reference=draft.ApplicationReference(
            company="Example Company",
            job_title="Scientific Software Engineer",
            job_spec_ref="JOB-001",
            content_plan_ref="PLAN-DOC-001",
        ),
        header=draft.CandidateHeader(
            full_name="Kevin Chabot",
        ),
        claims=[
            draft.DraftClaim(
                id="CLAIM-001",
                text="Developed scientific Python workflows.",
                plan_item_ref="PLAN-999",
                basis=draft.ClaimBasis.EVIDENCE,
                evidence_refs=["SCEN-001"],
            )
        ],
    )

    issues = validate_draft_plan_references(
        content_plan,
        cv_draft,
    )

    assert [issue.code for issue in issues] == [
        "draft.unknown_plan_item"
    ]

    assert issues[0].references == ["CLAIM-001", "PLAN-999"]

def test_draft_claim_cannot_exceed_plan_item_boundaries() -> None:
    content_plan = planning.CVContentPlan(
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
                requirement_refs=["REQ-001"],
                evidence_refs=["SCEN-001"],
                purpose="Demonstrate Python development experience.",
                priority=planning.PlanningPriority.HIGH,
                inclusion_status=planning.InclusionStatus.INCLUDE,
            )
        ],
    )

    cv_draft = draft.CVDraft(
        application_reference=draft.ApplicationReference(
            company="Example Company",
            job_title="Scientific Software Engineer",
            job_spec_ref="JOB-001",
            content_plan_ref="PLAN-DOC-001",
        ),
        header=draft.CandidateHeader(
            full_name="Kevin Chabot",
        ),
        claims=[
            draft.DraftClaim(
                id="CLAIM-001",
                text="Developed scientific Python workflows.",
                plan_item_ref="PLAN-001",
                basis=draft.ClaimBasis.EVIDENCE,
                requirement_refs=["REQ-999"],
                evidence_refs=["SCEN-999"],
            )
        ],
    )

    issues = validate_draft_plan_alignment(
        content_plan,
        cv_draft,
    )

    assert [issue.code for issue in issues] == [
        "draft.requirement_not_approved",
        "draft.evidence_not_approved",
    ]

    assert issues[0].references == [
        "CLAIM-001",
        "PLAN-001",
        "REQ-999",
    ]

    assert issues[1].references == [
        "CLAIM-001",
        "PLAN-001",
        "SCEN-999",
    ]

def test_draft_claim_cannot_use_omitted_plan_item() -> None:
    content_plan = planning.CVContentPlan(
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
                target_section=planning.CVSection.SKILLS,
                content_type=planning.ContentType.SKILL_ENTRY,
                purpose="Do not include unsupported skill.",
                priority=planning.PlanningPriority.LOW,
                inclusion_status=planning.InclusionStatus.OMIT,
            )
        ],
    )

    cv_draft = draft.CVDraft(
        application_reference=draft.ApplicationReference(
            company="Example Company",
            job_title="Scientific Software Engineer",
            job_spec_ref="JOB-001",
            content_plan_ref="PLAN-DOC-001",
        ),
        header=draft.CandidateHeader(
            full_name="Kevin Chabot",
        ),
        claims=[
            draft.DraftClaim(
                id="CLAIM-001",
                text="Claim that should never have been written.",
                plan_item_ref="PLAN-001",
                basis=draft.ClaimBasis.CANONICAL,
                source_entity_refs=["EXP-001"],
            )
        ],
    )

    issues = validate_draft_plan_alignment(
        content_plan,
        cv_draft,
    )

    assert [issue.code for issue in issues] == [
        "draft.omitted_plan_item"
    ]

    assert issues[0].references == [
        "CLAIM-001",
        "PLAN-001",
    ]

def test_draft_reports_candidate_fact_mismatch() -> None:
    candidate_profile = candidate.CandidateProfile(
        identity=candidate.CandidateIdentity(
            full_name="Kevin Chabot",
        ),
        education=[
            candidate.EducationRecord(
                id="EDU-001",
                degree="Ph.D.",
                field="Electrical Engineering",
                institution="Université de Sherbrooke",
                start_date=common.PartialDate(year=2018),
                end_date=common.PartialDate(year=2026),
                status=candidate.EducationStatus.COMPLETED,
            )
        ],
    )

    cv_draft = draft.CVDraft(
        application_reference=draft.ApplicationReference(
            company="Example Company",
            job_title="Scientific Software Engineer",
            job_spec_ref="JOB-001",
            content_plan_ref="PLAN-DOC-001",
        ),
        header=draft.CandidateHeader(
            full_name="Kevin Chabot",
        ),
        education=[
            draft.DraftEducation(
                source_entity_ref="EDU-001",
                degree="Ph.D.",
                field="Computer Science",  # deliberately wrong
                institution="Université de Sherbrooke",
                date_text="2018–2026",
            )
        ],
    )

    issues = validate_draft_against_candidate_profile(
        candidate_profile,
        cv_draft,
    )

    assert [issue.code for issue in issues] == [
        "draft.education_field_mismatch"
    ]

    assert issues[0].references == ["EDU-001"]

def test_valid_pipeline_contracts_produce_no_errors() -> None:
    pipeline = make_valid_pipeline()

    report = validate_pipeline_contracts(
        pipeline.candidate_profile,
        pipeline.job_spec,
        pipeline.evidence_map,
        pipeline.content_plan,
        pipeline.cv_draft,
    )

    assert report.is_valid
    assert report.issues == []


def test_pipeline_report_is_invalid_when_contract_fails() -> None:
    candidate_profile = candidate.CandidateProfile(
        identity=candidate.CandidateIdentity(
            full_name="Kevin Chabot",
        )
    )

    job_spec = job.JobSpec(
        metadata=job.JobMetadata(
            title="Scientific Software Engineer",
            company="Example Company",
        )
    )

    evidence_map = evidence.EvidenceMap()

    content_plan = planning.CVContentPlan(
        application_target=planning.ApplicationTarget(
            job_title="Scientific Software Engineer",
            company="Example Company",
            job_spec_reference="JOB-001",
        ),
        document_strategy=planning.DocumentStrategy(
            primary_positioning="Scientific software engineer",
        ),
    )

    cv_draft = draft.CVDraft(
        application_reference=draft.ApplicationReference(
            company="Example Company",
            job_title="Scientific Software Engineer",
            job_spec_ref="JOB-001",
            content_plan_ref="PLAN-DOC-001",
        ),
        header=draft.CandidateHeader(
            full_name="Wrong Name",
        ),
    )

    report = validate_pipeline_contracts(
        candidate_profile,
        job_spec,
        evidence_map,
        content_plan,
        cv_draft,
    )

    assert not report.is_valid

    assert [issue.code for issue in report.issues] == [
        "draft.header_name_mismatch"
    ]

def test_content_plan_rejects_unknown_candidate_experience() -> None:
    candidate_profile = make_candidate_profile()
    content_plan = make_content_plan()

    original_item = content_plan.planned_items[0]

    invalid_item = original_item.model_copy(
        update={"source_entity_ref": "EXP-999"}
    )

    invalid_plan = content_plan.model_copy(
        update={"planned_items": [invalid_item]}
    )

    issues = validate_content_plan_against_candidate_profile(
        candidate_profile,
        invalid_plan,
    )

    assert [issue.code for issue in issues] == [
        "planning.unknown_candidate_experience"
    ]

    assert issues[0].references == [
        "PLAN-001",
        "EXP-999",
    ]