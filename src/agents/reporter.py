"""Reporter agent: composes a Markdown report with embedded chart images.

Inputs:  full GraphState
Outputs: GraphState.report_markdown,
         charts written to <project>/docs/charts/<variant_id>/
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..schemas.state import GraphState
from ..viz import render_all


_PROJECT_ROOT = Path(__file__).parent.parent.parent
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_CHARTS_ROOT = _PROJECT_ROOT / "docs" / "charts"


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

    chart_dir = _CHARTS_ROOT / state.design.variant_id
    chart_files = render_all(state, chart_dir)
    # Markdown image paths are relative to docs/example_report.md → charts/<id>/...
    chart_rel = {
        name: f"charts/{state.design.variant_id}/{fname}"
        for name, fname in chart_files.items()
        if fname
    }

    template = _env().get_template("report.md.j2")
    md = template.render(
        state=state,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        charts=chart_rel,
    )

    return {"report_markdown": md}
