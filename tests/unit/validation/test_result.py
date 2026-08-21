import cv_generator.validation.result as result


def test_report_is_valid_when_it_has_no_errors() -> None:
    report = result.ValidationReport(
        issues=[
            result.ValidationIssue(
                code="planning.suspicious_emphasis",
                message="Potentially excessive emphasis.",
                stage=result.ValidationStage.PLANNING,
                severity=result.ValidationSeverity.WARNING,
            )
        ]
    )

    assert report.is_valid


def test_report_is_invalid_when_it_contains_error() -> None:
    report = result.ValidationReport(
        issues=[
            result.ValidationIssue(
                code="planning.unknown_requirement",
                message="Unknown requirement.",
                stage=result.ValidationStage.PLANNING,
            )
        ]
    )

    assert not report.is_valid