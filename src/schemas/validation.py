"""Validation result schemas."""

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    ERROR = "error"      # нарушение → блокирует выпуск отчёта
    WARNING = "warning"  # требует обсуждения
    INFO = "info"


class ValidationIssue(BaseModel):
    rule_id: str = Field(..., description="ID правила из rules.yaml, e.g. 'SP107.6.1.3'")
    severity: Severity
    message: str = Field(..., description="Что именно нарушено и почему")
    actual_value: str | float | None = None
    required_value: str | float | None = None
    sp_citation: str | None = Field(default=None, description="Дословная цитата пункта СП через RAG")


class ValidationReport(BaseModel):
    issues: list[ValidationIssue] = Field(default_factory=list)
    rules_checked: int = 0

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def passed(self) -> bool:
        return not self.has_errors
