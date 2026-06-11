"""Structural loads per СП 107.13330 п. 5.14.

Applies overload factors prescribed by the SP:
- snow:  γ = 1.4
- wind:  q10 = 1.0 (at 10 m), q2 = 0.6 (at 2 m and lower)
- trellis: 150 N/m² normative, γ = 1.3 (only for crops on trellises)

For polyethylene coverings the wind coefficient is reduced by 20% per п. 5.14.
"""

from __future__ import annotations

from ..schemas.calc_results import StructuralLoadsResult
from ..schemas.design import DesignVariant
from ..schemas.project import ClimateData, CoveringMaterial, CropType

_TRELLIS_CROPS = {CropType.TOMATO, CropType.CUCUMBER}


def compute_loads(
    design: DesignVariant,
    climate: ClimateData,
    crop: CropType | None = None,
) -> StructuralLoadsResult:
    roof_area_m2 = sum(b.length_m * b.width_m * 1.15 for b in design.blocks)
    wall_area_m2 = sum(2 * (b.length_m + b.width_m) * b.eave_height_m for b in design.blocks)

    snow_factor = 1.4
    wind_q10 = 1.0
    wind_q2 = 0.6

    # СП 107.13330 п. 5.14: для плёночных теплиц ветровой коэффициент уменьшается на 20%.
    if any(b.covering == CoveringMaterial.POLYETHYLENE for b in design.blocks):
        wind_q10 *= 0.8
        wind_q2 *= 0.8

    # Effective wind pressure averaged between low and high walls (rough).
    avg_wind_kpa = climate.wind_load_kpa * (wind_q10 + wind_q2) / 2

    snow_kn = climate.snow_load_kpa * snow_factor * roof_area_m2
    wind_kn = avg_wind_kpa * wall_area_m2

    trellis_n_per_m2 = 150.0
    trellis_overload = 1.3
    trellis_note = ""
    if crop is None or crop in _TRELLIS_CROPS:
        trellis_note = f"Шпалерная нагрузка {trellis_n_per_m2} Н/м² (γ={trellis_overload})."

    notes_parts: list[str] = []
    if climate.snow_load_kpa >= 2.5:
        notes_parts.append("Высокая снеговая нагрузка — требуется усиленный каркас и/или подогрев кровли.")
    if trellis_note:
        notes_parts.append(trellis_note)

    return StructuralLoadsResult(
        snow_load_total_kn=round(snow_kn, 0),
        wind_load_total_kn=round(wind_kn, 0),
        notes=" ".join(notes_parts),
        snow_overload_factor=snow_factor,
        wind_q10_factor=wind_q10,
        wind_q2_factor=wind_q2,
        trellis_load_n_per_m2=trellis_n_per_m2,
        trellis_overload_factor=trellis_overload,
    )
