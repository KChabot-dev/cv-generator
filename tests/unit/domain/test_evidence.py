import pytest
from pydantic import ValidationError

import cv_generator.domain.evidence as evidence


def test_evidence_scenario_accepts_grounded_scenario() -> None:
    scenario = evidence.EvidenceScenario(
        id="SCEN-001",
        summary="Implemented scientific image-processing workflows in Python.",
        source_items=[
            evidence.SourceItem(
                source_document="Scientific-Image-Processing.md",
                source_section="ROI processing",
                supporting_text="Implemented ROI-based image-processing workflows.",
                source_type=evidence.SourceType.SKILL,
            )
        ],
        technical_details=[
            "Python",
            "OpenCV",
            "ROI processing",
        ],
        autonomy_level=evidence.AutonomyLevel.INDEPENDENT,
    )

    assert len(scenario.source_items) == 1


def test_evidence_scenario_requires_source_evidence() -> None:
    with pytest.raises(ValidationError):
        evidence.EvidenceScenario(
            id="SCEN-001",
            summary="Implemented scientific image-processing workflows.",
            source_items=[],
        )

def test_scenario_match_preserves_relevance() -> None:
    match = evidence.ScenarioMatch(
        scenario_ref="SCEN-001",
        relevance=evidence.ScenarioRelevance.DIRECT,
    )

    assert match.relevance == evidence.ScenarioRelevance.DIRECT

def test_capability_assessment_keeps_depth_and_confidence_separate() -> None:
    assessment = evidence.CapabilityAssessment(
        depth=evidence.CapabilityDepth.BASIC,
        breadth=[
            "image I/O",
            "ROI processing",
            "mask operations",
        ],
        repetition=evidence.RepetitionLevel.HIGH,
        autonomy=[evidence.AutonomyLevel.INDEPENDENT],
        contexts=["scientific research"],
        confidence=evidence.ConfidenceLevel.VERY_HIGH,
        capability_summary=(
            "Independent practical image-processing experience "
            "across multiple scientific workflows."
        ),
    )

    assert assessment.depth == evidence.CapabilityDepth.BASIC
    assert assessment.confidence == evidence.ConfidenceLevel.VERY_HIGH

def test_partial_match_preserves_missing_elements_and_claim_scope() -> None:
    match = evidence.RequirementMatch(
        match_strength=evidence.MatchStrength.PARTIAL,
        matched_elements=[
            "OpenCV",
            "image processing",
            "masks",
            "contours",
        ],
        missing_elements=[
            "object detection",
            "tracking",
            "real-time computer vision",
        ],
        claim_eligibility=evidence.ClaimEligibility.CONSERVATIVE,
        allowed_claim_scope=(
            "Practical OpenCV experience in scientific image processing"
        ),
    )

    assert "object detection" in match.missing_elements
    assert match.claim_eligibility == evidence.ClaimEligibility.CONSERVATIVE

def test_unsupported_assessment_contains_no_evidence_or_claim() -> None:
    assessment = evidence.EvidenceAssessment(
        requirement_id="REQ-012",
        requirement_match=evidence.RequirementMatch(
            match_strength=evidence.MatchStrength.UNSUPPORTED,
            claim_eligibility=evidence.ClaimEligibility.NONE,
        ),
    )

    assert assessment.scenario_matches == []
    assert assessment.capability_assessment is None

def test_unsupported_assessment_rejects_scenario_matches() -> None:
    with pytest.raises(ValidationError):
        evidence.EvidenceAssessment(
            requirement_id="REQ-012",
            scenario_matches=[
                evidence.ScenarioMatch(
                    scenario_ref="SCEN-001",
                    relevance=evidence.ScenarioRelevance.RELATED,
                )
            ],
            requirement_match=evidence.RequirementMatch(
                match_strength=evidence.MatchStrength.UNSUPPORTED,
                claim_eligibility=evidence.ClaimEligibility.NONE,
            ),
        )

