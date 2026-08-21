import cv_generator.domain.candidate as candidate
import cv_generator.domain.common as common
import cv_generator.domain.job as job
import cv_generator.domain.evidence as evidence
import cv_generator.domain.planning as planning
import cv_generator.domain.draft as draft
from dataclasses import dataclass


def make_candidate_profile(
    *,
    full_name: str = "Test Candidate",
) -> candidate.CandidateProfile:
    return candidate.CandidateProfile(
        identity=candidate.CandidateIdentity(
            full_name=full_name,
        ),
        experiences=[
            candidate.ExperienceRecord(
                id="EXP-001",
                role_title="Research Software Developer",
                organization="Example University",
                start_date=common.PartialDate(year=2020),
                end_date=common.PartialDate(year=2024),
            )
        ],
    )


def make_job_spec() -> job.JobSpec:
    return job.JobSpec(
        metadata=job.JobMetadata(
            title="Scientific Software Engineer",
            company="Example Company",
        ),
        requirements=[
            job.JobRequirement(
                id="REQ-001",
                category=job.RequirementCategory.TECHNICAL_SKILL,
                description="Python development",
                priority=job.RequirementPriority.REQUIRED,
                explicitness=job.RequirementExplicitness.EXPLICIT,
                source_text="Strong Python development experience required.",
            )
        ],
    )

def make_evidence_map() -> evidence.EvidenceMap:
    source = evidence.SourceItem(
        source_document="skills.md",
        supporting_text="Developed reusable scientific Python workflows.",
        source_type=evidence.SourceType.SKILL,
    )

    return evidence.EvidenceMap(
        scenarios=[
            evidence.EvidenceScenario(
                id="SCEN-001",
                summary="Scientific Python development",
                source_items=[source],
            )
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
                    capability_summary="Practical scientific Python development.",
                ),
                requirement_match=evidence.RequirementMatch(
                    match_strength=evidence.MatchStrength.STRONG,
                    claim_eligibility=evidence.ClaimEligibility.DIRECT,
                    allowed_claim_scope="Practical scientific Python development",
                ),
            )
        ],
    )

def make_content_plan() -> planning.CVContentPlan:
    return planning.CVContentPlan(
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
                requirement_refs=["REQ-001"],
                evidence_refs=["SCEN-001"],
                purpose="Demonstrate scientific Python development.",
                priority=planning.PlanningPriority.HIGH,
                inclusion_status=planning.InclusionStatus.INCLUDE,
                allowed_claim_scope="Practical scientific Python development",
            )
        ],
    )

def make_cv_draft(
    *,
    full_name: str = "Test Candidate",
) -> draft.CVDraft:
    return draft.CVDraft(
        application_reference=draft.ApplicationReference(
            company="Example Company",
            job_title="Scientific Software Engineer",
            job_spec_ref="JOB-001",
            content_plan_ref="PLAN-DOC-001",
        ),
        header=draft.CandidateHeader(
            full_name=full_name,
        ),
        experiences=[
            draft.DraftExperience(
                source_entity_ref="EXP-001",
                role_title="Research Software Developer",
                organization="Example University",
                date_text="2020–2024",
                bullets=[
                    draft.ExperienceBullet(
                        text=(
                            "Developed reusable scientific Python workflows."
                        ),
                        claim_refs=["CLAIM-001"],
                    )
                ],
            )
        ],
        claims=[
            draft.DraftClaim(
                id="CLAIM-001",
                text="Developed reusable scientific Python workflows.",
                plan_item_ref="PLAN-001",
                basis=draft.ClaimBasis.MIXED,
                source_entity_refs=["EXP-001"],
                requirement_refs=["REQ-001"],
                evidence_refs=["SCEN-001"],
            )
        ],
    )

@dataclass(frozen=True)
class PipelineArtifacts:
    candidate_profile: candidate.CandidateProfile
    job_spec: job.JobSpec
    evidence_map: evidence.EvidenceMap
    content_plan: planning.CVContentPlan
    cv_draft: draft.CVDraft

def make_valid_pipeline() -> PipelineArtifacts:
    return PipelineArtifacts(
        candidate_profile=make_candidate_profile(),
        job_spec=make_job_spec(),
        evidence_map=make_evidence_map(),
        content_plan=make_content_plan(),
        cv_draft=make_cv_draft(),
    )