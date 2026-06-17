# Pre-design solution: Тестовый отказ системы

**Region:** Новосибирская область
**Greenhouse type:** year-round
**Crop:** tomato
**Target yield:** 2000.0 t/year
**Generated:** 2026-06-17 06:36

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

**Rationale:** This is a year-round glass greenhouse complex designed for intensive tomato production (trellis culture) in the severe continental climate of the Novosibirsk region. Glass cladding is selected to maximise light transmittance (τ≈0.88), which is critical given the low winter solar radiation. The brief explicitly requires at least two separate blocks; however, the plot is extremely small (25 × 20 m) and must accommodate year-round greenhouses with a mandatory minimum 6 m clearance between blocks per SP 107.13330 clause 4.4. Two blocks are arranged along the 25 m plot length with a 6 m fire-and-access gap between them, leaving each block with the minimum viable footprint. Important engineering caveat: the clay soil with groundwater depth of only 0.5 m (frost-heaving conditions) requires a pile foundation with perimeter drainage and enhanced waterproofing. It must be honestly noted that the 500 m² plot is physically incapable of accommodating the target yield of 2 000 t/year — even with the most intensive technology, the available growing area yields a small fraction of that figure; this constraint (ENG.5) cannot be resolved by design choices alone and must be escalated to the client for site re-selection or yield target revision.

**Total growing area:** 216 m²
**Complex footprint (with auxiliary):** 500.0 m²

### Greenhouse blocks

- **Block A** — 12.0 × 9.0 m (area 108 m²)
  - Heights: eave 2.4 m, ridge 5.5 m
  - Layout: block (multi-span), 1 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 14.0%
- **Block B** — 12.0 × 9.0 m (area 108 m²)
  - Heights: eave 2.4 m, ridge 5.5 m
  - Layout: block (multi-span), 1 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 14.0%

### Complex structural parameters

| Parameter | Value | SP Clause |
| --- | --- | --- |
| Plinth height | 0.4 m | 5.8 |
| Foundation rise above soil | 0.4 m | 5.9 |
| Territory fence height | 1.8 m | 4.16 |

### Auxiliary zones

- **Boiler house** — 16.0 m² (Heating plant and utility room)
- **Storage** — 12.0 m² (Storage for tools, fertilisers and consumables)
- **Staff facilities** — 8.0 m² (Changing rooms and sanitary facilities for personnel)
- **Nutrient mixing room** — 9.0 m² (Nutrient solution preparation and dosing pumps)

---

## 3. Engineering calculations

### 3.1. Heat supply

![Heat losses and peak load](charts/failed_v1/energy_balance.png)

- Design temperature difference: **55.0 °C**
- Envelope area: **450.0 m²**
- Overall heat transfer coefficient U: **6.4 W/(m²·K)**
- Transmission losses: **158.4 kW**
- Infiltration losses: **31.7 kW**
- **Peak heating load: 190.1 kW**
- Annual heat demand: **504.0 MWh**
- Coolant temperature: **95.0 °C** _(SP 7.9 ≤150)_
- Lower-zone heat share: **45.0%** _(SP 7.13 ≥40)_

### 3.2. Water supply

![Water demand](charts/failed_v1/water_demand.png)

- Daily demand: **0.97 m³/day**
- Peak hourly: **0.12 m³/h**
- Annual: **292 m³/year**
- Irrigation method: Drip (default)
- Reliability category: **II** _(SP 6.14)_
- Hose service radius: **40.0 m** _(SP 6.8 ≤45)_

### 3.3. Lighting and supplemental

![Light balance](charts/failed_v1/light_balance.png)

- Target DLI: **22.0 mol/m²/day**
- Natural winter DLI: **2.6 mol/m²/day**
- **Supplemental lighting required**: installed 266.2 W/m², consumption 208837 kWh/year
- Aisle floor illuminance: 8.0 lx _(SP 8.3 ≤10)_

### 3.4. Annual energy consumption

![Annual energy breakdown](charts/failed_v1/annual_energy.png)

### 3.5. Ventilation

- Summer target air changes per hour: **60.0 h⁻¹**
- Vent opening share of envelope: **20.0%** _(SP 7.18 ≥20, ≥10 north of 60°N)_
- Vent opening share of floor: 41.7%
- Forced ventilation: **not required**

### 3.6. Structural loads

- Snow load on roof: **835.0 kN** (γ=1.4)
- Wind load on walls: **48.0 kN** (q₁₀=1.0, q₂=0.6)
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

Rules checked: **36**

### ERROR — ENG.5-yield-feasibility

Площадь выращивания × норма культуры должна покрывать минимум 90% целевой урожайности из ТЗ. Иначе участок физически не вмещает заявленный объём продукции.

- Actual: `вмещает ~11 т/год (tomato @ 50.0 кг/м² × 216 м²)`
- Required: `>= 1800 т/год (90% от ТЗ 2000.0 т)`
- **Source** _(SP 107.13330, original Russian text)_: Инженерная проверка (не из СП): достижимость целевой урожайности


---

_Generated by agro-greenhouse-designer. Outputs are pre-design estimates and require validation by a qualified engineer before detailed documentation._