def test_evidence_map_rejects_duplicate_scenario_ids() -> None:
    source = evidence.SourceItem(
        source_document="skills.md",
        supporting_text="Documented evidence.",
        source_type=evidence.SourceType.SKILL,
    )

    with pytest.raises(ValidationError):
        evidence.EvidenceMap(
            scenarios=[
                evidence.EvidenceScenario(
                    id="SCEN-001",
                    summary="First scenario",
                    source_items=[source],
                ),
                evidence.EvidenceScenario(
                    id="SCEN-001",
                    summary="Different scenario",
                    source_items=[source],
                ),
            ]
        )


def test_evidence_map_rejects_duplicate_requirement_assessments() -> None:
    unsupported_match = evidence.RequirementMatch(
        match_strength=evidence.MatchStrength.UNSUPPORTED,
        claim_eligibility=evidence.ClaimEligibility.NONE,
    )

    with pytest.raises(ValidationError):
        evidence.EvidenceMap(
            assessments=[
                evidence.EvidenceAssessment(
                    requirement_id="REQ-001",
                    requirement_match=unsupported_match,
                ),
                evidence.EvidenceAssessment(
                    requirement_id="REQ-001",
                    requirement_match=unsupported_match,
                ),
            ]
        )


def test_evidence_map_rejects_unknown_scenario_reference() -> None:
    with pytest.raises(ValidationError):
        evidence.EvidenceMap(
            assessments=[
                evidence.EvidenceAssessment(
                    requirement_id="REQ-001",
                    scenario_matches=[
                        evidence.ScenarioMatch(
                            scenario_ref="SCEN-999",
                            relevance=evidence.ScenarioRelevance.DIRECT,
                        )
                    ],
                    capability_assessment=evidence.CapabilityAssessment(
                        depth=evidence.CapabilityDepth.WORKING,
                        repetition=evidence.RepetitionLevel.LOW,
                        confidence=evidence.ConfidenceLevel.HIGH,
                        capability_summary="Documented Python capability.",
                    ),
                    requirement_match=evidence.RequirementMatch(
                        match_strength=evidence.MatchStrength.STRONG,
                        claim_eligibility=evidence.ClaimEligibility.DIRECT,
                        allowed_claim_scope="Python development experience",
                    ),
                )
            ]
        )

def test_evidence_map_json_round_trip() -> None:
    source = evidence.SourceItem(
        source_document="skills.md",
        supporting_text="Implemented scientific image-processing workflows.",
        source_type=evidence.SourceType.SKILL,
    )

    evidence_map = evidence.EvidenceMap(
        scenarios=[
            evidence.EvidenceScenario(
                id="SCEN-001",
                summary="Scientific image-processing experience",
                source_items=[source],
            )
        ],
        assessments=[
            evidence.EvidenceAssessment(
                requirement_id="REQ-001",
                scenario_matches=[
                    evidence.ScenarioMatch(
                        scenario_ref="SCEN-001",
                        relevance=evidence.ScenarioRelevance.DIRECT,
                    )
                ],
                capability_assessment=evidence.CapabilityAssessment(
                    depth=evidence.CapabilityDepth.WORKING,
                    repetition=evidence.RepetitionLevel.HIGH,
                    autonomy=[evidence.AutonomyLevel.INDEPENDENT],
                    contexts=["scientific research"],
                    confidence=evidence.ConfidenceLevel.HIGH,
                    capability_summary="Independent scientific image-processing work.",
                ),
                requirement_match=evidence.RequirementMatch(
                    match_strength=evidence.MatchStrength.STRONG,
                    claim_eligibility=evidence.ClaimEligibility.DIRECT,
                    allowed_claim_scope="Scientific image-processing experience",
                ),
            )
        ],
    )

    json_data = evidence_map.model_dump_json()
    restored_map = evidence.EvidenceMap.model_validate_json(json_data)

    assert restored_map == evidence_map