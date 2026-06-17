# Pre-design solution: Тепличный комплекс «Заря»

**Region:** Краснодарский край
**Greenhouse type:** year-round
**Crop:** tomato
**Target yield:** 500.0 t/year
**Generated:** 2026-06-17 04:02

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

**Rationale:** A year-round multi-span block-type greenhouse complex is selected to maximise usable growing area on a rectangular 200 × 100 m plot while maintaining efficient heating and structural economy. Glass cladding (τ ≈ 0.88) is chosen over polycarbonate or film because tomato requires the highest possible winter light transmission, critical at a Krasnodar latitude with only 3.8 MJ/m²/day solar radiation in winter. Two parallel blocks oriented along the plot length are arranged side by side across the width, with a service corridor gap between them; this layout keeps the footprint compact while allowing independent climate zones. Loam soil with a groundwater depth of 3.0 m (above the 2 m threshold) calls for strip foundations at 1 m embedment with waterproofing, but no perimeter drainage is required at this GWD. The trellis tomato culture demands a ridge height well above 5.5 m, so both blocks are designed with generous eave and ridge heights to accommodate overhead crop wires and internal machinery.

**Total growing area:** 10368 m²
**Complex footprint (with auxiliary):** 10368.0 m²

### Greenhouse blocks

- **Block A** — 96.0 × 54.0 m (area 5184 m²)
  - Heights: eave 4.0 m, ridge 6.0 m
  - Layout: block (multi-span), 6 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 13.0%
- **Block B** — 96.0 × 54.0 m (area 5184 m²)
  - Heights: eave 4.0 m, ridge 6.0 m
  - Layout: block (multi-span), 6 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 13.0%

### Complex structural parameters

| Parameter | Value | SP Clause |
| --- | --- | --- |
| Plinth height | 0.4 m | 5.8 |
| Foundation rise above soil | 0.4 m | 5.9 |
| Territory fence height | 1.8 m | 4.16 |

### Auxiliary zones

- **Boiler house** — 120.0 m² (Heating plant and hot-water distribution for both blocks)
- **Utility building** — 80.0 m² (Staff facilities, storage, and crop-handling area)
- **Irrigation pump room** — 40.0 m² (Drip-irrigation mixing and pumping station)
- **Guard post** — 20.0 m² (Security checkpoint at main entrance)

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

- Actual: `2.507716049382716`
- Required: `[5.0, 30.0]`
- **Source** _(SP 107.13330, original Russian text)_: Инженерная проверка (не из СП): обоснованная доля подсобок


---

_Generated by agro-greenhouse-designer. Outputs are pre-design estimates and require validation by a qualified engineer before detailed documentation._