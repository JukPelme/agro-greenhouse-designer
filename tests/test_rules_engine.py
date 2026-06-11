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


def test_film_with_opaque_share_too_high_triggers_sp511_and_eng3():
    """τ=0.50 violates ENG.3 (<0.60); opaque_share_pct=15 violates SP107.5.11-film (>10%)."""
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
    design = DesignVariant(
        variant_id="bad",
        rationale="cheap film + lots of opaque",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96,
                width_m=12,
                ridge_height_m=6.0,
                eave_height_m=5.0,
                covering=CoveringMaterial.POLYETHYLENE,
                light_transmittance=0.50,
                opaque_share_pct=15.0,
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



def test_block_span_violates_5_5_for_multi_span():
    """Multi-span block with span_width=12 m violates SP107.5.5-span-block (cap 9 m)."""
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
    from src.schemas.design import GreenhouseLayoutType
    design = DesignVariant(
        variant_id="wide-span",
        rationale="too-wide multi-span",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96, width_m=24, ridge_height_m=6.5, eave_height_m=5.5,
                covering=CoveringMaterial.GLASS, light_transmittance=0.88,
                layout=GreenhouseLayoutType.BLOCK,
                span_width_m=12.0,  # > 9 cap
                span_count=2,
            ),
            GreenhouseBlock(
                name="Блок 2",
                length_m=96, width_m=24, ridge_height_m=6.5, eave_height_m=5.5,
                covering=CoveringMaterial.GLASS, light_transmittance=0.88,
                layout=GreenhouseLayoutType.BLOCK,
                span_width_m=12.0,
                span_count=2,
            ),
        ],
        estimated_footprint_m2=5000,
    )
    eng = _engineer(design, climate, CropType.TOMATO)
    issues, _ = evaluate_rules(brief, design, eng)
    assert "SP107.5.5-span-block" in {i.rule_id for i in issues}


def test_low_plinth_triggers_5_8():
    """plinth_height_m=0.2 violates SP107.5.8 (≥ 0.3)."""
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
    design = DesignVariant(
        variant_id="low-plinth",
        rationale="shallow plinth",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96, width_m=12, ridge_height_m=6.0, eave_height_m=5.0,
                covering=CoveringMaterial.GLASS, light_transmittance=0.88,
            ),
        ],
        estimated_footprint_m2=1500,
        plinth_height_m=0.2,
    )
    eng = _engineer(design, climate, CropType.TOMATO)
    issues, _ = evaluate_rules(brief, design, eng)
    assert "SP107.5.8" in {i.rule_id for i in issues}


def test_glass_thickness_too_thick_triggers_5_23():
    """glass_thickness_mm=6 violates SP107.5.23 (≤4)."""
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
    design = DesignVariant(
        variant_id="thick-glass",
        rationale="too thick",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96, width_m=12, ridge_height_m=6.0, eave_height_m=5.0,
                covering=CoveringMaterial.GLASS, light_transmittance=0.88,
                glass_thickness_mm=6.0,
            ),
        ],
        estimated_footprint_m2=1500,
    )
    eng = _engineer(design, climate, CropType.TOMATO)
    issues, _ = evaluate_rules(brief, design, eng)
    assert "SP107.5.23" in {i.rule_id for i in issues}



def test_mixed_layout_catches_only_offending_block():
    """Ангар 25 м (нарушает SP107.5.5-span-angar ≤21) + блок 9 м (валидный).

    Pairwise engine should fire only for the angar block, not skip the rule
    because the other block has layout=block.
    """
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
    from src.schemas.design import GreenhouseLayoutType
    design = DesignVariant(
        variant_id="mixed",
        rationale="angar + block",
        blocks=[
            GreenhouseBlock(
                name="Ангарный 25 м",
                length_m=96, width_m=25, ridge_height_m=6.5, eave_height_m=5.5,
                covering=CoveringMaterial.GLASS, light_transmittance=0.88,
                layout=GreenhouseLayoutType.ANGAR, span_width_m=25.0, span_count=1,
            ),
            GreenhouseBlock(
                name="Блочный 9 м",
                length_m=96, width_m=18, ridge_height_m=6.5, eave_height_m=5.5,
                covering=CoveringMaterial.GLASS, light_transmittance=0.88,
                layout=GreenhouseLayoutType.BLOCK, span_width_m=9.0, span_count=2,
            ),
        ],
        estimated_footprint_m2=4500,
    )
    eng = _engineer(design, climate, CropType.TOMATO)
    issues, _ = evaluate_rules(brief, design, eng, climate=climate)
    rule_ids = {i.rule_id for i in issues}
    assert "SP107.5.5-span-angar" in rule_ids  # the angar 25 m is over the 21 m cap


def test_eng1_ridge_below_eave_triggers_custom_check():
    """ridge=5.0 eave=5.5 (ridge < eave + 0.5) should trigger ENG.1 custom check."""
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
    design = DesignVariant(
        variant_id="flat-roof",
        rationale="ridge equals eave — bad",
        blocks=[
            GreenhouseBlock(
                name="Блок плоский",
                length_m=96, width_m=12, ridge_height_m=5.0, eave_height_m=5.5,
                covering=CoveringMaterial.GLASS, light_transmittance=0.88,
            ),
        ],
        estimated_footprint_m2=1500,
    )
    eng = _engineer(design, climate, CropType.TOMATO)
    issues, _ = evaluate_rules(brief, design, eng, climate=climate)
    assert "ENG.1-ridge-vs-eave" in {i.rule_id for i in issues}


def test_aux_share_between_5_and_30_passes():
    """Aux share inside the band 5..30 should NOT trigger ENG.2-aux-share."""
    climate = lookup_climate("Краснодарский край")
    brief = _brief()
    from src.schemas.design import LayoutZone
    design = DesignVariant(
        variant_id="balanced",
        rationale="15% aux",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96, width_m=12, ridge_height_m=6.0, eave_height_m=5.0,
                covering=CoveringMaterial.GLASS, light_transmittance=0.88,
            ),
        ],
        aux_zones=[LayoutZone(name="Aux", area_m2=300.0, purpose="test")],
        estimated_footprint_m2=2000,
    )
    eng = _engineer(design, climate, CropType.TOMATO)
    issues, _ = evaluate_rules(brief, design, eng, climate=climate)
    assert "ENG.2-aux-share" not in {i.rule_id for i in issues}
