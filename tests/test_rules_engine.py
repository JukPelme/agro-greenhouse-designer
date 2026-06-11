"""Sanity tests for the rules engine.

These tests pin specific rule_ids — they will fail if rules.yaml changes
identifiers, which is intentional. Update tests when intentionally renaming.
"""

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


def _engineer(design, climate, crop):
    return EngineeringReport(
        heat=compute_heat_balance(design, climate),
        water=compute_water_demand(design, crop, climate),
        light=compute_lighting(design, crop, climate),
        ventilation=compute_ventilation(design, climate),
        loads=compute_loads(design, climate),
    )


def _brief(crop=CropType.TOMATO, kind=GreenhouseType.YEAR_ROUND):
    return ProjectBrief(
        project_name="test",
        greenhouse_type=kind,
        target_crop=crop,
        target_annual_yield_t=100.0,
        site=SiteParameters(
            region="Краснодарский край",
            plot_area_m2=5000,
            plot_length_m=100,
            plot_width_m=50,
        ),
    )


def test_low_light_polyethylene_triggers_engineering_and_sp_511():
    """tau=0.50 on polyethylene violates ENG.3 (<0.60) AND SP107.5.11-film (<0.90)."""
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
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
                light_transmittance=0.50,
            ),
        ],
        estimated_footprint_m2=1500,
    )
    eng = _engineer(design, climate, CropType.TOMATO)
    issues, checked = evaluate_rules(brief, design, eng)
    rule_ids = {i.rule_id for i in issues}
    assert "ENG.3-light-min" in rule_ids
    assert "SP107.5.11-film" in rule_ids
    assert checked > 0


def test_year_round_passes_when_aisle_and_transmittance_ok():
    """Sanity: a sensible year-round design with two glass blocks should NOT trip 4.4 or 5.11."""
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
    design = DesignVariant(
        variant_id="good",
        rationale="reasonable",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96,
                width_m=12,
                ridge_height_m=6.0,
                eave_height_m=5.0,
                covering=CoveringMaterial.GLASS,
                light_transmittance=0.88,
            ),
            GreenhouseBlock(
                name="Блок 2",
                length_m=96,
                width_m=12,
                ridge_height_m=6.0,
                eave_height_m=5.0,
                covering=CoveringMaterial.GLASS,
                light_transmittance=0.88,
            ),
        ],
        # Enough aux to satisfy ENG.2-aux-share (≥5%)
        aux_zones=[],
        estimated_footprint_m2=2500,
    )
    eng = _engineer(design, climate, CropType.TOMATO)
    issues, _ = evaluate_rules(brief, design, eng)
    rule_ids = {i.rule_id for i in issues}
    assert "SP107.4.4-year-round" not in rule_ids  # min_aisle defaults to 6.0 with >=2 blocks
    assert "SP107.5.11-glass" not in rule_ids  # tau=0.88 >= 0.85
    assert "ENG.3-light-min" not in rule_ids  # tau=0.88 >= 0.60
