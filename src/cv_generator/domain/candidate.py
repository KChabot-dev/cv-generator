from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from cv_generator.domain.common import (
    DomainModel,
    PartialDate,
    is_definitely_before,
)


class CandidateIdentity(DomainModel):
    full_name: str
    location: str | None = None
    email: str | None = None
    phone: str | None = None
    professional_links: list[str] = Field(default_factory=list)


class EducationStatus(StrEnum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    DISCONTINUED = "discontinued"

class EducationRecord(DomainModel):
    id: str
    degree: str
    field: str
    institution: str
    location: str | None = None
    start_date: PartialDate
    end_date: PartialDate | None = None
    status: EducationStatus
    
    @model_validator(mode="after")
    def validate_record_consistency(self) -> Self:
        if self.status in {
            EducationStatus.COMPLETED,
            EducationStatus.DISCONTINUED,
        } and self.end_date is None:
            raise ValueError(
                f"{self.status.value} education requires an end_date"
            )

        if self.end_date is not None and is_definitely_before(
            self.end_date, self.start_date
        ):
            raise ValueError("end_date cannot be earlier than start_date")

        return self

class ExperienceRecord(DomainModel):
    id: str
    role_title: str
    organization: str
    location: str | None = None
    start_date: PartialDate
    end_date: PartialDate | None = None

    @model_validator(mode="after")
    def validate_date_order(self) -> Self:
        if self.end_date is not None and is_definitely_before(
            self.end_date, self.start_date
        ):
            raise ValueError("end_date cannot be earlier than start_date")
        return self

class LanguageProficiency(StrEnum):
    ELEMENTARY = "elementary"
    LIMITED_WORKING = "limited_working"
    PROFESSIONAL_WORKING = "professional_working"
    FULL_PROFESSIONAL = "full_professional"
    NATIVE_OR_BILINGUAL = "native_or_bilingual"


class LanguageRecord(DomainModel):
    language: str
    proficiency: LanguageProficiency | None = None

class CandidateProfile(DomainModel):
    identity: CandidateIdentity
    education: list[EducationRecord] = Field(default_factory=list)
    experiences: list[ExperienceRecord] = Field(default_factory=list)
    languages: list[LanguageRecord] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        education_ids = [record.id for record in self.education]
        experience_ids = [record.id for record in self.experiences]

        if len(education_ids) != len(set(education_ids)):
            raise ValueError("education record IDs must be unique")

        if len(experience_ids) != len(set(experience_ids)):
            raise ValueError("experience record IDs must be unique")

        return self