import pytest
from pydantic import ValidationError

from cv_generator.domain.candidate import (
    CandidateIdentity,
    CandidateProfile,
    EducationRecord,
    EducationStatus,
    ExperienceRecord,
    LanguageProficiency,
    LanguageRecord,
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

def test_experience_record_allows_missing_end_date() -> None:
    ExperienceRecord(
        id="EXP-001",
        role_title="Graduate Researcher",
        organization="Université de Sherbrooke",
        start_date=PartialDate(year=2018),
    )


def test_experience_record_rejects_end_date_before_start_date() -> None:
    with pytest.raises(ValidationError):
        ExperienceRecord(
            id="EXP-001",
            role_title="Graduate Researcher",
            organization="Université de Sherbrooke",
            start_date=PartialDate(year=2020),
            end_date=PartialDate(year=2018),
        )

def test_candidate_profile_accepts_nested_records() -> None:
    profile = CandidateProfile(
        identity=CandidateIdentity(full_name="Kevin Chabot"),
        education=[
            EducationRecord(
                id="EDU-001",
                degree="B.Eng.",
                field="Electrical Engineering",
                institution="Université de Sherbrooke",
                start_date=PartialDate(year=2015),
                end_date=PartialDate(year=2018),
                status=EducationStatus.COMPLETED,
            )
        ],
        experiences=[
            ExperienceRecord(
                id="EXP-001",
                role_title="Graduate Researcher",
                organization="Université de Sherbrooke",
                start_date=PartialDate(year=2018),
            )
        ],
        languages=[
            LanguageRecord(
                language="French",
                proficiency=LanguageProficiency.NATIVE_OR_BILINGUAL,
            )
        ],
    )

    assert len(profile.education) == 1
    assert len(profile.experiences) == 1
    assert len(profile.languages) == 1

def test_candidate_profile_rejects_duplicate_education_ids() -> None:
    with pytest.raises(ValidationError):
        CandidateProfile(
            identity=CandidateIdentity(full_name="Kevin Chabot"),
            education=[
                EducationRecord(
                    id="EDU-001",
                    degree="B.Eng.",
                    field="Electrical Engineering",
                    institution="Université de Sherbrooke",
                    start_date=PartialDate(year=2015),
                    end_date=PartialDate(year=2018),
                    status=EducationStatus.COMPLETED,
                ),
                EducationRecord(
                    id="EDU-001",
                    degree="B.Sc.",
                    field="Biology",
                    institution="Université de Sherbrooke",
                    start_date=PartialDate(year=2011),
                    end_date=PartialDate(year=2014),
                    status=EducationStatus.COMPLETED,
                ),
            ],
        )

def test_candidate_profile_rejects_duplicate_experience_ids() -> None:
    with pytest.raises(ValidationError):
        CandidateProfile(
            identity=CandidateIdentity(full_name="Kevin Chabot"),
            experiences=[
                ExperienceRecord(
                    id="EXP-001",
                    role_title="Graduate Researcher",
                    organization="Université de Sherbrooke",
                    start_date=PartialDate(year=2018),
                ),
                ExperienceRecord(
                    id="EXP-001",
                    role_title="Research Intern",
                    organization="3IT",
                    start_date=PartialDate(year=2015),
                    end_date=PartialDate(year=2015),
                ),
            ],
        )

def test_candidate_profile_json_round_trip() -> None:
    profile = CandidateProfile(
        identity=CandidateIdentity(full_name="Kevin Chabot"),
        education=[
            EducationRecord(
                id="EDU-001",
                degree="B.Eng.",
                field="Electrical Engineering",
                institution="Université de Sherbrooke",
                start_date=PartialDate(year=2015),
                end_date=PartialDate(year=2018),
                status=EducationStatus.COMPLETED,
            )
        ],
    )

    json_data = profile.model_dump_json()
    restored_profile = CandidateProfile.model_validate_json(json_data)

    assert restored_profile == profile

def test_candidate_identity_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CandidateIdentity.model_validate(
            {
                "full_name": "Kevin Chabot",
                "emali": "wrong-field@example.com",
            }
        )