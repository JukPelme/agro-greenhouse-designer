"""Reporter agent: composes a Markdown report; PDF rendering is a downstream step.

Inputs:  full GraphState
Outputs: GraphState.report_markdown
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..schemas.state import GraphState


_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def reporter_node(state: GraphState) -> dict:
    if state.design is None or state.engineering is None:
        return {"errors": ["Reporter: нет design или engineering для отчёта."]}

    template = _env().get_template("report.md.j2")
    md = template.render(
        state=state,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    return {"report_markdown": md}
