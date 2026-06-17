"""Heat balance per СП 107.13330 п. 7.9 (supply temp), п. 7.13 (lower-zone share).

Branches by greenhouse_type:
- year_round  → ΔT from the design winter temperature t5 (worst-case heating)
- seasonal    → ΔT from a representative early/late-season night temperature
                (a film cover doesn't operate through the deep winter)
- nursery     → treated as seasonal by default
"""

from __future__ import annotations

from ..schemas.calc_results import HeatLossResult
from ..schemas.design import CoveringMaterial, DesignVariant
from ..schemas.project import ClimateData, GreenhouseType

_U_BY_COVERING: dict[CoveringMaterial, float] = {
    CoveringMaterial.GLASS: 6.4,           # single glazing
    CoveringMaterial.POLYCARBONATE: 3.6,   # honeycomb 10 mm
    CoveringMaterial.POLYETHYLENE: 4.2,    # double film with air gap
}

_INFILTRATION_FACTOR = 0.20

# Representative outside temperatures the greenhouse must handle for each
# operating mode. Production code would derive from monthly climate data;
# for pre-design a per-mode constant is enough.
_SEASONAL_T_DESIGN_C = 5.0   # warm spring/autumn night
_NURSERY_T_DESIGN_C = -5.0   # nursery (rassada) protects from frost; cold but not winter peak


def _design_outside_temp(greenhouse_type: GreenhouseType, climate: ClimateData) -> float:
    if greenhouse_type == GreenhouseType.YEAR_ROUND:
        return climate.t_design_winter_c
    if greenhouse_type == GreenhouseType.NURSERY:
        return _NURSERY_T_DESIGN_C
    return _SEASONAL_T_DESIGN_C


def _heating_period_days(greenhouse_type: GreenhouseType, climate: ClimateData) -> int:
    if greenhouse_type == GreenhouseType.YEAR_ROUND:
        return climate.heating_period_days
    if greenhouse_type == GreenhouseType.NURSERY:
        # Nursery runs late winter → early summer ≈ 100 days
        return 100
    # Seasonal heating mainly in spring shoulders ≈ 60 days
    return 60


def _heating_degree_days(greenhouse_type: GreenhouseType, climate: ClimateData) -> float:
    if greenhouse_type == GreenhouseType.YEAR_ROUND:
        return climate.heating_degree_days
    # Approximate seasonal HDD as average ΔT × period days
    return (18.0 - _SEASONAL_T_DESIGN_C) * _heating_period_days(greenhouse_type, climate)


def compute_heat_balance(
    design: DesignVariant,
    climate: ClimateData,
    greenhouse_type: GreenhouseType = GreenhouseType.YEAR_ROUND,
    t_indoor_c: float = 18.0,
    supply_temp_c: float = 95.0,
) -> HeatLossResult:
    t_outside = _design_outside_temp(greenhouse_type, climate)
    delta_t = t_indoor_c - t_outside

    envelope_area = sum(b.envelope_area_m2 for b in design.blocks)
    weighted_u = sum(_U_BY_COVERING[b.covering] * b.envelope_area_m2 for b in design.blocks) / envelope_area

    transmission_w = weighted_u * envelope_area * delta_t
    infiltration_w = transmission_w * _INFILTRATION_FACTOR
    total_w = transmission_w + infiltration_w

    hdd = _heating_degree_days(greenhouse_type, climate)
    annual_kwh = weighted_u * envelope_area * hdd * 24 / 1000
    annual_kwh += annual_kwh * _INFILTRATION_FACTOR

    # СП 107.13330 п. 7.13: ≥ 40% of heat to the 0..1 m zone.
    share_lower = 45.0

    return HeatLossResult(
        design_temp_diff_c=delta_t,
        envelope_area_m2=round(envelope_area, 1),
        overall_heat_transfer_coef_w_m2k=round(weighted_u, 2),
        transmission_loss_kw=round(transmission_w / 1000, 1),
        infiltration_loss_kw=round(infiltration_w / 1000, 1),
        total_peak_load_kw=round(total_w / 1000, 1),
        annual_heat_demand_mwh=round(annual_kwh / 1000, 1),
        supply_temp_c=supply_temp_c,
        share_to_lower_zone_pct=share_lower,
    )
