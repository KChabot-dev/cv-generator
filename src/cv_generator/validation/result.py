from enum import StrEnum

from pydantic import Field

from cv_generator.domain.common import DomainModel


class ValidationSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class ValidationStage(StrEnum):
    EVIDENCE = "evidence"
    PLANNING = "planning"
    DRAFT = "draft"
    PIPELINE = "pipeline"


class ValidationIssue(DomainModel):
    code: str
    message: str
    stage: ValidationStage
    severity: ValidationSeverity = ValidationSeverity.ERROR
    references: list[str] = Field(default_factory=list)


class ValidationReport(DomainModel):
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(
            issue.severity == ValidationSeverity.ERROR
            for issue in self.issues
        )