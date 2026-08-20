from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from cv_generator.domain.common import DomainModel


class ClaimBasis(StrEnum):
    CANONICAL = "canonical"
    EVIDENCE = "evidence"
    MIXED = "mixed"

class DraftClaim(DomainModel):
    id: str
    text: str
    plan_item_ref: str
    basis: ClaimBasis

    source_entity_refs: list[str] = Field(default_factory=list)
    requirement_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        if self.basis == ClaimBasis.CANONICAL and not self.source_entity_refs:
            raise ValueError(
                "canonical claims must reference canonical candidate data"
            )

        if self.basis == ClaimBasis.EVIDENCE and not self.evidence_refs:
            raise ValueError(
                "evidence-based claims must reference supporting evidence"
            )

        if self.basis == ClaimBasis.MIXED:
            if not self.source_entity_refs or not self.evidence_refs:
                raise ValueError(
                    "mixed claims must reference both canonical data and evidence"
                )

        return self

class ApplicationReference(DomainModel):
    company: str
    job_title: str
    job_spec_ref: str
    content_plan_ref: str


class CandidateHeader(DomainModel):
    full_name: str
    location: str | None = None
    email: str | None = None
    phone: str | None = None
    professional_links: list[str] = Field(default_factory=list)

class ProfessionalSummary(DomainModel):
    text: str
    claim_refs: list[str] = Field(default_factory=list)

class DraftSection(DomainModel):
    section: str
    title: str
    order: int = Field(ge=1)
    entries: list[str] = Field(default_factory=list)

class ExperienceBullet(DomainModel):
    text: str
    claim_refs: list[str] = Field(default_factory=list)


class DraftExperience(DomainModel):
    source_entity_ref: str
    role_title: str
    organization: str
    location: str | None = None
    date_text: str
    bullets: list[ExperienceBullet] = Field(default_factory=list)

class DraftSkillGroup(DomainModel):
    label: str
    skills: list[str] = Field(min_length=1)
    claim_refs: list[str] = Field(default_factory=list)


class DraftEducation(DomainModel):
    source_entity_ref: str
    degree: str
    field: str
    institution: str
    location: str | None = None
    date_text: str
    details: list[str] = Field(default_factory=list)
    claim_refs: list[str] = Field(default_factory=list)

class DraftPublication(DomainModel):
    citation_text: str
    claim_refs: list[str] = Field(default_factory=list)


class DraftPresentation(DomainModel):
    citation_text: str
    claim_refs: list[str] = Field(default_factory=list)


class DraftLanguage(DomainModel):
    language: str
    proficiency: str | None = None

class CVDraft(DomainModel):
    application_reference: ApplicationReference
    header: CandidateHeader
    professional_summary: ProfessionalSummary | None = None

    skill_groups: list[DraftSkillGroup] = Field(default_factory=list)
    experiences: list[DraftExperience] = Field(default_factory=list)
    education: list[DraftEducation] = Field(default_factory=list)
    publications: list[DraftPublication] = Field(default_factory=list)
    presentations: list[DraftPresentation] = Field(default_factory=list)
    languages: list[DraftLanguage] = Field(default_factory=list)

    claims: list[DraftClaim] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_claim_references(self) -> Self:
        claim_ids = [claim.id for claim in self.claims]

        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("draft claim IDs must be unique")

        known_claim_ids = set(claim_ids)

        referenced_claim_ids: list[str] = []

        if self.professional_summary is not None:
            referenced_claim_ids.extend(self.professional_summary.claim_refs)

        for skill_group in self.skill_groups:
            referenced_claim_ids.extend(skill_group.claim_refs)

        for experience in self.experiences:
            for bullet in experience.bullets:
                referenced_claim_ids.extend(bullet.claim_refs)

        for education in self.education:
            referenced_claim_ids.extend(education.claim_refs)

        for publication in self.publications:
            referenced_claim_ids.extend(publication.claim_refs)

        for presentation in self.presentations:
            referenced_claim_ids.extend(presentation.claim_refs)

        for claim_ref in referenced_claim_ids:
            if claim_ref not in known_claim_ids:
                raise ValueError(f"unknown claim reference: {claim_ref}")

        return self