"""Generate a deliberately impossible ТЗ and capture how the system refuses.

This is the 'system can say no' demonstration cited in the README.
"""

from __future__ import annotations

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
    notes="Деструктивный тест: ТЗ обязательно требует минимум ДВА отдельных блока теплиц для разделения культур.",
)


def main() -> None:
    # Two graph runs — one per language — for the failed case as well.
    from src.agents.reporter import reporter_node

    out_dir = ROOT / "demo_cache"
    out_dir.mkdir(exist_ok=True)
    docs_dir = ROOT / "docs"

    final_state = None
    for lang in ("ru", "en"):
        raw = graph.invoke({"brief": BAD_BRIEF, "lang": lang}, {"recursion_limit": 25})
        state = GraphState(**{k: v for k, v in raw.items() if k != "messages"})
        state.design.variant_id = "failed_v1"
        chart_dir = ROOT / "docs" / "charts" / "failed_v1"
        render_all(state, chart_dir)

        # Re-render with reporter_node so charts dir and language are in sync
        result = reporter_node(state)
        state.report_markdown = result["report_markdown"]
        state.report_pdf_path = result.get("report_pdf_path")

        json_out = out_dir / f"failed_run.{lang}.json"
        json_out.write_text(state.model_dump_json(indent=2, exclude={"messages"}), encoding="utf-8")
        md_out = docs_dir / f"failed_example.{lang}.md"
        md_out.write_text(state.report_markdown, encoding="utf-8")
        print(f"  {lang}: {json_out.name}, report {len(state.report_markdown)} chars")
        final_state = state

    state = final_state

    (out_dir / "failed_run.json").write_text(
        (out_dir / "failed_run.ru.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

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
    print("Failed-case: ru/en JSON saved in demo_cache/")
    print(f"Charts: {chart_dir}")
    print(f"Iterations: {state.iteration} / max {state.max_iterations}")
    print(f"Validation: {len(state.validation.issues)} issues ({n_errors} errors)")
    for issue in state.validation.issues[:6]:
        print(f"  [{issue.severity.value}] {issue.rule_id}: {issue.message[:80]}")


if __name__ == "__main__":
    main()
