"""Analyst agent: parses the brief, fetches climate data, checks feasibility.

Inputs:  GraphState.brief
Outputs: GraphState.climate, GraphState.analyst_notes
"""

from __future__ import annotations

from ..schemas.project import ClimateData
from ..schemas.state import GraphState

CLIMATE_FIXTURES: dict[str, ClimateData] = {}  # filled by src.rag.climate_lookup


def analyst_node(state: GraphState) -> dict:
    """Resolve climate from region, sanity-check the brief.

    Returns a partial-state dict per LangGraph convention.
    """
    from ..rag.climate_lookup import lookup_climate

    region = state.brief.site.region
    climate = lookup_climate(region)

    from ..i18n import t

    notes_parts: list[str] = []
    if climate is None:
        return {
            "errors": [f"Не найдены климатические данные для региона '{region}'"],
            "analyst_notes": "Аналитик отказался: нет климатических данных.",
        }

    brief = state.brief
    target_yield_per_m2 = brief.target_annual_yield_t * 1000 / brief.site.plot_area_m2
    lang = state.lang
    notes_parts.append(
        t("analyst_yield_per_m2", lang, value=f"{target_yield_per_m2:.1f}")
    )
    if target_yield_per_m2 > 60:
        notes_parts.append(t("analyst_high_yield_warning", lang))

    if brief.site.plot_length_m * brief.site.plot_width_m < brief.site.plot_area_m2 * 0.9:
        notes_parts.append(t("analyst_dimensions_mismatch", lang))

    return {
        "climate": climate,
        "analyst_notes": "\n".join(notes_parts),
    }
