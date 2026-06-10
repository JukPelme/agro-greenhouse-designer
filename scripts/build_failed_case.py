"""Generate a deliberately impossible ТЗ and capture how the system refuses.

This is the 'system can say no' demonstration cited in the README.
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
from src.schemas.state import GraphState

# Impossible request: round-year tomato in Novosibirsk on a *tiny* plot with
# absurdly high yield. Designer cannot honor the ridge-height / transmittance
# constraints AND fit on the plot AND hit the yield target simultaneously.
BAD_BRIEF = ProjectBrief(
    project_name="Тестовый отказ системы",
    greenhouse_type=GreenhouseType.YEAR_ROUND,
    target_crop=CropType.TOMATO,
    target_annual_yield_t=2000.0,           # ~2 kt/year is huge
    site=SiteParameters(
        region="Новосибирская область",
        plot_area_m2=500.0,                  # 500 м² — заведомо мало
        plot_length_m=25.0,
        plot_width_m=20.0,
        groundwater_depth_m=0.5,             # очень высокий уровень
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

    out_pkl = ROOT / "demo_cache" / "failed_run.pkl"
    out_pkl.parent.mkdir(exist_ok=True)
    with out_pkl.open("wb") as fh:
        pickle.dump(state, fh)

    (ROOT / "docs" / "failed_example.md").write_text(state.report_markdown, encoding="utf-8")

    n_errors = sum(1 for i in state.validation.issues if i.severity.value == "error")
    print(f"Failed-case state pickled: {out_pkl}")
    print(f"Iterations: {state.iteration} / max {state.max_iterations}")
    print(f"Validation: {len(state.validation.issues)} issues ({n_errors} errors)")
    for issue in state.validation.issues[:6]:
        print(f"  [{issue.severity.value}] {issue.rule_id}: {issue.message[:80]}")


if __name__ == "__main__":
    main()
