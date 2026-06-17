# Pre-design solution: Тестовый отказ системы

**Region:** Новосибирская область
**Greenhouse type:** year-round
**Crop:** tomato
**Target yield:** 2000.0 t/year
**Generated:** 2026-06-17 05:46

---

## 1. Site inputs and analysis

Target yield per plot area: 4000.0 kg/m²/year
⚠ Target yield is very high — intensive technology required.

**Climate parameters (per Russian SP 131.13330):**

| Parameter | Value |
| --- | --- |
| Design winter temperature (t5) | -37.0 °C |
| Design summer temperature | 25.0 °C |
| Heating degree-days | 6076.0 |
| Heating period | 227 days |
| Snow load | 2.4 kPa |
| Wind load | 0.3 kPa |
| Solar radiation (winter) | 1.5 MJ/m²/day |

---

## 2. Design solution (variant failed_v1)

**Rationale:** This design proposes two compact year-round glass greenhouse blocks (Block A and Block B) on a very constrained 25 × 20 m plot in the Novosibirsk region, targeting tomato trellis culture. Glass cladding is chosen to maximise light transmittance (τ ≈ 0.88), which is critical given the region's low winter solar radiation. Each block is a single-span (angar) layout because the plot width cannot accommodate multi-span block configurations while maintaining the mandatory 6 m inter-block clearance for year-round greenhouses per SP 107.13330 clause 4.4. Ridge height is set to 5.5 m as required for trellis tomato culture. It must be noted that the plot (500 m²) is physically unable to deliver 2 000 t/year of tomatoes under any greenhouse configuration — the agronomic carrying capacity of this site is many orders of magnitude below the stated target yield; the project brief contains a fundamental contradiction between plot size and yield target that cannot be resolved by layout changes alone.

**Total growing area:** 72 m²
**Complex footprint (with auxiliary):** 500.0 m²

### Greenhouse blocks

- **Block A** — 6.0 × 6.0 m (area 36 m²)
  - Heights: eave 2.4 m, ridge 5.5 m
  - Layout: angar (single-span), 1 spans of 6.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 15.0%
- **Block B** — 6.0 × 6.0 m (area 36 m²)
  - Heights: eave 2.4 m, ridge 5.5 m
  - Layout: angar (single-span), 1 spans of 6.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 15.0%

### Complex structural parameters

| Parameter | Value | SP Clause |
| --- | --- | --- |
| Plinth height | 0.4 m | 5.8 |
| Foundation rise above soil | 0.4 m | 5.9 |
| Territory fence height | 1.8 m | 4.16 |

### Auxiliary zones

- **Boiler house** — 12.0 m² (Heating plant and utility room)
- **Tool and fertiliser storage** — 8.0 m² (Storage for tools, agrochemicals and fertilisers)
- **Packaging and sorting area** — 8.0 m² (Post-harvest packaging and product sorting)
- **Staff facilities** — 7.0 m² (Changing rooms, sanitary facilities and rest room for personnel)

---

## 3. Engineering calculations

### 3.1. Heat supply

![Heat losses and peak load](charts/failed_v1/energy_balance.png)

- Design temperature difference: **55.0 °C**
- Envelope area: **198.0 m²**
- Overall heat transfer coefficient U: **6.4 W/(m²·K)**
- Transmission losses: **69.7 kW**
- Infiltration losses: **13.9 kW**
- **Peak heating load: 83.6 kW**
- Annual heat demand: **221.7 MWh**
- Coolant temperature: **95.0 °C** _(SP 7.9 ≤150)_
- Lower-zone heat share: **45.0%** _(SP 7.13 ≥40)_

### 3.2. Water supply

![Water demand](charts/failed_v1/water_demand.png)

- Daily demand: **0.32 m³/day**
- Peak hourly: **0.04 m³/h**
- Annual: **97 m³/year**
- Irrigation method: Drip (default)
- Reliability category: **II** _(SP 6.14)_
- Hose service radius: **40.0 m** _(SP 6.8 ≤45)_

### 3.3. Lighting and supplemental

![Light balance](charts/failed_v1/light_balance.png)

- Target DLI: **22.0 mol/m²/day**
- Natural winter DLI: **2.6 mol/m²/day**
- **Supplemental lighting required**: installed 266.2 W/m², consumption 69612 kWh/year
- Aisle floor illuminance: 8.0 lx _(SP 8.3 ≤10)_

### 3.4. Annual energy consumption

![Annual energy breakdown](charts/failed_v1/annual_energy.png)

### 3.5. Ventilation

- Summer target air changes per hour: **60.0 h⁻¹**
- Vent opening share of envelope: **15.0%** _(SP 7.18 ≥20, ≥10 north of 60°N)_
- Vent opening share of floor: 41.2%
- Forced ventilation: **not required**

### 3.6. Structural loads

- Snow load on roof: **278.0 kN** (γ=1.4)
- Wind load on walls: **28.0 kN** (q₁₀=1.0, q₂=0.6)
- Trellis load: 150.0 N/m² (γ=1.3)

_Overload factors and normative values per SP 107.13330 clause 5.14._

### 3.7. Geotechnical conditions and foundation

- Foundation soil: **clay**
- Groundwater depth: **0.5 m**
- Recommended foundation type: **pile**
- Minimum embedment depth: **3.0 m**
- Perimeter drainage: **required**
- Waterproofing grade: **enhanced**

> Clay with high groundwater table — frost-heaving soil. Pile foundation embedded below the freezing depth; enhanced waterproofing and mandatory perimeter drainage required.

_Preliminary recommendations. A proper engineering-geological survey per SP 47.13330 is required for working documentation._

---

## 4. SP 107.13330 compliance check

Rules checked: **35**

### ERROR — ENG.5-yield-feasibility

Площадь выращивания × норма культуры должна покрывать минимум 90% целевой урожайности из ТЗ. Иначе участок физически не вмещает заявленный объём продукции.

- Actual: `вмещает ~4 т/год (tomato @ 50.0 кг/м² × 72 м²)`
- Required: `>= 1800 т/год (90% от ТЗ 2000.0 т)`
- **Source** _(SP 107.13330, original Russian text)_: Инженерная проверка (не из СП): достижимость целевой урожайности


---

_Generated by agro-greenhouse-designer. Outputs are pre-design estimates and require validation by a qualified engineer before detailed documentation._