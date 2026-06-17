"""Pre-design geotechnical recommendations from soil type + groundwater depth.

This is a rule-of-thumb mapper, not a substitute for an actual survey.
A typical Russian engineering-geological survey (СП 47.13330) is required
before working documentation. Here we only produce sensible defaults that
the Designer can challenge and the Reporter can show in the brief.

References used for the heuristics:
- СП 22.13330 (фундаменты) — minimum embedment depth for soil classes
- СП 50-101-2004 — strip vs pile selection for low-rise structures
- Industry practice for greenhouses on weak soils (clay with high water
  table → pile rafts; rocky → monolithic slab; sand → strip)
"""

from __future__ import annotations

from ..schemas.calc_results import GeotechnicalResult
from ..schemas.project import SiteParameters, SoilType


def compute_geotechnical(site: SiteParameters) -> GeotechnicalResult:
    soil = site.soil_type
    gwd = site.groundwater_depth_m

    from ..i18n import t

    if soil == SoilType.ROCKY:
        foundation = "slab"
        depth = 0.5
        notes_key = "geotech_rocky"
    elif soil == SoilType.SAND:
        foundation = "strip"
        depth = 0.7
        notes_key = "geotech_sand"
    elif soil == SoilType.LOAM:
        foundation = "strip"
        depth = 1.0
        notes_key = "geotech_loam"
    elif soil == SoilType.CLAY:
        if gwd < 1.5:
            foundation = "pile"
            depth = 3.0
            notes_key = "geotech_clay_high_water"
        else:
            foundation = "strip"
            depth = 1.5
            notes_key = "geotech_clay_dry"
    else:
        foundation = "strip"
        depth = 1.0
        notes_key = "geotech_unknown"
    notes = t(notes_key, "ru")  # fallback raw text for non-templated consumers

    drainage_required = (
        gwd < 1.0
        or soil == SoilType.CLAY
        or (soil == SoilType.LOAM and gwd < 2.0)
    )

    waterproofing = "enhanced" if (gwd < 1.5 or soil == SoilType.CLAY) else "standard"

    return GeotechnicalResult(
        soil_type=soil.value,
        groundwater_depth_m=gwd,
        recommended_foundation=foundation,
        foundation_depth_min_m=depth,
        drainage_required=drainage_required,
        waterproofing_grade=waterproofing,
        notes=notes,
        notes_key=notes_key,
    )
