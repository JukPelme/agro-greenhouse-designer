"""Engineer agent: runs deterministic calc.* functions on the proposed design.

NB: there is no LLM call here. Engineer is a pure function over the design
and climate. The LLM stays out of arithmetic by design — this is the central
trustworthiness pattern for the system.

Inputs:  GraphState.design, GraphState.climate, GraphState.brief
Outputs: GraphState.engineering
"""

from __future__ import annotations

from ..calc import geotechnical, heat, lighting, structural, ventilation, water
from ..schemas.calc_results import EngineeringReport
from ..schemas.state import GraphState


def engineer_node(state: GraphState) -> dict:
    if state.design is None or state.climate is None:
        return {"errors": ["Engineer: нет design или climate."]}

    design = state.design
    climate = state.climate
    brief = state.brief

    heat_result = heat.compute_heat_balance(
        design=design, climate=climate, greenhouse_type=brief.greenhouse_type, t_indoor_c=18.0
    )
    water_result = water.compute_water_demand(
        design=design, crop=brief.target_crop, climate=climate, greenhouse_type=brief.greenhouse_type
    )
    light_result = lighting.compute_lighting(
        design=design, crop=brief.target_crop, climate=climate, greenhouse_type=brief.greenhouse_type
    )
    vent_result = ventilation.compute_ventilation(design=design, climate=climate)
    loads_result = structural.compute_loads(design=design, climate=climate, crop=brief.target_crop)
    geotech_result = geotechnical.compute_geotechnical(site=brief.site)

    return {
        "engineering": EngineeringReport(
            heat=heat_result,
            water=water_result,
            light=light_result,
            ventilation=vent_result,
            loads=loads_result,
            geotechnical=geotech_result,
        )
    }
