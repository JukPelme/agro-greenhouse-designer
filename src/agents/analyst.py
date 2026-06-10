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

    notes_parts: list[str] = []
    if climate is None:
        return {
            "errors": [f"Не найдены климатические данные для региона '{region}'"],
            "analyst_notes": "Аналитик отказался: нет климатических данных.",
        }

    # Sanity checks — early signals for Designer.
    brief = state.brief
    target_yield_per_m2 = brief.target_annual_yield_t * 1000 / brief.site.plot_area_m2
    notes_parts.append(
        f"Целевая урожайность относительно участка: {target_yield_per_m2:.1f} кг/м²/год"
    )
    if target_yield_per_m2 > 60:
        notes_parts.append("⚠ Целевая урожайность очень высокая — потребуется интенсивная технология.")

    if brief.site.plot_length_m * brief.site.plot_width_m < brief.site.plot_area_m2 * 0.9:
        notes_parts.append("⚠ Указанные размеры участка не сходятся с заявленной площадью (>10%).")

    return {
        "climate": climate,
        "analyst_notes": "\n".join(notes_parts),
    }
