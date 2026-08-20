import pytest
from pydantic import ValidationError

import cv_generator.domain.planning as planning


def test_section_plan_rejects_invalid_order() -> None:
    with pytest.raises(ValidationError):
        planning.SectionPlan(
            section=planning.CVSection.EXPERIENCE,
            order=0,
            purpose="Highlight the most relevant professional experience.",
            importance=planning.PlanningPriority.CRITICAL,
        )

def test_included_requirement_targeted_item_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        planning.PlannedContentItem(
            id="PLAN-001",
            target_section=planning.CVSection.EXPERIENCE,
            content_type=planning.ContentType.EXPERIENCE_BULLET,
            source_entity_ref="EXP-001",
            requirement_refs=["REQ-006"],
            purpose="Demonstrate relevant Python development experience.",
            priority=planning.PlanningPriority.HIGH,
            inclusion_status=planning.InclusionStatus.INCLUDE,
        )

def test_cv_content_plan_rejects_duplicate_planned_item_ids() -> None:
    item = planning.PlannedContentItem(
        id="PLAN-001",
        target_section=planning.CVSection.EDUCATION,
        content_type=planning.ContentType.EDUCATION_ENTRY,
        source_entity_ref="EDU-001",
        purpose="Include canonical education.",
        priority=planning.PlanningPriority.HIGH,
        inclusion_status=planning.InclusionStatus.INCLUDE,
    )

    with pytest.raises(ValidationError):
        planning.CVContentPlan(
            application_target=planning.ApplicationTarget(
                job_title="Scientific Software Engineer",
                company="Example Company",
                job_spec_reference="JOB-001",
            ),
            document_strategy=planning.DocumentStrategy(
                primary_positioning="Scientific software engineer",
            ),
            planned_items=[item, item],
        )

def test_cv_content_plan_rejects_duplicate_section_order() -> None:
    with pytest.raises(ValidationError):
        planning.CVContentPlan(
            application_target=planning.ApplicationTarget(
                job_title="Scientific Software Engineer",
                company="Example Company",
                job_spec_reference="JOB-001",
            ),
            document_strategy=planning.DocumentStrategy(
                primary_positioning="Scientific software engineer",
            ),
            section_plan=[
                planning.SectionPlan(
                    section=planning.CVSection.SKILLS,
                    order=1,
                    purpose="Show relevant technical capabilities.",
                    importance=planning.PlanningPriority.HIGH,
                ),
                planning.SectionPlan(
                    section=planning.CVSection.EXPERIENCE,
                    order=1,
                    purpose="Show relevant professional experience.",
                    importance=planning.PlanningPriority.CRITICAL,
                ),
            ],
        )

def test_cv_content_plan_rejects_duplicate_sections() -> None:
    with pytest.raises(ValidationError):
        planning.CVContentPlan(
            application_target=planning.ApplicationTarget(
                job_title="Scientific Software Engineer",
                company="Example Company",
                job_spec_reference="JOB-001",
            ),
            document_strategy=planning.DocumentStrategy(
                primary_positioning="Scientific software engineer",
            ),
            section_plan=[
                planning.SectionPlan(
                    section=planning.CVSection.EXPERIENCE,
                    order=1,
                    purpose="Primary relevant experience.",
                    importance=planning.PlanningPriority.CRITICAL,
                ),
                planning.SectionPlan(
                    section=planning.CVSection.EXPERIENCE,
                    order=2,
                    purpose="More experience.",
                    importance=planning.PlanningPriority.HIGH,
                ),
            ],
        )

def test_cv_content_plan_json_round_trip() -> None:
    plan = planning.CVContentPlan(
        application_target=planning.ApplicationTarget(
            job_title="Scientific Software Engineer",
            company="Example Company",
            job_spec_reference="JOB-001",
        ),
        document_strategy=planning.DocumentStrategy(
            target_length="2 pages",
            primary_positioning="Scientific software engineer",
            highest_priority_requirements=["REQ-001"],
        ),
        section_plan=[
            planning.SectionPlan(
                section=planning.CVSection.EXPERIENCE,
                order=1,
                purpose="Present the most relevant experience.",
                importance=planning.PlanningPriority.CRITICAL,
            )
        ],
    )

    json_data = plan.model_dump_json()
    restored_plan = planning.CVContentPlan.model_validate_json(json_data)

    assert restored_plan == plan