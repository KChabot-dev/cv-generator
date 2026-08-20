from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from cv_generator.domain.common import DomainModel


class ApplicationTarget(DomainModel):
    job_title: str
    company: str
    job_spec_reference: str


class DocumentStrategy(DomainModel):
    target_length: str | None = None
    primary_positioning: str
    highest_priority_requirements: list[str] = Field(default_factory=list)
    secondary_requirements: list[str] = Field(default_factory=list)
    emphasis_notes: list[str] = Field(default_factory=list)


class CVSection(StrEnum):
    SUMMARY = "summary"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    EDUCATION = "education"
    PUBLICATIONS = "publications"
    PRESENTATIONS = "presentations"
    LANGUAGES = "languages"


class PlanningPriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SectionPlan(DomainModel):
    section: CVSection
    order: int = Field(ge=1)
    purpose: str
    importance: PlanningPriority


class ContentType(StrEnum):
    SUMMARY_STATEMENT = "summary_statement"
    SKILL_ENTRY = "skill_entry"
    EXPERIENCE_ENTRY = "experience_entry"
    EXPERIENCE_BULLET = "experience_bullet"
    PROJECT_ENTRY = "project_entry"
    EDUCATION_ENTRY = "education_entry"
    PUBLICATION_ENTRY = "publication_entry"
    PRESENTATION_ENTRY = "presentation_entry"
    LANGUAGE_ENTRY = "language_entry"
    OTHER = "other"


class InclusionStatus(StrEnum):
    INCLUDE = "include"
    OPTIONAL = "optional"
    OMIT = "omit"


class PlannedContentItem(DomainModel):
    id: str
    target_section: CVSection
    content_type: ContentType
    source_entity_ref: str | None = None
    requirement_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    purpose: str
    priority: PlanningPriority
    inclusion_status: InclusionStatus
    emphasis: list[str] = Field(default_factory=list)
    allowed_claim_scope: str | None = None
    prohibited_implications: list[str] = Field(default_factory=list)
    length_guidance: str | None = None
    planning_notes: str | None = None

    @model_validator(mode="after")
    def validate_traceability(self) -> Self:
        if self.inclusion_status == InclusionStatus.INCLUDE:
            if self.requirement_refs and not self.evidence_refs:
                raise ValueError(
                    "included requirement-targeted content must reference evidence"
                )

        return self

class NotableOmission(DomainModel):
    source_entity_ref: str
    reason: str
    notes: str | None = None

class CVContentPlan(DomainModel):
    application_target: ApplicationTarget
    document_strategy: DocumentStrategy
    section_plan: list[SectionPlan] = Field(default_factory=list)
    planned_items: list[PlannedContentItem] = Field(default_factory=list)
    notable_omissions: list[NotableOmission] = Field(default_factory=list)
    planning_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_internal_consistency(self) -> Self:
        planned_item_ids = [item.id for item in self.planned_items]

        if len(planned_item_ids) != len(set(planned_item_ids)):
            raise ValueError("planned content item IDs must be unique")

        section_orders = [section.order for section in self.section_plan]

        if len(section_orders) != len(set(section_orders)):
            raise ValueError("section order values must be unique")

        sections = [section.section for section in self.section_plan]

        if len(sections) != len(set(sections)):
            raise ValueError("each CV section can appear only once")

        return self