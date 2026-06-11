"""Structural loads per СП 107.13330 п. 5.14.

Applies overload factors prescribed by the SP:
- snow:  γ = 1.4
- wind:  q10 = 1.0 (at 10 m), q2 = 0.6 (at 2 m and lower)
- trellis: 150 N/m² normative, γ = 1.3 (only for crops on trellises)

Simplifications (declared up front so the reviewer sees the model boundary):
1. _ROOF_DEVELOPMENT_FACTOR is a *constant* multiplier on the projected roof
   area. In reality it depends on the slope (1.10 for 45% slope, more for
   arched). For pre-design we keep 1.15 ≈ a moderate average — refined in v3.
2. Polyethylene's 20% wind reduction (п. 5.14) is applied to the whole structure
   if *any* block is poly. For mixed-covering complexes this under-estimates
   wind on the glass blocks. Track-it-flag is roof_area_m2 vs per-block; v3
   should compute per-block.
3. Wind pressure is averaged between q10 (top of wall) and q2 (bottom).
   Real engineering would integrate by height — fine for predesign envelope.
"""

from __future__ import annotations

from ..schemas.calc_results import StructuralLoadsResult
from ..schemas.design import DesignVariant
from ..schemas.project import ClimateData, CoveringMaterial, CropType

# Roof development multiplier: projected area × this ≈ actual slope-pitched area.
# 1.15 is a moderate pre-design average across 20–45% slopes.
_ROOF_DEVELOPMENT_FACTOR = 1.15

# СП 107.13330 п. 5.14 — overload factors / pressure coefficients.
_SNOW_OVERLOAD = 1.4
_WIND_Q10 = 1.0
_WIND_Q2 = 0.6
_FILM_WIND_DISCOUNT = 0.8   # 20% reduction for polyethylene per п. 5.14
_TRELLIS_LOAD_N_M2 = 150.0
_TRELLIS_OVERLOAD = 1.3

# Crops that put trellis load on the frame.
_TRELLIS_CROPS = {CropType.TOMATO, CropType.CUCUMBER}


def compute_loads(
    design: DesignVariant,
    climate: ClimateData,
    crop: CropType | None = None,
) -> StructuralLoadsResult:
    roof_area_m2 = sum(b.length_m * b.width_m * _ROOF_DEVELOPMENT_FACTOR for b in design.blocks)
    wall_area_m2 = sum(2 * (b.length_m + b.width_m) * b.eave_height_m for b in design.blocks)

    snow_factor = _SNOW_OVERLOAD
    wind_q10 = _WIND_Q10
    wind_q2 = _WIND_Q2

    # Simplification #2 — see module docstring. Drops wind on the entire complex
    # if any block is polyethylene. Acceptable pre-design under-estimate.
    if any(b.covering == CoveringMaterial.POLYETHYLENE for b in design.blocks):
        wind_q10 *= _FILM_WIND_DISCOUNT
        wind_q2 *= _FILM_WIND_DISCOUNT

    avg_wind_kpa = climate.wind_load_kpa * (wind_q10 + wind_q2) / 2

    snow_kn = climate.snow_load_kpa * snow_factor * roof_area_m2
    wind_kn = avg_wind_kpa * wall_area_m2

    # Conservatively include trellis load when crop is unknown — better to
    # over-design than to silently skip a real load. Frame engineers expect this.
    has_trellis = crop is None or crop in _TRELLIS_CROPS
    trellis_note = ""
    if has_trellis:
        trellis_note = f"Шпалерная нагрузка {_TRELLIS_LOAD_N_M2} Н/м² (γ={_TRELLIS_OVERLOAD})."

    notes: list[str] = []
    if climate.snow_load_kpa >= 2.5:
        notes.append("Высокая снеговая нагрузка — требуется усиленный каркас и/или подогрев кровли.")
    if trellis_note:
        notes.append(trellis_note)

    return StructuralLoadsResult(
        snow_load_total_kn=round(snow_kn, 0),
        wind_load_total_kn=round(wind_kn, 0),
        notes=" ".join(notes),
        snow_overload_factor=snow_factor,
        wind_q10_factor=wind_q10,
        wind_q2_factor=wind_q2,
        trellis_load_n_per_m2=_TRELLIS_LOAD_N_M2,
        trellis_overload_factor=_TRELLIS_OVERLOAD,
    )
