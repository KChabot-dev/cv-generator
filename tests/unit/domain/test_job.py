import pytest
from pydantic import ValidationError

import cv_generator.domain.job as job


def test_job_metadata_preserves_missing_information() -> None:
    metadata = job.JobMetadata(
        title="Scientific Software Engineer",
        company="Example Company",
        work_arrangement=job.WorkArrangement.REMOTE,
        employment_type=job.EmploymentType.FULL_TIME,
    )

    assert metadata.location is None
    assert metadata.compensation is None
    assert metadata.travel is None
    assert metadata.other_constraints == []


def test_job_requirement_accepts_grounded_experience_requirement() -> None:
    requirement = job.JobRequirement(
        id="REQ-001",
        category=job.RequirementCategory.TECHNICAL_SKILL,
        description="Professional Python development experience",
        priority=job.RequirementPriority.REQUIRED,
        expected_level=job.ExpectedLevel.WORKING_KNOWLEDGE,
        experience_requirement=job.ExperienceRequirement(
            minimum_years=3,
            context=job.ExperienceContext.PROFESSIONAL,
            qualitative_expectation="professional Python development",
        ),
        explicitness=job.RequirementExplicitness.EXPLICIT,
        source_text="3+ years of professional Python development experience",
    )

    assert requirement.experience_requirement is not None
    assert requirement.experience_requirement.minimum_years == 3

def test_experience_requirement_rejects_empty_requirement() -> None:
    with pytest.raises(ValidationError):
        job.ExperienceRequirement()

def test_job_spec_accepts_nested_requirements() -> None:
    spec = job.JobSpec(
        metadata=job.JobMetadata(
            title="Scientific Software Engineer",
            company="Example Company",
        ),
        requirements=[
            job.JobRequirement(
                id="REQ-001",
                category=job.RequirementCategory.TECHNICAL_SKILL,
                description="Professional Python development experience",
                priority=job.RequirementPriority.REQUIRED,
                explicitness=job.RequirementExplicitness.EXPLICIT,
                source_text="3+ years of professional Python development experience",
            )
        ],
    )

    assert len(spec.requirements) == 1


def test_job_spec_rejects_duplicate_requirement_ids() -> None:
    with pytest.raises(ValidationError):
        job.JobSpec(
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
                ),
                job.JobRequirement(
                    id="REQ-001",
                    category=job.RequirementCategory.SOFTWARE_PRACTICE,
                    description="Automated testing",
                    priority=job.RequirementPriority.PREFERRED,
                    explicitness=job.RequirementExplicitness.EXPLICIT,
                    source_text="Experience with automated testing preferred.",
                ),
            ],
        )

def test_job_spec_json_round_trip() -> None:
    spec = job.JobSpec(
        metadata=job.JobMetadata(
            title="Scientific Software Engineer",
            company="Example Company",
            work_arrangement=job.WorkArrangement.REMOTE,
            employment_type=job.EmploymentType.FULL_TIME,
        ),
        requirements=[
            job.JobRequirement(
                id="REQ-001",
                category=job.RequirementCategory.TECHNICAL_SKILL,
                description="Professional Python development experience",
                priority=job.RequirementPriority.REQUIRED,
                expected_level=job.ExpectedLevel.WORKING_KNOWLEDGE,
                experience_requirement=job.ExperienceRequirement(
                    minimum_years=3,
                    context=job.ExperienceContext.PROFESSIONAL,
                    qualitative_expectation="professional Python development",
                ),
                explicitness=job.RequirementExplicitness.EXPLICIT,
                source_text="3+ years of professional Python development experience",
            )
        ],
    )

    json_data = spec.model_dump_json()
    restored_spec = job.JobSpec.model_validate_json(json_data)

    assert restored_spec == spec