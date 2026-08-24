from pathlib import Path

import pytest
from pydantic import ValidationError

import cv_generator.domain.candidate as candidate
import cv_generator.domain.common as common
from cv_generator.persistence.json_store import load_json, save_json


def test_save_and_load_candidate_profile(tmp_path: Path) -> None:
    profile = candidate.CandidateProfile(
        identity=candidate.CandidateIdentity(
            full_name="Kevin Chabot",
        ),
        experiences=[
            candidate.ExperienceRecord(
                id="EXP-001",
                role_title="Graduate Researcher",
                organization="Université de Sherbrooke",
                start_date=common.PartialDate(year=2018),
            )
        ],
    )

    path = tmp_path / "candidate_profile.json"

    save_json(profile, path)

    restored_profile = load_json(
        candidate.CandidateProfile,
        path,
    )

    assert restored_profile == profile

def test_load_json_rejects_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "candidate_profile.json"

    path.write_text(
        '{"identity": {"full_name": "Kevin Chabot"',
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_json(
            candidate.CandidateProfile,
            path,
        )

def test_load_json_rejects_schema_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "candidate_profile.json"

    path.write_text(
        """
        {
          "identity": {
            "wrong_field": "Kevin Chabot"
          },
          "education": [],
          "experiences": [],
          "languages": []
        }
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_json(
            candidate.CandidateProfile,
            path,
        )

def test_save_json_creates_parent_directories(tmp_path: Path) -> None:
    profile = candidate.CandidateProfile(
        identity=candidate.CandidateIdentity(
            full_name="Kevin Chabot",
        )
    )

    path = tmp_path / "artifacts" / "candidate" / "profile.json"

    save_json(profile, path)

    assert path.exists()