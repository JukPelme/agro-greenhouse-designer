"""Input schemas: project brief (ТЗ) and intermediate domain models."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


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

    region: str = Field(..., description="Russian region for climate lookup, e.g. 'Краснодарский край'")
    plot_area_m2: float = Field(..., gt=0, description="Total available plot area, m²")
    plot_length_m: float = Field(..., gt=0)
    plot_width_m: float = Field(..., gt=0)
    elevation_m: float = Field(default=0, description="Elevation above sea level, m")
    soil_type: SoilType = SoilType.LOAM
    groundwater_depth_m: float = Field(default=3.0, gt=0)
    has_grid_power: bool = True
    has_water_supply: bool = True
    has_gas_supply: bool = False


class ProjectBrief(BaseModel):
    """The 'ТЗ' — what the client wants."""

    project_name: str
    greenhouse_type: GreenhouseType
    target_crop: CropType
    target_annual_yield_t: float = Field(..., gt=0, description="Tonnes per year")
    site: SiteParameters
    budget_rub: float | None = Field(default=None, description="Optional CAPEX cap, RUB")
    notes: str = Field(default="", description="Free-form additional requirements")

    @field_validator("plot_length_m", "plot_width_m", check_fields=False)
    @classmethod
    def _positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be positive")
        return v


class ClimateData(BaseModel):
    """Climatology snapshot per SP 131.13330 for the project region."""

    region: str
    t_design_winter_c: float = Field(..., description="Design winter temperature (-5 day mean), °C")
    t_design_summer_c: float
    heating_degree_days: float = Field(..., description="Sum of (T_indoor - T_outdoor) for heating period")
    heating_period_days: int
    avg_wind_speed_winter_ms: float
    snow_load_kpa: float = Field(..., description="Normative snow load, kPa")
    wind_load_kpa: float
    solar_radiation_winter_mj_m2_day: float
