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

    # LangGraph returns a dict; rebuild GraphState so the UI can use attribute
    # access (state.report_markdown, state.validation.issues, …).
    state = GraphState(**{k: v for k, v in raw.items() if k != "messages"})

    out = ROOT / "demo_cache" / "default_run.json"
    out.parent.mkdir(exist_ok=True)
    # JSON is more robust than pickle across schema migrations:
    # extra fields are tolerated, missing ones get defaults, no class refs.
    out.write_text(state.model_dump_json(indent=2, exclude={"messages"}), encoding="utf-8")

    # Also persist the rendered report next to docs/ for at-a-glance review.
    (ROOT / "docs" / "example_report.md").write_text(state.report_markdown, encoding="utf-8")

    print(f"Cached final state to {out} ({out.stat().st_size} bytes)")
    print(f"Rendered report to docs/example_report.md ({len(state.report_markdown)} chars)")
    print(f"Validation issues: {len(state.validation.issues)}, iterations: {state.iteration}")


if __name__ == "__main__":
    main()
