"""Input schemas: project brief (ТЗ) and intermediate domain models."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class GreenhouseType(str, Enum):
    YEAR_ROUND = "year_round"
    SEASONAL = "seasonal"
    NURSERY = "nursery"


class CropType(str, Enum):
    TOMATO = "tomato"
    CUCUMBER = "cucumber"
    LETTUCE = "lettuce"
    HERBS = "herbs"
    STRAWBERRY = "strawberry"


class CoveringMaterial(str, Enum):
    GLASS = "glass"
    POLYCARBONATE = "polycarbonate"
    POLYETHYLENE = "polyethylene"


class SoilType(str, Enum):
    SAND = "sand"
    LOAM = "loam"
    CLAY = "clay"
    ROCKY = "rocky"


class SiteParameters(BaseModel):
    """Site-level inputs that constrain layout and engineering."""

    model_config = ConfigDict(extra="allow")

    region: str = Field(..., description="Регион РФ для climate lookup из СП 131.13330")
    plot_area_m2: float = Field(..., gt=0)
    plot_length_m: float = Field(..., gt=0)
    plot_width_m: float = Field(..., gt=0)
    elevation_m: float = Field(default=0, description="Высота над уровнем моря, м")
    soil_type: SoilType = SoilType.LOAM
    groundwater_depth_m: float = Field(default=3.0, gt=0)
    has_grid_power: bool = True
    has_water_supply: bool = True
    has_gas_supply: bool = False

    # СП 107.13330 п. 4.6 — зооветеринарные разрывы (необязательно, по умолчанию большая дистанция)
    distance_to_animal_facilities_m: float = Field(
        default=1000.0,
        description="Расстояние до ближайших животноводческих/птицеводческих комплексов, м",
    )

    # СП 107.13330 п. 4.9 — снегозащита
    snow_transfer_volume_m3_per_m: float = Field(
        default=0.0,
        description="Объём снегопереноса за зиму на 1 м фронта, м³/м (нужен при >200)",
    )


class ProjectBrief(BaseModel):
    """The 'ТЗ' — what the client wants."""

    project_name: str
    greenhouse_type: GreenhouseType
    target_crop: CropType
    target_annual_yield_t: float = Field(..., gt=0)
    site: SiteParameters
    budget_rub: float | None = Field(default=None)
    notes: str = Field(default="")


class ClimateData(BaseModel):
    """Climatology snapshot per SP 131.13330 for the project region."""

    region: str
    t_design_winter_c: float = Field(..., description="Расчётная зимняя температура (t5), °C")
    t_design_summer_c: float
    heating_degree_days: float
    heating_period_days: int
    avg_wind_speed_winter_ms: float
    snow_load_kpa: float
    wind_load_kpa: float
    solar_radiation_winter_mj_m2_day: float

    # Для СП 107.13330 п. 7.18: «севернее 60° с.ш.» — отдельный пороговый процент вентиляции
    is_northern: bool = Field(default=False, description="True если регион севернее 60° с.ш.")
