from enum import StrEnum
from typing import Self

from pydantic import Field, model_validator

from cv_generator.domain.common import DomainModel


class SourceType(StrEnum):
    SKILL = "skill"
    EXPERIENCE = "experience"
    PROJECT = "project"
    CODE_AUDIT = "code_audit"
    PUBLICATION = "publication"
    PRESENTATION = "presentation"
    EDUCATION = "education"
    OTHER = "other"


class AutonomyLevel(StrEnum):
    INDEPENDENT = "independent"
    COLLABORATIVE = "collaborative"
    CONTRIBUTED = "contributed"
    ASSISTED = "assisted"
    EXPLORATORY = "exploratory"
    LED = "led"


class SourceItem(DomainModel):
    source_document: str
    source_section: str | None = None
    supporting_text: str
    source_type: SourceType


class EvidenceScenario(DomainModel):
    id: str
    summary: str
    source_items: list[SourceItem] = Field(min_length=1)
    source_entity_refs: list[str] = Field(default_factory=list)
    technical_details: list[str] = Field(default_factory=list)
    context: str | None = None
    autonomy_level: AutonomyLevel | None = None
    outcome: str | None = None
    limitations: list[str] = Field(default_factory=list)
    notes: str | None = None

class ScenarioRelevance(StrEnum):
    DIRECT = "direct"
    RELATED = "related"
    CONTEXTUAL = "contextual"


class ScenarioMatch(DomainModel):
    scenario_ref: str
    relevance: ScenarioRelevance
    notes: str | None = None

class CapabilityDepth(StrEnum):
    BASIC = "basic"
    WORKING = "working"
    ADVANCED = "advanced"


class RepetitionLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CapabilityAssessment(DomainModel):
    depth: CapabilityDepth
    breadth: list[str] = Field(default_factory=list)
    repetition: RepetitionLevel
    autonomy: list[AutonomyLevel] = Field(default_factory=list)
    contexts: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel
    capability_summary: str

class MatchStrength(StrEnum):
    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"
    UNSUPPORTED = "unsupported"


class ClaimEligibility(StrEnum):
    DIRECT = "direct"
    CONSERVATIVE = "conservative"
    NONE = "none"


class RequirementMatch(DomainModel):
    match_strength: MatchStrength
    matched_elements: list[str] = Field(default_factory=list)
    missing_elements: list[str] = Field(default_factory=list)
    claim_eligibility: ClaimEligibility
    allowed_claim_scope: str | None = None
    match_notes: str | None = None

    @model_validator(mode="after")
    def validate_claim_consistency(self) -> Self:
        if self.match_strength == MatchStrength.UNSUPPORTED:
            if self.claim_eligibility != ClaimEligibility.NONE:
                raise ValueError("unsupported requirements cannot be claim-eligible")

            if self.allowed_claim_scope is not None:
                raise ValueError("unsupported requirements" \
                " cannot have an allowed claim scope")

        return self

class EvidenceAssessment(DomainModel):
    requirement_id: str
    scenario_matches: list[ScenarioMatch] = Field(default_factory=list)
    capability_assessment: CapabilityAssessment | None = None
    requirement_match: RequirementMatch
    assessment_notes: str | None = None

    @model_validator(mode="after")
    def validate_assessment_consistency(self) -> Self:
        if self.requirement_match.match_strength == MatchStrength.UNSUPPORTED:
            if self.scenario_matches:
                raise ValueError(
                    "unsupported requirements cannot reference evidence scenarios"
                )

            if self.capability_assessment is not None:
                raise ValueError(
                    "unsupported requirements cannot have a capability assessment"
                )

        return self

class EvidenceMap(DomainModel):
    scenarios: list[EvidenceScenario] = Field(default_factory=list)
    assessments: list[EvidenceAssessment] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_reference_integrity(self) -> Self:
        scenario_ids = [scenario.id for scenario in self.scenarios]
        assessment_requirement_ids = [
            assessment.requirement_id for assessment in self.assessments
        ]

        if len(scenario_ids) != len(set(scenario_ids)):
            raise ValueError("evidence scenario IDs must be unique")

        if len(assessment_requirement_ids) != len(set(assessment_requirement_ids)):
            raise ValueError("each requirement can have only one evidence assessment")

        known_scenario_ids = set(scenario_ids)

        for assessment in self.assessments:
            for match in assessment.scenario_matches:
                if match.scenario_ref not in known_scenario_ids:
                    raise ValueError(
                        f"unknown scenario reference: {match.scenario_ref}"
                    )

        return self