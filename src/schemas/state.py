"""LangGraph shared state.

Each agent reads from and writes to fields here. Optional fields are populated
as the graph progresses; missing values signal the orchestrator that a step
hasn't run yet or was skipped due to errors.
"""

from typing import Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from .calc_results import EngineeringReport
from .design import DesignVariant
from .project import ClimateData, ProjectBrief
from .validation import ValidationReport


class GraphState(BaseModel):
    """Shared state passed between LangGraph nodes."""

    # Input
    brief: ProjectBrief

    # Resolved context (Analyst)
    climate: ClimateData | None = None
    analyst_notes: str = ""

    # Design (Designer)
    design: DesignVariant | None = None

    # Engineering (Engineer)
    engineering: EngineeringReport | None = None

    # Validation (Validator)
    validation: ValidationReport | None = None
    iteration: int = 0
    max_iterations: int = 3

    # Output (Reporter)
    report_markdown: str = ""
    report_pdf_path: str | None = None

    # Audit trail
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
