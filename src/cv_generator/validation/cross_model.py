from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.draft import CVDraft
from cv_generator.domain.evidence import (
    ClaimEligibility,
    EvidenceMap,
)
from cv_generator.domain.job import JobSpec
from cv_generator.domain.planning import (
    CVContentPlan,
    InclusionStatus,
)
from cv_generator.validation.result import (
    ValidationIssue,
    ValidationReport,
    ValidationStage,
)


def validate_evidence_map_against_job_spec(
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    job_requirement_ids = {
        requirement.id for requirement in job_spec.requirements
    }

    assessed_requirement_ids = {
        assessment.requirement_id for assessment in evidence_map.assessments
    }

    unknown_requirement_ids = (
        assessed_requirement_ids - job_requirement_ids
    )

    missing_requirement_ids = (
        job_requirement_ids - assessed_requirement_ids
    )

    for requirement_id in sorted(unknown_requirement_ids):
        issues.append(
            ValidationIssue(
                code="evidence.unknown_requirement",
                message=(
                    f"EvidenceMap references unknown requirement: "
                    f"{requirement_id}"
                ),
                stage=ValidationStage.EVIDENCE,
                references=[requirement_id],
            )
        )

    for requirement_id in sorted(missing_requirement_ids):
        issues.append(
            ValidationIssue(
                code="evidence.missing_assessment",
                message=(
                    f"Job requirement has no evidence assessment: "
                    f"{requirement_id}"
                ),
                stage=ValidationStage.EVIDENCE,
                references=[requirement_id],
            )
        )

    return issues


def validate_content_plan_references(
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    known_requirement_ids = {
        requirement.id for requirement in job_spec.requirements
    }

    known_scenario_ids = {
        scenario.id for scenario in evidence_map.scenarios
    }

    for item in content_plan.planned_items:
        for requirement_ref in item.requirement_refs:
            if requirement_ref not in known_requirement_ids:
                issues.append(
                    ValidationIssue(
                        code="planning.unknown_requirement",
                        message=(
                            f"{item.id} references unknown requirement: "
                            f"{requirement_ref}"
                        ),
                        stage=ValidationStage.PLANNING,
                        references=[item.id, requirement_ref],
                    )

                )

            for evidence_ref in item.evidence_refs:
                if evidence_ref not in known_scenario_ids:
                    issues.append(
                        ValidationIssue(
                            code="planning.unknown_evidence_scenario",
                            message=(
                                f"{item.id} references unknown evidence scenario: "
                                f"{evidence_ref}"
                            ),
                            stage=ValidationStage.PLANNING,
                            references=[item.id, evidence_ref],
                        )
                    )

    return issues

def validate_content_plan_evidence_alignment(
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    assessments_by_requirement = {
        assessment.requirement_id: assessment
        for assessment in evidence_map.assessments
    }

    for item in content_plan.planned_items:
        item_evidence_refs = set(item.evidence_refs)

        for requirement_ref in item.requirement_refs:
            assessment = assessments_by_requirement.get(requirement_ref)

            if assessment is None:
                continue

            approved_scenario_refs = {
                match.scenario_ref
                for match in assessment.scenario_matches
            }

            if not item_evidence_refs.intersection(approved_scenario_refs):
                issues.append(
                    ValidationIssue(
                        code="planning.evidence_not_aligned",
                        message=(
                            f"{item.id} has no approved evidence for requirement: "
                            f"{requirement_ref}"
                        ),
                        stage=ValidationStage.PLANNING,
                        references=[item.id, requirement_ref],
                    )
                )

    return issues

def validate_content_plan_claim_eligibility(
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    assessments_by_requirement = {
        assessment.requirement_id: assessment
        for assessment in evidence_map.assessments
    }

    for item in content_plan.planned_items:
        if item.inclusion_status == InclusionStatus.OMIT:
            continue

        for requirement_ref in item.requirement_refs:
            assessment = assessments_by_requirement.get(requirement_ref)

            if assessment is None:
                continue

            if (
                assessment.requirement_match.claim_eligibility
                == ClaimEligibility.NONE
            ):
                issues.append(
                    ValidationIssue(
                        code="planning.claim_not_eligible",
                        message=(
                            f"{item.id} targets requirement with no "
                            f"claim eligibility: {requirement_ref}"
                        ),
                        stage=ValidationStage.PLANNING,
                        references=[item.id, requirement_ref],
                    )
                )

    return issues


def validate_draft_plan_references(
    content_plan: CVContentPlan,
    cv_draft: CVDraft,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    planned_items_by_id = {
        item.id: item for item in content_plan.planned_items
    }

    for claim in cv_draft.claims:
        planned_item = planned_items_by_id.get(claim.plan_item_ref)

        if planned_item is None:
            issues.append(
                ValidationIssue(
                    code="draft.unknown_plan_item",
                    message=(
                        f"{claim.id} references unknown planned content item: "
                        f"{claim.plan_item_ref}"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[claim.id, claim.plan_item_ref],
                )
            )

    return issues

def validate_draft_plan_alignment(
    content_plan: CVContentPlan,
    cv_draft: CVDraft,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    planned_items_by_id = {
        item.id: item for item in content_plan.planned_items
    }

    for claim in cv_draft.claims:
        planned_item = planned_items_by_id.get(claim.plan_item_ref)

        if planned_item is None:
            # Already reported by validate_draft_plan_references().
            continue

        if planned_item.inclusion_status == InclusionStatus.OMIT:
            issues.append(
                ValidationIssue(
                    code="draft.omitted_plan_item",
                    message=(
                        f"{claim.id} references omitted planned content item: "
                        f"{claim.plan_item_ref}"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[claim.id, claim.plan_item_ref],
                )
            )
            continue

        approved_requirement_refs = set(planned_item.requirement_refs)
        approved_evidence_refs = set(planned_item.evidence_refs)

        for requirement_ref in claim.requirement_refs:
            if requirement_ref not in approved_requirement_refs:
                issues.append(
                    ValidationIssue(
                        code="draft.requirement_not_approved",
                        message=(
                            f"{claim.id} uses requirement not approved by "
                            f"{claim.plan_item_ref}: {requirement_ref}"
                        ),
                        stage=ValidationStage.DRAFT,
                        references=[
                            claim.id,
                            claim.plan_item_ref,
                            requirement_ref,
                        ],
                    )
                )

        for evidence_ref in claim.evidence_refs:
            if evidence_ref not in approved_evidence_refs:
                issues.append(
                    ValidationIssue(
                        code="draft.evidence_not_approved",
                        message=(
                            f"{claim.id} uses evidence not approved by "
                            f"{claim.plan_item_ref}: {evidence_ref}"
                        ),
                        stage=ValidationStage.DRAFT,
                        references=[
                            claim.id,
                            claim.plan_item_ref,
                            evidence_ref,
                        ],
                    )
                )

    return issues

def validate_draft_against_candidate_profile(
    candidate_profile: CandidateProfile,
    cv_draft: CVDraft,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    # Header
    identity = candidate_profile.identity

    if cv_draft.header.full_name != identity.full_name:
        issues.append(
                        ValidationIssue(
                code="draft.header_name_mismatch",
                message="draft header full name does not match CandidateProfile",
                stage=ValidationStage.DRAFT,
            )
        )

    optional_header_fields = ("location", "email", "phone")

    for field_name in optional_header_fields:
        draft_value = getattr(cv_draft.header, field_name)
        profile_value = getattr(identity, field_name)

        if draft_value is not None and draft_value != profile_value:
            issues.append(
                ValidationIssue(
                    code="draft.header_field_mismatch",
                    message=(
                        f"draft header {field_name} "
                        "does not match CandidateProfile"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[field_name],
                )
            )

    for link in cv_draft.header.professional_links:
        if link not in identity.professional_links:
            issues.append(
                ValidationIssue(
                    code="draft.unknown_professional_link",
                    message=(
                        f"draft header contains unknown professional link: {link}"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[link],
                )
            )

    # Experiences
    experiences_by_id = {
        experience.id: experience
        for experience in candidate_profile.experiences
    }

    for draft_experience in cv_draft.experiences:
        source_experience = experiences_by_id.get(draft_experience.source_entity_ref)

        if source_experience is None:
            issues.append(
                ValidationIssue(
                    code="draft.unknown_candidate_experience",
                    message=(
                        "draft experience references unknown candidate experience: "
                        f"{draft_experience.source_entity_ref}"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_experience.source_entity_ref],
                )
            )
            continue

        if draft_experience.role_title != source_experience.role_title:
            issues.append(
                ValidationIssue(
                    code="draft.experience_role_mismatch",
                    message=(
                        f"{draft_experience.source_entity_ref} role title "
                        "does not match CandidateProfile"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_experience.source_entity_ref],
                )
            )

        if draft_experience.organization != source_experience.organization:
            issues.append(
                ValidationIssue(
                    code="draft.experience_organization_mismatch",
                    message=(
                        f"{draft_experience.source_entity_ref} organization "
                        "does not match CandidateProfile"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_experience.source_entity_ref],
                )
            )

        if (
            draft_experience.location is not None
            and draft_experience.location != source_experience.location
        ):
            issues.append(
                ValidationIssue(
                    code="draft.experience_location_mismatch",
                    message=(
                        f"{draft_experience.source_entity_ref} location "
                        "does not match CandidateProfile"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_experience.source_entity_ref],
                )
            )

    # Education
    education_by_id = {
        record.id: record
        for record in candidate_profile.education
    }

    for draft_education in cv_draft.education:
        source_education = education_by_id.get(draft_education.source_entity_ref)

        if source_education is None:
            issues.append(
                ValidationIssue(
                    code="draft.unknown_candidate_education",
                    message=(
                        "draft education references unknown candidate education: "
                        f"{draft_education.source_entity_ref}"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_education.source_entity_ref],
                )
            )
            continue

        if draft_education.degree != source_education.degree:
            issues.append(
                ValidationIssue(
                    code="draft.education_degree_mismatch",
                    message=(
                        f"{draft_education.source_entity_ref} degree "
                        "does not match CandidateProfile"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_education.source_entity_ref],
                )
            )

        if draft_education.field != source_education.field:
            issues.append(
                ValidationIssue(
                    code="draft.education_field_mismatch",
                    message=(
                        f"{draft_education.source_entity_ref} field "
                        "does not match CandidateProfile"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_education.source_entity_ref],
                )
            )

        if draft_education.institution != source_education.institution:
            issues.append(
                ValidationIssue(
                    code="draft.education_institution_mismatch",
                    message=(
                        f"{draft_education.source_entity_ref} institution "
                        "does not match CandidateProfile"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_education.source_entity_ref],
                )
            )

        if (
            draft_education.location is not None
            and draft_education.location != source_education.location
        ):
            issues.append(
                ValidationIssue(
                    code="draft.education_location_mismatch",
                    message=(
                        f"{draft_education.source_entity_ref} location "
                        "does not match CandidateProfile"
                    ),
                    stage=ValidationStage.DRAFT,
                    references=[draft_education.source_entity_ref],
                )
            )

    return issues

def validate_pipeline_contracts(
    candidate_profile: CandidateProfile,
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
    cv_draft: CVDraft,
) -> ValidationReport:
    issues: list[ValidationIssue] = []

    issues.extend(
        validate_evidence_map_against_job_spec(
            job_spec,
            evidence_map,
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

    return ValidationReport(issues=issues)