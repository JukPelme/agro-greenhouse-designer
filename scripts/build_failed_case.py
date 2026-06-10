"""Generate a deliberately impossible ТЗ and capture how the system refuses.

This is the 'system can say no' demonstration cited in the README.
"""

from __future__ import annotations

import pickle
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.graph import graph
from src.schemas.project import (
    CropType,
    GreenhouseType,
    ProjectBrief,
    SiteParameters,
    SoilType,
)
from src.schemas.state import GraphState
from src.viz import render_all

BAD_BRIEF = ProjectBrief(
    project_name="Тестовый отказ системы",
    greenhouse_type=GreenhouseType.YEAR_ROUND,
    target_crop=CropType.TOMATO,
    target_annual_yield_t=2000.0,
    site=SiteParameters(
        region="Новосибирская область",
        plot_area_m2=500.0,
        plot_length_m=25.0,
        plot_width_m=20.0,
        groundwater_depth_m=0.5,
        has_grid_power=False,
        has_water_supply=False,
        has_gas_supply=False,
        soil_type=SoilType.CLAY,
    ),
    notes="Деструктивный тест: ТЗ заведомо противоречиво.",
)


def main() -> None:
    raw = graph.invoke({"brief": BAD_BRIEF}, {"recursion_limit": 25})
    state = GraphState(**{k: v for k, v in raw.items() if k != "messages"})

    # Use a dedicated variant_id so failed-case charts don't overwrite happy-case.
    state.design.variant_id = "failed_v1"

    # Re-render the charts into a separate directory and re-build the report.
    chart_dir = ROOT / "docs" / "charts" / "failed_v1"
    chart_files = render_all(state, chart_dir)
    chart_rel = {
        name: f"charts/{state.design.variant_id}/{fname}"
        for name, fname in chart_files.items()
        if fname
    }
    env = Environment(
        loader=FileSystemLoader(str(ROOT / "src" / "templates")),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    state.report_markdown = env.get_template("report.md.j2").render(
        state=state,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        charts=chart_rel,
    )

    out_pkl = ROOT / "demo_cache" / "failed_run.pkl"
    out_pkl.parent.mkdir(exist_ok=True)
    with out_pkl.open("wb") as fh:
        pickle.dump(state, fh)

    (ROOT / "docs" / "failed_example.md").write_text(state.report_markdown, encoding="utf-8")

    # Render PDF for the failed case too.
    from src.render import markdown_to_pdf
    pdf_path = ROOT / "docs" / "report_failed_v1.pdf"
    try:
        markdown_to_pdf(md_text=state.report_markdown, base_url=ROOT / "docs", out_path=pdf_path)
        state.report_pdf_path = str(pdf_path.relative_to(ROOT))
        print(f"PDF: {pdf_path}")
    except Exception as exc:
        print(f"PDF skipped: {exc}")

    n_errors = sum(1 for i in state.validation.issues if i.severity.value == "error")
    print(f"Failed-case state pickled: {out_pkl}")
    print(f"Charts: {chart_dir} ({len(chart_files)} files)")
    print(f"Iterations: {state.iteration} / max {state.max_iterations}")
    print(f"Validation: {len(state.validation.issues)} issues ({n_errors} errors)")
    for issue in state.validation.issues[:6]:
        print(f"  [{issue.severity.value}] {issue.rule_id}: {issue.message[:80]}")


if __name__ == "__main__":
    main()
