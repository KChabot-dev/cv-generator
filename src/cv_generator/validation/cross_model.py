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


def validate_evidence_map_against_job_spec(
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
) -> list[str]:
    errors: list[str] = []

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
        errors.append(
            f"EvidenceMap references unknown requirement: {requirement_id}"
        )

    for requirement_id in sorted(missing_requirement_ids):
        errors.append(
            f"Job requirement has no evidence assessment: {requirement_id}"
        )

    return errors


def validate_content_plan_references(
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
) -> list[str]:
    errors: list[str] = []

    known_requirement_ids = {
        requirement.id for requirement in job_spec.requirements
    }

    known_scenario_ids = {
        scenario.id for scenario in evidence_map.scenarios
    }

    for item in content_plan.planned_items:
        for requirement_ref in item.requirement_refs:
            if requirement_ref not in known_requirement_ids:
                errors.append(
                    f"{item.id} references unknown requirement: "
                    f"{requirement_ref}"
                )

        for evidence_ref in item.evidence_refs:
            if evidence_ref not in known_scenario_ids:
                errors.append(
                    f"{item.id} references unknown evidence scenario: "
                    f"{evidence_ref}"
                )

    return errors

def validate_content_plan_evidence_alignment(
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
) -> list[str]:
    errors: list[str] = []

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
                errors.append(
                    f"{item.id} has no approved evidence for requirement: "
                    f"{requirement_ref}"
                )

    return errors

def validate_content_plan_claim_eligibility(
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
) -> list[str]:
    errors: list[str] = []

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
                errors.append(
                    f"{item.id} targets requirement with no claim eligibility: "
                    f"{requirement_ref}"
                )

    return errors


def validate_draft_plan_references(
    content_plan: CVContentPlan,
    cv_draft: CVDraft,
) -> list[str]:
    errors: list[str] = []

    planned_items_by_id = {
        item.id: item for item in content_plan.planned_items
    }

    for claim in cv_draft.claims:
        planned_item = planned_items_by_id.get(claim.plan_item_ref)

        if planned_item is None:
            errors.append(
                f"{claim.id} references unknown planned content item: "
                f"{claim.plan_item_ref}"
            )

    return errors

def validate_draft_plan_alignment(
    content_plan: CVContentPlan,
    cv_draft: CVDraft,
) -> list[str]:
    errors: list[str] = []

    planned_items_by_id = {
        item.id: item for item in content_plan.planned_items
    }

    for claim in cv_draft.claims:
        planned_item = planned_items_by_id.get(claim.plan_item_ref)

        if planned_item is None:
            # Already reported by validate_draft_plan_references().
            continue

        if planned_item.inclusion_status == InclusionStatus.OMIT:
            errors.append(
                f"{claim.id} references omitted planned content item: "
                f"{claim.plan_item_ref}"
            )
            continue

        approved_requirement_refs = set(planned_item.requirement_refs)
        approved_evidence_refs = set(planned_item.evidence_refs)

        for requirement_ref in claim.requirement_refs:
            if requirement_ref not in approved_requirement_refs:
                errors.append(
                    f"{claim.id} uses requirement not approved by "
                    f"{claim.plan_item_ref}: {requirement_ref}"
                )

        for evidence_ref in claim.evidence_refs:
            if evidence_ref not in approved_evidence_refs:
                errors.append(
                    f"{claim.id} uses evidence not approved by "
                    f"{claim.plan_item_ref}: {evidence_ref}"
                )

    return errors

def validate_draft_against_candidate_profile(
    candidate_profile: CandidateProfile,
    cv_draft: CVDraft,
) -> list[str]:
    errors: list[str] = []

    # Header
    identity = candidate_profile.identity

    if cv_draft.header.full_name != identity.full_name:
        errors.append("draft header full name does not match CandidateProfile")

    optional_header_fields = ("location", "email", "phone")

    for field_name in optional_header_fields:
        draft_value = getattr(cv_draft.header, field_name)
        profile_value = getattr(identity, field_name)

        if draft_value is not None and draft_value != profile_value:
            errors.append(
                f"draft header {field_name} does not match CandidateProfile"
            )

    for link in cv_draft.header.professional_links:
        if link not in identity.professional_links:
            errors.append(
                f"draft header contains unknown professional link: {link}"
            )

    # Experiences
    experiences_by_id = {
        experience.id: experience
        for experience in candidate_profile.experiences
    }

    for draft_experience in cv_draft.experiences:
        source_experience = experiences_by_id.get(draft_experience.source_entity_ref)

        if source_experience is None:
            errors.append(
                "draft experience references unknown candidate experience: "
                f"{draft_experience.source_entity_ref}"
            )
            continue

        if draft_experience.role_title != source_experience.role_title:
            errors.append(
                f"{draft_experience.source_entity_ref} role title "
                "does not match CandidateProfile"
            )

        if draft_experience.organization != source_experience.organization:
            errors.append(
                f"{draft_experience.source_entity_ref} organization "
                "does not match CandidateProfile"
            )

        if (
            draft_experience.location is not None
            and draft_experience.location != source_experience.location
        ):
            errors.append(
                f"{draft_experience.source_entity_ref} location "
                "does not match CandidateProfile"
            )

    # Education
    education_by_id = {
        record.id: record
        for record in candidate_profile.education
    }

    for draft_education in cv_draft.education:
        source = education_by_id.get(draft_education.source_entity_ref)

        if source is None:
            errors.append(
                "draft education references unknown candidate education: "
                f"{draft_education.source_entity_ref}"
            )
            continue

        if draft_education.degree != source.degree:
            errors.append(
                f"{draft_education.source_entity_ref} degree "
                "does not match CandidateProfile"
            )

        if draft_education.field != source.field:
            errors.append(
                f"{draft_education.source_entity_ref} field "
                "does not match CandidateProfile"
            )

        if draft_education.institution != source.institution:
            errors.append(
                f"{draft_education.source_entity_ref} institution "
                "does not match CandidateProfile"
            )

        if (
            draft_education.location is not None
            and draft_education.location != source.location
        ):
            errors.append(
                f"{draft_education.source_entity_ref} location "
                "does not match CandidateProfile"
            )

    return errors

def validate_pipeline_contracts(
    candidate_profile: CandidateProfile,
    job_spec: JobSpec,
    evidence_map: EvidenceMap,
    content_plan: CVContentPlan,
    cv_draft: CVDraft,
) -> list[str]:
    errors: list[str] = []

    errors.extend(
        validate_evidence_map_against_job_spec(
            job_spec,
            evidence_map,
        )
    )

    errors.extend(
        validate_content_plan_references(
            job_spec,
            evidence_map,
            content_plan,
        )
    )

    errors.extend(
        validate_content_plan_evidence_alignment(
            evidence_map,
            content_plan,
        )
    )

    errors.extend(
        validate_content_plan_claim_eligibility(
            evidence_map,
            content_plan,
        )
    )

    errors.extend(
        validate_draft_plan_references(
            content_plan,
            cv_draft,
        )
    )

    errors.extend(
        validate_draft_plan_alignment(
            content_plan,
            cv_draft,
        )
    )

    errors.extend(
        validate_draft_against_candidate_profile(
            candidate_profile,
            cv_draft,
        )
    )

    return errors