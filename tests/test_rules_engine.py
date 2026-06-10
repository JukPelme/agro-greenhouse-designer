"""Sanity tests for the rules engine."""

from src.calc.heat import compute_heat_balance
from src.calc.lighting import compute_lighting
from src.calc.structural import compute_loads
from src.calc.ventilation import compute_ventilation
from src.calc.water import compute_water_demand
from src.rag.climate_lookup import lookup_climate
from src.rag.rules_engine import evaluate_rules
from src.schemas.calc_results import EngineeringReport
from src.schemas.design import CoveringMaterial, DesignVariant, GreenhouseBlock
from src.schemas.project import (
    CropType,
    GreenhouseType,
    ProjectBrief,
    SiteParameters,
)


def _full_eng_report(design, climate, crop):
    return EngineeringReport(
        heat=compute_heat_balance(design, climate),
        water=compute_water_demand(design, crop, climate),
        light=compute_lighting(design, crop, climate),
        ventilation=compute_ventilation(design, climate),
        loads=compute_loads(design, climate),
    )


def test_low_light_transmittance_triggers_error():
    """Polyethylene with tau=0.5 should violate SP107.4.1 (>=0.60)."""
    climate = lookup_climate("Краснодарский край")
    brief = ProjectBrief(
        project_name="bad",
        greenhouse_type=GreenhouseType.YEAR_ROUND,
        target_crop=CropType.TOMATO,
        target_annual_yield_t=100.0,
        site=SiteParameters(
            region="Краснодарский край",
            plot_area_m2=5000,
            plot_length_m=100,
            plot_width_m=50,
        ),
    )
    design = DesignVariant(
        variant_id="bad",
        rationale="cheap film",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96,
                width_m=12,
                ridge_height_m=6.0,
                eave_height_m=5.0,
                covering=CoveringMaterial.POLYETHYLENE,
                light_transmittance=0.50,  # too low for year_round
            ),
        ],
        estimated_footprint_m2=1500,
    )
    eng = _full_eng_report(design, climate, CropType.TOMATO)

    issues, checked = evaluate_rules(brief, design, eng)
    rule_ids = {i.rule_id for i in issues}
    assert "SP107.4.1" in rule_ids
    assert checked > 0


def test_low_ridge_height_triggers_for_tomato():
    """Ridge height 4.0 m should violate SP107.5.2 for tomato year-round."""
    climate = lookup_climate("Краснодарский край")
    brief = ProjectBrief(
        project_name="low",
        greenhouse_type=GreenhouseType.YEAR_ROUND,
        target_crop=CropType.TOMATO,
        target_annual_yield_t=100.0,
        site=SiteParameters(
            region="Краснодарский край",
            plot_area_m2=5000,
            plot_length_m=100,
            plot_width_m=50,
        ),
    )
    design = DesignVariant(
        variant_id="low",
        rationale="low ceiling",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96,
                width_m=12,
                ridge_height_m=4.0,  # too low for tomato
                eave_height_m=3.5,
                covering=CoveringMaterial.GLASS,
                light_transmittance=0.88,
            ),
        ],
        estimated_footprint_m2=1500,
    )
    eng = _full_eng_report(design, climate, CropType.TOMATO)
    issues, _ = evaluate_rules(brief, design, eng)
    rule_ids = {i.rule_id for i in issues}
    assert "SP107.5.2" in rule_ids
