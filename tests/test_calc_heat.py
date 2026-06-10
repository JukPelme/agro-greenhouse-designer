"""Sanity tests for heat balance calc.

These are NOT validation against a real reference project — they're guard
rails so a refactor can't silently break the orders of magnitude.
"""

from src.calc.heat import compute_heat_balance
from src.rag.climate_lookup import lookup_climate
from src.schemas.design import (
    CoveringMaterial,
    DesignVariant,
    GreenhouseBlock,
)


def _sample_design() -> DesignVariant:
    return DesignVariant(
        variant_id="t1",
        rationale="test",
        blocks=[
            GreenhouseBlock(
                name="Блок 1",
                length_m=96,
                width_m=25.6,
                ridge_height_m=6.5,
                eave_height_m=5.5,
                covering=CoveringMaterial.GLASS,
                light_transmittance=0.88,
            ),
        ],
        estimated_footprint_m2=3000,
    )


def test_heat_balance_moscow_glass():
    climate = lookup_climate("Московская область")
    assert climate is not None

    result = compute_heat_balance(_sample_design(), climate, t_indoor_c=18.0)

    # Δt for Moscow at +18 indoor and -25 design winter
    assert result.design_temp_diff_c == 43.0

    # Peak load for ~2460 m² floor glass house in Moscow should sit between
    # 400 and 1200 kW — a generous but meaningful sanity envelope.
    assert 400 < result.total_peak_load_kw < 1800

    assert result.total_peak_load_kw > result.transmission_loss_kw


def test_heat_balance_polycarbonate_reduces_load():
    climate = lookup_climate("Московская область")

    glass_design = _sample_design()
    pc_design = _sample_design()
    pc_design.blocks[0].covering = CoveringMaterial.POLYCARBONATE

    glass_result = compute_heat_balance(glass_design, climate)
    pc_result = compute_heat_balance(pc_design, climate)

    assert pc_result.total_peak_load_kw < glass_result.total_peak_load_kw
