"""Heat balance calculations for greenhouses.

References:
- СП 50.13330 «Тепловая защита зданий» (общие принципы)
- НТП-АПК 1.10.09 «Нормы технологического проектирования теплиц»
- Учебник: Ващенко С.Ф. «Тепличное хозяйство», глава по теплотехнике

NB: simplified single-zone steady-state model — enough for pre-design.
Detailed dynamic modelling (TRNSYS, EnergyPlus) is out of scope for MVP.
"""

from __future__ import annotations

from ..schemas.calc_results import HeatLossResult
from ..schemas.design import CoveringMaterial, DesignVariant
from ..schemas.project import ClimateData

# U-values (Вт/(м²·К)) — справочные значения для одного слоя ограждения
_U_BY_COVERING: dict[CoveringMaterial, float] = {
    CoveringMaterial.GLASS: 6.4,           # одинарное остекление
    CoveringMaterial.POLYCARBONATE: 3.6,   # сотовый PC 10 мм
    CoveringMaterial.POLYETHYLENE: 7.5,    # двойная плёнка
}

_INFILTRATION_FACTOR = 0.20  # 20% от трансмиссионных — упрощённо


def compute_heat_balance(
    design: DesignVariant,
    climate: ClimateData,
    t_indoor_c: float = 18.0,
) -> HeatLossResult:
    delta_t = t_indoor_c - climate.t_design_winter_c

    envelope_area = sum(b.envelope_area_m2 for b in design.blocks)
    # Weight U-value by envelope area share if blocks have different coverings.
    weighted_u = sum(
        _U_BY_COVERING[b.covering] * b.envelope_area_m2 for b in design.blocks
    ) / envelope_area

    transmission_w = weighted_u * envelope_area * delta_t
    infiltration_w = transmission_w * _INFILTRATION_FACTOR
    total_w = transmission_w + infiltration_w

    # Annual demand via heating degree days (rough approximation).
    annual_kwh = weighted_u * envelope_area * climate.heating_degree_days * 24 / 1000
    annual_kwh += annual_kwh * _INFILTRATION_FACTOR

    return HeatLossResult(
        design_temp_diff_c=delta_t,
        envelope_area_m2=round(envelope_area, 1),
        overall_heat_transfer_coef_w_m2k=round(weighted_u, 2),
        transmission_loss_kw=round(transmission_w / 1000, 1),
        infiltration_loss_kw=round(infiltration_w / 1000, 1),
        total_peak_load_kw=round(total_w / 1000, 1),
        annual_heat_demand_mwh=round(annual_kwh / 1000, 1),
    )
