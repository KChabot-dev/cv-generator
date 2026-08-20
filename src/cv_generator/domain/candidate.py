from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator

from cv_generator.domain.common import PartialDate, is_definitely_before


class CandidateIdentity(BaseModel):
    full_name: str
    location: str | None = None
    email: str | None = None
    phone: str | None = None
    professional_links: list[str] = Field(default_factory=list)


class EducationStatus(StrEnum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    DISCONTINUED = "discontinued"

class EducationRecord(BaseModel):
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

class ExperienceRecord(BaseModel):
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