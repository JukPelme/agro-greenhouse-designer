"""Ventilation per СП 107.13330 п. 7.18.

The SP measures vent openings against ENVELOPE area, not floor area.
Multi-span vegetable greenhouses: ≥20% of envelope, ≥10% in regions north
of 60° N latitude. North flag is carried on ClimateData.
"""

from __future__ import annotations

from ..schemas.calc_results import VentilationResult
from ..schemas.design import DesignVariant, GreenhouseLayoutType
from ..schemas.project import ClimateData

_TARGET_ACH = 60.0
_MAX_INDOOR_SUMMER_C = 28.0


def compute_ventilation(design: DesignVariant, climate: ClimateData) -> VentilationResult:
    forced_required = climate.t_design_summer_c >= 30.0

    is_multi_span = any(b.layout == GreenhouseLayoutType.BLOCK for b in design.blocks)
    if is_multi_span:
        envelope_share_pct = 10.0 if climate.is_northern else 20.0
    else:
        envelope_share_pct = 15.0  # single-span — SP says "by calculation", we use a baseline

    # Approximate floor-relative share for backward-compatible reporting.
    envelope_area = sum(b.envelope_area_m2 for b in design.blocks)
    floor_area = sum(b.floor_area_m2 for b in design.blocks) or 1.0
    floor_share_pct = (envelope_share_pct / 100) * envelope_area / floor_area * 100

    if forced_required:
        floor_share_pct = max(floor_share_pct, 12.0)

    return VentilationResult(
        summer_air_changes_per_hour=_TARGET_ACH,
        required_vent_opening_pct_of_floor=round(floor_share_pct, 1),
        forced_vent_required=forced_required,
        opening_share_of_envelope_pct=envelope_share_pct,
    )
