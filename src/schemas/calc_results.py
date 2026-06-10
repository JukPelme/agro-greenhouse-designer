"""Schemas for engineering calculation outputs."""

from pydantic import BaseModel, Field


class HeatLossResult(BaseModel):
    """Результат теплотехнического расчёта."""

    design_temp_diff_c: float = Field(..., description="ΔT = T_indoor - T_outdoor")
    envelope_area_m2: float
    overall_heat_transfer_coef_w_m2k: float = Field(..., description="U-value, Вт/(м²·К)")
    transmission_loss_kw: float = Field(..., description="Трансмиссионные теплопотери, кВт")
    infiltration_loss_kw: float
    total_peak_load_kw: float = Field(..., description="Расчётная пиковая нагрузка, кВт")
    annual_heat_demand_mwh: float = Field(..., description="Годовая потребность в тепле, МВт·ч")


class WaterDemandResult(BaseModel):
    daily_demand_m3: float = Field(..., description="Суточный расход воды, м³")
    peak_hourly_m3: float
    annual_demand_m3: float
    irrigation_method: str = Field(..., description="Капельное / дождевание / гидропоника")


class LightingResult(BaseModel):
    target_dli_mol_m2_day: float = Field(..., description="Требуемая daily light integral")
    natural_dli_winter_mol_m2_day: float
    supplemental_required: bool
    installed_lamp_power_w_m2: float = Field(..., ge=0)
    supplemental_kwh_year: float = Field(..., ge=0)


class VentilationResult(BaseModel):
    summer_air_changes_per_hour: float = Field(..., description="Кратность воздухообмена летом")
    required_vent_opening_pct_of_floor: float = Field(..., description="Площадь открываемых проёмов, %")
    forced_vent_required: bool


class StructuralLoadsResult(BaseModel):
    snow_load_total_kn: float
    wind_load_total_kn: float
    notes: str = Field(default="")


class EngineeringReport(BaseModel):
    heat: HeatLossResult
    water: WaterDemandResult
    light: LightingResult
    ventilation: VentilationResult
    loads: StructuralLoadsResult
