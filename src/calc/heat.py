"""Heat balance + СП 107.13330 п. 7.9 supply temp, п. 7.13 share to lower zone."""

from __future__ import annotations

from ..schemas.calc_results import HeatLossResult
from ..schemas.design import CoveringMaterial, DesignVariant
from ..schemas.project import ClimateData

_U_BY_COVERING: dict[CoveringMaterial, float] = {
    CoveringMaterial.GLASS: 6.4,
    CoveringMaterial.POLYCARBONATE: 3.6,
    CoveringMaterial.POLYETHYLENE: 7.5,
}

_INFILTRATION_FACTOR = 0.20


def compute_heat_balance(
    design: DesignVariant,
    climate: ClimateData,
    t_indoor_c: float = 18.0,
    supply_temp_c: float = 95.0,
) -> HeatLossResult:
    delta_t = t_indoor_c - climate.t_design_winter_c

    envelope_area = sum(b.envelope_area_m2 for b in design.blocks)
    weighted_u = sum(_U_BY_COVERING[b.covering] * b.envelope_area_m2 for b in design.blocks) / envelope_area

    transmission_w = weighted_u * envelope_area * delta_t
    infiltration_w = transmission_w * _INFILTRATION_FACTOR
    total_w = transmission_w + infiltration_w

    annual_kwh = weighted_u * envelope_area * climate.heating_degree_days * 24 / 1000
    annual_kwh += annual_kwh * _INFILTRATION_FACTOR

    # СП 107.13330 п. 7.13: не менее 40% теплоты подаётся в зону 0..1 м над почвой.
    # Designer может ставить выше через расчёт системы; здесь обоснованный default.
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
