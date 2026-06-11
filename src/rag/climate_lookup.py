"""Climate fixtures derived from СП 131.13330.2020 'Строительная климатология'.

For MVP we hard-code 5 representative Russian regions. Production version would
parse the full SP 131 tables, but for portfolio this gives realistic numbers
across cold/temperate/southern zones.

Values: t5 — design winter temperature (mean of coldest 5-day period);
        snow load — district II..VIII per СП 20.13330 Table 10.1;
        wind load — district I..VII per СП 20.13330 Table 11.1.
"""

from __future__ import annotations

from ..schemas.project import ClimateData

_REGIONS: dict[str, ClimateData] = {
    "Краснодарский край": ClimateData(
        region="Краснодарский край",
        t_design_winter_c=-19.0,
        t_design_summer_c=29.4,
        heating_degree_days=2510,
        heating_period_days=149,
        avg_wind_speed_winter_ms=3.6,
        snow_load_kpa=1.0,   # район II
        wind_load_kpa=0.38,  # район IV
        solar_radiation_winter_mj_m2_day=3.8,
    ),
    "Московская область": ClimateData(
        region="Московская область",
        t_design_winter_c=-25.0,
        t_design_summer_c=22.6,
        heating_degree_days=4564,
        heating_period_days=205,
        avg_wind_speed_winter_ms=4.2,
        snow_load_kpa=1.8,   # район III
        wind_load_kpa=0.23,  # район I
        solar_radiation_winter_mj_m2_day=1.6,
    ),
    "Ленинградская область": ClimateData(
        is_northern=False,  # СПб ~60° с.ш., но к зоне «севернее 60°» СП относит области выше Полярного круга
        region="Ленинградская область",
        t_design_winter_c=-24.0,
        t_design_summer_c=20.1,
        heating_degree_days=4796,
        heating_period_days=213,
        avg_wind_speed_winter_ms=4.8,
        snow_load_kpa=1.5,   # район III
        wind_load_kpa=0.30,  # район II
        solar_radiation_winter_mj_m2_day=1.1,
    ),
    "Свердловская область": ClimateData(
        region="Свердловская область",
        t_design_winter_c=-32.0,
        t_design_summer_c=23.4,
        heating_degree_days=5360,
        heating_period_days=221,
        avg_wind_speed_winter_ms=3.9,
        snow_load_kpa=2.0,   # район IV
        wind_load_kpa=0.30,  # район II
        solar_radiation_winter_mj_m2_day=1.4,
    ),
    "Новосибирская область": ClimateData(
        region="Новосибирская область",
        t_design_winter_c=-37.0,
        t_design_summer_c=25.0,
        heating_degree_days=6076,
        heating_period_days=227,
        avg_wind_speed_winter_ms=4.5,
        snow_load_kpa=2.4,   # район V
        wind_load_kpa=0.30,  # район II
        solar_radiation_winter_mj_m2_day=1.5,
    ),
}


def lookup_climate(region: str) -> ClimateData | None:
    return _REGIONS.get(region)


def available_regions() -> list[str]:
    return sorted(_REGIONS.keys())
