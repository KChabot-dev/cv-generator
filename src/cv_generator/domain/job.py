from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from cv_generator.domain.common import DomainModel


class WorkArrangement(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    OTHER = "other"


class JobMetadata(DomainModel):
    title: str
    company: str
    location: str | None = None
    work_arrangement: WorkArrangement | None = None
    employment_type: EmploymentType | None = None
    compensation: str | None = None
    travel: str | None = None
    other_constraints: list[str] = Field(default_factory=list)

class RequirementCategory(StrEnum):
    TECHNICAL_SKILL = "technical_skill"
    SOFTWARE_PRACTICE = "software_practice"
    RESPONSIBILITY = "responsibility"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    COLLABORATION = "collaboration"
    LEADERSHIP = "leadership"
    LANGUAGE = "language"
    OTHER = "other"


class RequirementPriority(StrEnum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    CORE_RESPONSIBILITY = "core_responsibility"
    ADVANTAGEOUS = "advantageous"
    UNSPECIFIED = "unspecified"


class ExpectedLevel(StrEnum):
    FAMILIARITY = "familiarity"
    WORKING_KNOWLEDGE = "working_knowledge"
    STRONG_PROFICIENCY = "strong_proficiency"
    ADVANCED_EXPERTISE = "advanced_expertise"
    UNSPECIFIED = "unspecified"


class RequirementExplicitness(StrEnum):
    EXPLICIT = "explicit"
    INFERRED = "inferred"


class ExperienceContext(StrEnum):
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"
    RESEARCH = "research"
    OTHER = "other"


class ExperienceRequirement(DomainModel):
    minimum_years: float | None = Field(default=None, ge=0)
    preferred_years: float | None = Field(default=None, ge=0)
    context: ExperienceContext | None = None
    qualitative_expectation: str | None = None

    @model_validator(mode="after")
    def validate_not_empty(self) -> Self:
        if (
            self.minimum_years is None
            and self.preferred_years is None
            and self.context is None
            and self.qualitative_expectation is None
        ):
            raise ValueError("experience requirement cannot be empty")

        return self

class JobRequirement(DomainModel):
    id: str
    category: RequirementCategory
    description: str
    priority: RequirementPriority
    expected_level: ExpectedLevel = ExpectedLevel.UNSPECIFIED
    experience_requirement: ExperienceRequirement | None = None
    explicitness: RequirementExplicitness
    source_text: str
    source_location: str | None = None
    interpretation_notes: str | None = None

class JobSpec(DomainModel):
    metadata: JobMetadata
    requirements: list[JobRequirement] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_requirement_ids(self) -> Self:
        requirement_ids = [requirement.id for requirement in self.requirements]

        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("requirement IDs must be unique")

        return self