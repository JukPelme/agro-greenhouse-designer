# Pre-design solution: Тепличный комплекс «Заря»

**Region:** Краснодарский край
**Greenhouse type:** year-round
**Crop:** tomato
**Target yield:** 500.0 t/year
**Generated:** 2026-06-17 06:34

---

## 1. Site inputs and analysis

Target yield per plot area: 25.0 kg/m²/year

**Climate parameters (per Russian SP 131.13330):**

| Parameter | Value |
| --- | --- |
| Design winter temperature (t5) | -19.0 °C |
| Design summer temperature | 29.4 °C |
| Heating degree-days | 2510.0 |
| Heating period | 149 days |
| Snow load | 1.0 kPa |
| Wind load | 0.38 kPa |
| Solar radiation (winter) | 3.8 MJ/m²/day |

---

## 2. Design solution (variant v1)

**Rationale:** Year-round glass greenhouse complex for trellis tomato production in the Krasnodar region. Glass covering was chosen for its superior light transmittance (τ ≈ 0.88), which is critical for high-yield tomato cultivation during short winter days in the southern climate. A multi-span block layout is adopted to maximise the usable growing area within the 200 × 100 m plot while maintaining the structural rigidity required for year-round operation with full heating and supplemental lighting. Ridge height is set to 6.0 m to accommodate long trellis culture and overhead infrastructure (heating pipes, lighting bars, monorail). Soil type is loam with groundwater at 3.0 m depth, which is above the frost-heaving threshold, so a conventional strip foundation (depth 1.0 m) with standard waterproofing is recommended. The two main growing blocks are arranged along the plot length with a service road between them, and a full auxiliary zone (boiler house, storage, packaging, staff, admin, nutrient mixing) is grouped at one gable end.

**Total growing area:** 10368 m²
**Complex footprint (with auxiliary):** 20000.0 m²

### Greenhouse blocks

- **Block A** — 96.0 × 54.0 m (area 5184 m²)
  - Heights: eave 4.0 m, ridge 6.0 m
  - Layout: block (multi-span), 6 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 14.0%
- **Block B** — 96.0 × 54.0 m (area 5184 m²)
  - Heights: eave 4.0 m, ridge 6.0 m
  - Layout: block (multi-span), 6 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 14.0%

### Complex structural parameters

| Parameter | Value | SP Clause |
| --- | --- | --- |
| Plinth height | 0.4 m | 5.8 |
| Foundation rise above soil | 0.4 m | 5.9 |
| Territory fence height | 1.8 m | 4.16 |

### Auxiliary zones

- **Boiler house** — 120.0 m² (Gas-independent electric boiler plant and heat distribution for year-round heating)
- **Tool and fertiliser storage** — 80.0 m² (Storage of tools, consumables and mineral fertilisers)
- **Packaging and sorting hall** — 100.0 m² (Post-harvest handling, grading and packaging of tomato produce)
- **Staff facilities** — 60.0 m² (Locker rooms, showers, canteen and rest area for personnel)
- **Administrative building** — 80.0 m² (Offices, meeting room and security post)
- **Nutrient mixing and pumping room** — 60.0 m² (Preparation and distribution of nutrient solution for drip irrigation)

---

## 3. Engineering calculations

### 3.1. Heat supply

![Heat losses and peak load](charts/v1/energy_balance.png)

- Design temperature difference: **37.0 °C**
- Envelope area: **14323.2 m²**
- Overall heat transfer coefficient U: **6.4 W/(m²·K)**
- Transmission losses: **3391.7 kW**
- Infiltration losses: **678.3 kW**
- **Peak heating load: 4070.1 kW**
- Annual heat demand: **6626.5 MWh**
- Coolant temperature: **95.0 °C** _(SP 7.9 ≤150)_
- Lower-zone heat share: **45.0%** _(SP 7.13 ≥40)_

### 3.2. Water supply

![Water demand](charts/v1/water_demand.png)

- Daily demand: **46.66 m³/day**
- Peak hourly: **5.83 m³/h**
- Annual: **13997 m³/year**
- Irrigation method: Drip (default)
- Reliability category: **II** _(SP 6.14)_
- Hose service radius: **40.0 m** _(SP 6.8 ≤45)_

### 3.3. Lighting and supplemental

![Light balance](charts/v1/light_balance.png)

- Target DLI: **22.0 mol/m²/day**
- Natural winter DLI: **6.7 mol/m²/day**
- **Supplemental lighting required**: installed 210.5 W/m², consumption 5203983 kWh/year
- Aisle floor illuminance: 8.0 lx _(SP 8.3 ≤10)_

### 3.4. Annual energy consumption

![Annual energy breakdown](charts/v1/annual_energy.png)

### 3.5. Ventilation

- Summer target air changes per hour: **60.0 h⁻¹**
- Vent opening share of envelope: **20.0%** _(SP 7.18 ≥20, ≥10 north of 60°N)_
- Vent opening share of floor: 27.6%
- Forced ventilation: **not required**

### 3.6. Structural loads

- Snow load on roof: **16692.0 kN** (γ=1.4)
- Wind load on walls: **730.0 kN** (q₁₀=1.0, q₂=0.6)
- Trellis load: 150.0 N/m² (γ=1.3)

_Overload factors and normative values per SP 107.13330 clause 5.14._

### 3.7. Geotechnical conditions and foundation

- Foundation soil: **loam**
- Groundwater depth: **3.0 m**
- Recommended foundation type: **strip**
- Minimum embedment depth: **1.0 m**
- Perimeter drainage: **not required**
- Waterproofing grade: **standard**

> Loam — strip foundation with waterproofing; drainage if groundwater table is high.

_Preliminary recommendations. A proper engineering-geological survey per SP 47.13330 is required for working documentation._

---

## 4. SP 107.13330 compliance check

Rules checked: **34**

### WARNING — ENG.2-aux-share

Подсобные зоны должны занимать 5–30% площади комплекса. Меньше — нехватка для обслуживания; больше — неэффективное использование участка.

- Actual: `2.5`
- Required: `[5.0, 30.0]`
- **Source** _(SP 107.13330, original Russian text)_: Инженерная проверка (не из СП): обоснованная доля подсобок


---

_Generated by agro-greenhouse-designer. Outputs are pre-design estimates and require validation by a qualified engineer before detailed documentation._