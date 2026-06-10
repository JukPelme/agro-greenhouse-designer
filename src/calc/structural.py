"""Structural loads — snow and wind, very simplified for pre-design."""

from __future__ import annotations

from ..schemas.calc_results import StructuralLoadsResult
from ..schemas.design import DesignVariant
from ..schemas.project import ClimateData


def compute_loads(design: DesignVariant, climate: ClimateData) -> StructuralLoadsResult:
    roof_area_m2 = sum(b.length_m * b.width_m * 1.15 for b in design.blocks)
    wall_area_m2 = sum(
        2 * (b.length_m + b.width_m) * b.eave_height_m for b in design.blocks
    )

    snow_kn = climate.snow_load_kpa * roof_area_m2
    wind_kn = climate.wind_load_kpa * wall_area_m2 * 0.8  # form-factor

    notes = ""
    if climate.snow_load_kpa >= 2.5:
        notes = "Высокая снеговая нагрузка — требуется усиленный каркас и/или подогрев кровли."

    return StructuralLoadsResult(
        snow_load_total_kn=round(snow_kn, 0),
        wind_load_total_kn=round(wind_kn, 0),
        notes=notes,
    )
