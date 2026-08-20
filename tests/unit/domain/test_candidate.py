import pytest
from pydantic import ValidationError

from cv_generator.domain.candidate import (
    CandidateIdentity,
    EducationRecord,
    EducationStatus,
)
from cv_generator.domain.common import PartialDate


def test_candidate_identity_with_required_name() -> None:
    identity = CandidateIdentity(full_name="Kevin Chabot")

    assert identity.full_name == "Kevin Chabot"
    assert identity.location is None
    assert identity.email is None
    assert identity.phone is None
    assert identity.professional_links == []


def test_education_record_accepts_valid_dates() -> None:
    record = EducationRecord(
        id="EDU-001",
        degree="B.Eng.",
        field="Electrical Engineering",
        institution="Université de Sherbrooke",
        start_date=PartialDate(year=2015),
        end_date=PartialDate(year=2018),
        status=EducationStatus.COMPLETED,
    )

    assert record.id == "EDU-001"


def test_education_record_rejects_end_year_before_start_year() -> None:
    with pytest.raises(ValidationError):
        EducationRecord(
            id="EDU-001",
            degree="B.Eng.",
            field="Electrical Engineering",
            institution="Université de Sherbrooke",
            start_date=PartialDate(year=2018),
            end_date=PartialDate(year=2017),
            status=EducationStatus.COMPLETED,
        )


def test_education_record_rejects_earlier_month_in_same_year() -> None:
    with pytest.raises(ValidationError):
        EducationRecord(
            id="EDU-001",
            degree="B.Eng.",
            field="Electrical Engineering",
            institution="Université de Sherbrooke",
            start_date=PartialDate(year=2018, month=9),
            end_date=PartialDate(year=2018, month=5),
            status=EducationStatus.COMPLETED,
        )

def test_completed_education_requires_end_date() -> None:
    with pytest.raises(ValidationError):
        EducationRecord(
            id="EDU-001",
            degree="B.Eng.",
            field="Electrical Engineering",
            institution="Université de Sherbrooke",
            start_date=PartialDate(year=2015),
            status=EducationStatus.COMPLETED,
        )


def test_in_progress_education_allows_missing_end_date() -> None:
    EducationRecord(
        id="EDU-002",
        degree="Ph.D.",
        field="Engineering",
        institution="Université de Sherbrooke",
        start_date=PartialDate(year=2018),
        status=EducationStatus.IN_PROGRESS,
    )