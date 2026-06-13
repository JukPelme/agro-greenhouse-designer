"""One-shot script: run the graph once and pickle the resulting state.

Used to populate demo_cache/default_run.pkl so the Streamlit demo can replay
a full session without spending LLM tokens.

Requires ANTHROPIC_API_KEY (or ANTHROPIC_API_KEY_DISCORD) in the env.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.graph import graph
from src.schemas.project import (
    CropType,
    GreenhouseType,
    ProjectBrief,
    SiteParameters,
    SoilType,
)
from src.schemas.state import GraphState


def main() -> None:
    brief = ProjectBrief(
        project_name="Тепличный комплекс «Заря»",
        greenhouse_type=GreenhouseType.YEAR_ROUND,
        target_crop=CropType.TOMATO,
        target_annual_yield_t=500.0,
        site=SiteParameters(
            region="Краснодарский край",
            plot_area_m2=20_000.0,
            plot_length_m=200.0,
            plot_width_m=100.0,
            soil_type=SoilType.LOAM,
        ),
        notes="Стандартное портфолио-демо.",
    )

    raw = graph.invoke({"brief": brief}, {"recursion_limit": 25})
    state = GraphState(**{k: v for k, v in raw.items() if k != "messages"})

    # Render both languages — Reporter is deterministic (no LLM), so we just
    # re-invoke it with state.lang swapped instead of re-running the graph.
    from src.agents.reporter import reporter_node

    out_dir = ROOT / "demo_cache"
    out_dir.mkdir(exist_ok=True)
    docs_dir = ROOT / "docs"

    for lang in ("ru", "en"):
        state.lang = lang
        result = reporter_node(state)
        state.report_markdown = result["report_markdown"]
        state.report_pdf_path = result.get("report_pdf_path")

        json_out = out_dir / f"default_run.{lang}.json"
        json_out.write_text(state.model_dump_json(indent=2, exclude={"messages"}), encoding="utf-8")

        md_out = docs_dir / f"example_report.{lang}.md"
        md_out.write_text(state.report_markdown, encoding="utf-8")
        print(f"  {lang}: {json_out.name} ({json_out.stat().st_size} B), report {len(state.report_markdown)} chars")

    # Keep `default_run.json` as a back-compat alias for the Russian version.
    (out_dir / "default_run.json").write_text(
        (out_dir / "default_run.ru.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    print(f"Validation issues: {len(state.validation.issues)}, iterations: {state.iteration}")


if __name__ == "__main__":
    main()
