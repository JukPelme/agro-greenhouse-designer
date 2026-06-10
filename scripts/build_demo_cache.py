"""One-shot script: run the graph once and pickle the resulting state.

Used to populate demo_cache/default_run.pkl so the Streamlit demo can replay
a full session without spending LLM tokens.

Requires ANTHROPIC_API_KEY in the env.
"""

from __future__ import annotations

import pickle
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

    final = graph.invoke({"brief": brief})
    out = ROOT / "demo_cache" / "default_run.pkl"
    out.parent.mkdir(exist_ok=True)
    with out.open("wb") as fh:
        pickle.dump(final, fh)
    print(f"Cached final state to {out}")


if __name__ == "__main__":
    main()
