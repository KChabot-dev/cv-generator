import pytest
from pydantic import ValidationError

import cv_generator.domain.draft as draft


def test_draft_claim_preserves_traceability() -> None:
    claim = draft.DraftClaim(
        id="CLAIM-001",
        text="Developed Python workflows for scientific image processing.",
        plan_item_ref="PLAN-004",
        basis=draft.ClaimBasis.EVIDENCE,
        requirement_refs=["REQ-003"],
        evidence_refs=["SCEN-002"],
    )

    assert claim.plan_item_ref == "PLAN-004"
    assert claim.evidence_refs == ["SCEN-002"]

def test_canonical_claim_does_not_require_evidence() -> None:
    claim = draft.DraftClaim(
        id="CLAIM-002",
        text="Ph.D. in Electrical Engineering",
        plan_item_ref="PLAN-009",
        basis=draft.ClaimBasis.CANONICAL,
        source_entity_refs=["EDU-001"],
    )

    assert claim.evidence_refs == []
    assert claim.source_entity_refs == ["EDU-001"]

def test_evidence_claim_requires_evidence_reference() -> None:
    with pytest.raises(ValidationError):
        draft.DraftClaim(
            id="CLAIM-003",
            text="Developed production computer-vision systems.",
            plan_item_ref="PLAN-004",
            basis=draft.ClaimBasis.EVIDENCE,
        )

def test_candidate_header_preserves_canonical_information() -> None:
    header = draft.CandidateHeader(
        full_name="Kevin Chabot",
        location="Sherbrooke, QC",
        email="kevin@example.com",
        professional_links=["https://linkedin.com/in/example"],
    )

    assert header.full_name == "Kevin Chabot"
    assert header.phone is None
    assert len(header.professional_links) == 1

def test_draft_experience_connects_bullet_to_claims() -> None:
    experience = draft.DraftExperience(
        source_entity_ref="EXP-001",
        role_title="Graduate Researcher",
        organization="Université de Sherbrooke",
        date_text="2018–2026",
        bullets=[
            draft.ExperienceBullet(
                text="Developed Python workflows for scientific image processing.",
                claim_refs=["CLAIM-001"],
            )
        ],
    )

    assert experience.source_entity_ref == "EXP-001"
    assert experience.bullets[0].claim_refs == ["CLAIM-001"]

def test_draft_skill_group_preserves_grouped_skills() -> None:
    skill_group = draft.DraftSkillGroup(
        label="Scientific Computing",
        skills=[
            "Scientific Image Processing",
            "Signal Processing",
            "Time-Series Analysis",
        ],
        claim_refs=["CLAIM-004"],
    )

    assert len(skill_group.skills) == 3
    assert skill_group.claim_refs == ["CLAIM-004"]


def test_draft_education_preserves_canonical_reference() -> None:
    education = draft.DraftEducation(
        source_entity_ref="EDU-001",
        degree="Ph.D.",
        field="Electrical Engineering",
        institution="Université de Sherbrooke",
        date_text="2018–2026",
    )

    assert education.source_entity_ref == "EDU-001"
    assert education.details == []

def test_draft_publication_preserves_claim_references() -> None:
    publication = draft.DraftPublication(
        citation_text="Chabot et al. Micropatterned SPR imaging...",
        claim_refs=["CLAIM-010"],
    )

    assert publication.claim_refs == ["CLAIM-010"]


def test_draft_presentation_allows_no_claims() -> None:
    presentation = draft.DraftPresentation(
        citation_text="Single-Cell SPR Imaging, LN2 Poster, 2024",
    )

    assert presentation.claim_refs == []


def test_draft_language_allows_optional_proficiency() -> None:
    language = draft.DraftLanguage(
        language="English",
        proficiency="Full professional proficiency",
    )

    assert language.language == "English"
    assert language.proficiency == "Full professional proficiency"

def test_cv_draft_rejects_unknown_claim_reference() -> None:
    with pytest.raises(ValidationError):
        draft.CVDraft(
            application_reference=draft.ApplicationReference(
                company="Example Company",
                job_title="Scientific Software Engineer",
                job_spec_ref="JOB-001",
                content_plan_ref="PLAN-DOC-001",
            ),
            header=draft.CandidateHeader(
                full_name="Kevin Chabot",
            ),
            experiences=[
                draft.DraftExperience(
                    source_entity_ref="EXP-001",
                    role_title="Graduate Researcher",
                    organization="Université de Sherbrooke",
                    date_text="2018–2026",
                    bullets=[
                        draft.ExperienceBullet(
                            text="Developed scientific Python workflows.",
                            claim_refs=["CLAIM-999"],
                        )
                    ],
                )
            ],
        )

def test_cv_draft_rejects_duplicate_claim_ids() -> None:
    claim = draft.DraftClaim(
        id="CLAIM-001",
        text="Developed scientific Python workflows.",
        plan_item_ref="PLAN-001",
        basis=draft.ClaimBasis.EVIDENCE,
        evidence_refs=["SCEN-001"],
    )

    with pytest.raises(ValidationError):
        draft.CVDraft(
            application_reference=draft.ApplicationReference(
                company="Example Company",
                job_title="Scientific Software Engineer",
                job_spec_ref="JOB-001",
                content_plan_ref="PLAN-DOC-001",
            ),
            header=draft.CandidateHeader(
                full_name="Kevin Chabot",
            ),
            claims=[claim, claim],
        )

def test_cv_draft_rejects_unreferenced_claim() -> None:
    claim = draft.DraftClaim(
        id="CLAIM-001",
        text="Developed scientific Python workflows.",
        plan_item_ref="PLAN-001",
        basis=draft.ClaimBasis.EVIDENCE,
        evidence_refs=["SCEN-001"],
    )

    with pytest.raises(
        ValidationError,
        match="unreferenced draft claim",
    ):
        draft.CVDraft(
            application_reference=draft.ApplicationReference(
                company="Example Company",
                job_title="Scientific Software Engineer",
                job_spec_ref="JOB-001",
                content_plan_ref="PLAN-DOC-001",
            ),
            header=draft.CandidateHeader(
                full_name="Kevin Chabot",
            ),
            claims=[claim],
        )