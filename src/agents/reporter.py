"""Reporter agent: Markdown report + embedded charts + PDF export.

Inputs:  full GraphState
Outputs: GraphState.report_markdown, GraphState.report_pdf_path
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..render import markdown_to_pdf
from ..schemas.state import GraphState
from ..viz import render_all


_PROJECT_ROOT = Path(__file__).parent.parent.parent
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_DOCS_DIR = _PROJECT_ROOT / "docs"
_CHARTS_ROOT = _DOCS_DIR / "charts"


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

    # Also write a PDF next to the Markdown so the report ships as one file.
    pdf_path = _DOCS_DIR / f"report_{state.design.variant_id}.pdf"
    try:
        markdown_to_pdf(md_text=md, base_url=_DOCS_DIR, out_path=pdf_path)
        pdf_path_str: str | None = str(pdf_path.relative_to(_PROJECT_ROOT))
    except Exception as exc:  # PDF is a nice-to-have — never fail the graph for it
        pdf_path_str = None
        print(f"[reporter] PDF export skipped: {exc}")

    return {
        "report_markdown": md,
        "report_pdf_path": pdf_path_str,
    }
