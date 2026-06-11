"""Schemas for engineering calculation outputs.

Expanded with SP 107.13330-aligned fields:
- heat.share_to_lower_zone_pct  ← п. 7.13 (≥40%)
- heat.supply_temp_c            ← п. 7.9 (≤150 °C)
- water.reliability_category    ← п. 6.14 (I/II/III)
- water.hose_service_radius_m   ← п. 6.8 (≤45 м)
- ventilation.opening_share_of_envelope_pct ← п. 7.18 (≥20% или ≥10% севернее 60°)
- loads.snow_overload_factor, wind_q10_factor, trellis_load_n_per_m2 ← п. 5.14
"""

from typing import Literal

from pydantic import BaseModel, Field


class HeatLossResult(BaseModel):
    design_temp_diff_c: float
    envelope_area_m2: float
    overall_heat_transfer_coef_w_m2k: float
    transmission_loss_kw: float
    infiltration_loss_kw: float
    total_peak_load_kw: float
    annual_heat_demand_mwh: float

    # СП 107.13330
    supply_temp_c: float = Field(default=95.0, description="Температура теплоносителя, °C (п. 7.9 ≤150)")
    share_to_lower_zone_pct: float = Field(
        default=45.0,
        ge=0,
        le=100,
        description="Доля теплоты в нижнюю зону высотой 1 м (п. 7.13 ≥40%)",
    )


class WaterDemandResult(BaseModel):
    daily_demand_m3: float
    peak_hourly_m3: float
    annual_demand_m3: float
    irrigation_method: str

    # СП 107.13330 п. 6.14 / п. 6.8
    reliability_category: Literal[1, 2, 3] = Field(
        default=2,
        description="I=1, II=2, III=3. Для теплиц по п. 6.14 — I или II. Для парников допустима III.",
    )
    hose_service_radius_m: float = Field(
        default=40.0,
        gt=0,
        description="Радиус зоны обслуживания одним поливным краном, м (п. 6.8 ≤45)",
    )


class LightingResult(BaseModel):
    target_dli_mol_m2_day: float
    natural_dli_winter_mol_m2_day: float
    supplemental_required: bool
    installed_lamp_power_w_m2: float
    supplemental_kwh_year: float

    # СП 107.13330 п. 8.3
    aisle_floor_illuminance_lx: float = Field(
        default=8.0,
        ge=0,
        description="Освещённость на уровне пола в проездах, лк (п. 8.3 ≤10)",
    )


class VentilationResult(BaseModel):
    summer_air_changes_per_hour: float
    required_vent_opening_pct_of_floor: float
    forced_vent_required: bool

    # СП 107.13330 п. 7.18 — реальная формулировка
    opening_share_of_envelope_pct: float = Field(
        default=20.0,
        ge=0,
        description="Площадь проёмов как доля от площади ограждения, % (п. 7.18 ≥20, ≥10 севернее 60°)",
    )


class StructuralLoadsResult(BaseModel):
    snow_load_total_kn: float
    wind_load_total_kn: float
    notes: str = Field(default="")

    # СП 107.13330 п. 5.14 — коэффициенты перегрузки и нормативные значения
    snow_overload_factor: float = Field(default=1.4, description="Коэффициент перегрузки снеговой нагрузки")
    wind_q10_factor: float = Field(default=1.0, description="Коэф. скоростного напора ветра на 10 м")
    wind_q2_factor: float = Field(default=0.6, description="Коэф. скоростного напора ветра на 2 м и менее")
    trellis_load_n_per_m2: float = Field(
        default=150.0,
        description="Нормативная нагрузка от шпалер с растениями, Н/м² (п. 5.14)",
    )
    trellis_overload_factor: float = Field(default=1.3)


class EngineeringReport(BaseModel):
    heat: HeatLossResult
    water: WaterDemandResult
    light: LightingResult
    ventilation: VentilationResult
    loads: StructuralLoadsResult
