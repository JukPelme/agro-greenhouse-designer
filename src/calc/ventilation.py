"""Ventilation calculation — summer overheating control."""

from __future__ import annotations

from ..schemas.calc_results import VentilationResult
from ..schemas.design import DesignVariant
from ..schemas.project import ClimateData

_MAX_INDOOR_SUMMER_C = 28.0
_TARGET_ACH_NATURAL = 60.0  # типовое для остеклённых теплиц с боковой и коньковой вентиляцией


def compute_ventilation(
    design: DesignVariant,
    climate: ClimateData,
) -> VentilationResult:
    # If outdoor design summer is above 30 — natural alone usually insufficient.
    forced_required = climate.t_design_summer_c >= 30.0

    # Required opening as % of floor area: NTP-APK recommends >=20% for natural-only.
    if forced_required:
        opening_pct = 12.0
    elif climate.t_design_summer_c >= 25.0:
        opening_pct = 20.0
    else:
        opening_pct = 15.0

    return VentilationResult(
        summer_air_changes_per_hour=_TARGET_ACH_NATURAL,
        required_vent_opening_pct_of_floor=opening_pct,
        forced_vent_required=forced_required,
    )
