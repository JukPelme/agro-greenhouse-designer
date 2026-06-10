"""Water demand calculation — drip irrigation default."""

from __future__ import annotations

from ..schemas.calc_results import WaterDemandResult
from ..schemas.design import DesignVariant
from ..schemas.project import ClimateData, CropType

# l/m²/day at peak transpiration, source: VNII Ovoshchevodstva guides
_PEAK_DAILY_L_M2: dict[CropType, float] = {
    CropType.TOMATO: 4.5,
    CropType.CUCUMBER: 5.5,
    CropType.LETTUCE: 2.0,
    CropType.HERBS: 1.5,
    CropType.STRAWBERRY: 3.0,
}


def compute_water_demand(
    design: DesignVariant,
    crop: CropType,
    climate: ClimateData,  # noqa: ARG001 — climate-corrected version is v2
) -> WaterDemandResult:
    growing_m2 = sum(b.floor_area_m2 for b in design.blocks)
    peak_l_per_m2 = _PEAK_DAILY_L_M2.get(crop, 4.0)

    daily_m3 = growing_m2 * peak_l_per_m2 / 1000
    peak_hourly = daily_m3 / 8  # peak irrigation window ~8 hours
    annual_m3 = daily_m3 * 300  # active growing days

    return WaterDemandResult(
        daily_demand_m3=round(daily_m3, 2),
        peak_hourly_m3=round(peak_hourly, 2),
        annual_demand_m3=round(annual_m3, 0),
        irrigation_method="Капельное (по умолчанию)",
    )
