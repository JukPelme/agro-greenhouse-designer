"""Supplemental lighting — DLI-based approach.

Branches by greenhouse_type:
- year_round           → DLI deficit covered by HPS/LED supplemental lighting
- seasonal / nursery   → no supplemental lighting (natural daylight in season
                          is sufficient for typical Russian latitudes)
"""

from __future__ import annotations

from ..schemas.calc_results import LightingResult
from ..schemas.design import DesignVariant
from ..schemas.project import ClimateData, CropType, GreenhouseType

# Target DLI (mol/m²/day) per crop.
_TARGET_DLI: dict[CropType, float] = {
    CropType.TOMATO: 22.0,
    CropType.CUCUMBER: 20.0,
    CropType.LETTUCE: 14.0,
    CropType.HERBS: 12.0,
    CropType.STRAWBERRY: 17.0,
}

# Crude PAR conversion: 1 MJ/m²/day total solar ≈ 2.0 mol/m²/day PAR.
_PAR_FACTOR = 2.0


def compute_lighting(
    design: DesignVariant,
    crop: CropType,
    climate: ClimateData,
    greenhouse_type: GreenhouseType = GreenhouseType.YEAR_ROUND,
) -> LightingResult:
    target = _TARGET_DLI.get(crop, 18.0)

    growing_m2 = sum(b.floor_area_m2 for b in design.blocks)
    weighted_tau = sum(b.light_transmittance * b.floor_area_m2 for b in design.blocks) / growing_m2

    natural_dli = climate.solar_radiation_winter_mj_m2_day * _PAR_FACTOR * weighted_tau

    # Seasonal greenhouses run when daylight is sufficient — no supplemental.
    if greenhouse_type != GreenhouseType.YEAR_ROUND:
        return LightingResult(
            target_dli_mol_m2_day=target,
            natural_dli_winter_mol_m2_day=round(natural_dli, 1),
            supplemental_required=False,
            installed_lamp_power_w_m2=0.0,
            supplemental_kwh_year=0.0,
        )

    deficit_dli = max(target - natural_dli, 0)
    if deficit_dli == 0:
        return LightingResult(
            target_dli_mol_m2_day=target,
            natural_dli_winter_mol_m2_day=round(natural_dli, 1),
            supplemental_required=False,
            installed_lamp_power_w_m2=0.0,
            supplemental_kwh_year=0.0,
        )

    # 1 mol PAR ≈ 0.22 kWh of HPS electrical at typical efficacy 1.8 µmol/J.
    # 16 h supplemental window assumed.
    kwh_per_day_per_m2 = deficit_dli * 0.22
    installed_w_m2 = kwh_per_day_per_m2 * 1000 / 16
    annual_kwh = kwh_per_day_per_m2 * growing_m2 * climate.heating_period_days

    return LightingResult(
        target_dli_mol_m2_day=target,
        natural_dli_winter_mol_m2_day=round(natural_dli, 1),
        supplemental_required=True,
        installed_lamp_power_w_m2=round(installed_w_m2, 1),
        supplemental_kwh_year=round(annual_kwh, 0),
    )
