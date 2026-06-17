# Pre-design solution: Тепличный комплекс «Заря»

**Region:** Краснодарский край
**Greenhouse type:** year-round
**Crop:** tomato
**Target yield:** 500.0 t/year
**Generated:** 2026-06-17 05:43

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

**Rationale:** A year-round multi-span block-type greenhouse complex is selected for tomato trellis cultivation, which requires a ridge height well above 5.5 m to accommodate tall-growing plants and overhead irrigation infrastructure. Glass cladding was chosen for its superior light transmittance, which is critical in a tomato production facility targeting high annual yields — it maximises both direct and diffuse solar radiation reaching the crop canopy, especially important during the shorter winter days in the Krasnodar region. The layout consists of two parallel greenhouse blocks arranged along the 200 m plot length, each with ten 9 m spans across the 100 m plot width, providing the necessary growing area within the available footprint while preserving a clear access corridor between blocks and around the perimeter. The loam soil with a groundwater depth of 3.0 m is suitable for a conventional strip foundation at approximately 1 m embedment depth, with waterproofing applied as a precaution; no perimeter drainage is required at this groundwater level. Auxiliary zones are positioned at one end of the complex, grouped for operational efficiency, and collectively exceed 7% of the total footprint as required.

**Total growing area:** 17280 m²
**Complex footprint (with auxiliary):** 20000.0 m²

### Greenhouse blocks

- **Block A** — 96.0 × 90.0 m (area 8640 m²)
  - Heights: eave 4.0 m, ridge 6.0 m
  - Layout: block (multi-span), 10 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 12.0%
- **Block B** — 96.0 × 90.0 m (area 8640 m²)
  - Heights: eave 4.0 m, ridge 6.0 m
  - Layout: block (multi-span), 10 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 12.0%

### Complex structural parameters

| Parameter | Value | SP Clause |
| --- | --- | --- |
| Plinth height | 0.4 m | 5.8 |
| Foundation rise above soil | 0.4 m | 5.9 |
| Territory fence height | 1.8 m | 4.16 |

### Auxiliary zones

- **Boiler house** — 180.0 m² (Heating plant and utility room; electric boiler equipment (no gas supply on site))
- **Tool and fertiliser storage** — 150.0 m² (Storage of agricultural tools, fertilisers and plant-protection agents)
- **Nutrient mixing and pumping room** — 120.0 m² (Preparation and distribution of nutrient solutions for hydroponic/drip irrigation)
- **Packaging and sorting hall** — 200.0 m² (Sorting, grading, packaging and pre-cooling of harvested tomatoes)
- **Staff facilities** — 100.0 m² (Changing rooms, sanitary facilities, rest room and first-aid post for personnel)
- **Administrative building** — 150.0 m² (Offices, meeting room and control room for complex management (complex >5000 m²))

---

## 3. Engineering calculations

### 3.1. Heat supply

![Heat losses and peak load](charts/v1/energy_balance.png)

- Design temperature difference: **37.0 °C**
- Envelope area: **22848.0 m²**
- Overall heat transfer coefficient U: **6.4 W/(m²·K)**
- Transmission losses: **5410.4 kW**
- Infiltration losses: **1082.1 kW**
- **Peak heating load: 6492.5 kW**
- Annual heat demand: **10570.5 MWh**
- Coolant temperature: **95.0 °C** _(SP 7.9 ≤150)_
- Lower-zone heat share: **45.0%** _(SP 7.13 ≥40)_

### 3.2. Water supply

![Water demand](charts/v1/water_demand.png)

- Daily demand: **77.76 m³/day**
- Peak hourly: **9.72 m³/h**
- Annual: **23328 m³/year**
- Irrigation method: Drip (default)
- Reliability category: **II** _(SP 6.14)_
- Hose service radius: **40.0 m** _(SP 6.8 ≤45)_

### 3.3. Lighting and supplemental

![Light balance](charts/v1/light_balance.png)

- Target DLI: **22.0 mol/m²/day**
- Natural winter DLI: **6.7 mol/m²/day**
- **Supplemental lighting required**: installed 210.5 W/m², consumption 8673305 kWh/year
- Aisle floor illuminance: 8.0 lx _(SP 8.3 ≤10)_

### 3.4. Annual energy consumption

![Annual energy breakdown](charts/v1/annual_energy.png)

### 3.5. Ventilation

- Summer target air changes per hour: **60.0 h⁻¹**
- Vent opening share of envelope: **20.0%** _(SP 7.18 ≥20, ≥10 north of 60°N)_
- Vent opening share of floor: 26.4%
- Forced ventilation: **not required**

### 3.6. Structural loads

- Snow load on roof: **27821.0 kN** (γ=1.4)
- Wind load on walls: **905.0 kN** (q₁₀=1.0, q₂=0.6)
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

- Actual: `4.5`
- Required: `[5.0, 30.0]`
- **Source** _(SP 107.13330, original Russian text)_: Инженерная проверка (не из СП): обоснованная доля подсобок


---

_Generated by agro-greenhouse-designer. Outputs are pre-design estimates and require validation by a qualified engineer before detailed documentation._