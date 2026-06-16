# Pre-design solution: Тестовый отказ системы

**Region:** Новосибирская область
**Greenhouse type:** year_round
**Crop:** tomato
**Target yield:** 2000.0 t/year
**Generated:** 2026-06-16 09:15

---

## 1. Site inputs and analysis

Целевая урожайность относительно участка: 4000.0 кг/м²/год
⚠ Целевая урожайность очень высокая — потребуется интенсивная технология.

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

**Rationale:** Участок крайне мал для заявленной урожайности в 2000 т/год — это физически недостижимо на площади 500 м², даже при самых интенсивных технологиях. Тем не менее, в рамках ТЗ предложена максимально плотная компоновка из двух блочных многопролётных теплиц с полным использованием пятна застройки. Выбрано стеклянное ограждение как наилучшее по светопропусканию для томата в суровом климате Новосибирской области, где зимнее освещение критически мало. Высота в коньке обеспечивает шпалерное ведение томата. Фундамент — свайный с периметральным дренажом, поскольку грунт глинистый с высоким уровнем грунтовых вод, что требует защиты от морозного пучения. Два блока разделены минимальным технологическим разрывом согласно требованиям ТЗ, вспомогательные зоны размещены в торцах блоков для соответствия нормативной доле подсобных помещений.

**Total growing area:** 324 m²
**Complex footprint (with auxiliary):** 324.0 m²

### Greenhouse blocks

- **Блок А — Томат (основной)** — 18.0 × 9.0 m (area 162 m²)
  - Heights: eave 4.0 m, ridge 5.5 m
  - Layout: block, 1 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 12.0%
- **Блок Б — Томат (дополнительный)** — 18.0 × 9.0 m (area 162 m²)
  - Heights: eave 4.0 m, ridge 5.5 m
  - Layout: block, 1 spans of 9.0 m
  - Roof: straight, slope 45.0%
  - Covering: glass (τ=0.88), glass 4.0 mm  - Opaque structures share: 12.0%

### Complex structural parameters

| Parameter | Value | SP Clause |
| --- | --- | --- |
| Plinth height | 0.4 m | 5.8 |
| Foundation rise above soil | 0.4 m | 5.9 |
| Territory fence height | 1.8 m | 4.16 |

### Auxiliary zones

- **Технический узел Блока А** — 18.0 m² (Котельная, щитовая, хранение СЗР)
- **Технический узел Блока Б** — 18.0 m² (Система климат-контроля, склад инвентаря)
- **Санитарно-бытовой блок** — 20.0 m² (Комната персонала, санузлы, раздевалка)

---

## 3. Engineering calculations

### 3.1. Heat supply

![Heat losses and peak load](charts/failed_v1/energy_balance.png)

- Design temperature difference: **55.0 °C**
- Envelope area: **804.6 m²**
- Overall heat transfer coefficient U: **6.4 W/(m²·K)**
- Transmission losses: **283.2 kW**
- Infiltration losses: **56.6 kW**
- **Peak heating load: 339.9 kW**
- Annual heat demand: **901.1 MWh**
- Coolant temperature: **95.0 °C** _(SP 7.9 ≤150)_
- Lower-zone heat share: **45.0%** _(SP 7.13 ≥40)_

### 3.2. Water supply

![Water demand](charts/failed_v1/water_demand.png)

- Daily demand: **1.46 m³/day**
- Peak hourly: **0.18 m³/h**
- Annual: **437 m³/year**
- Irrigation method: Капельное (по умолчанию)
- Reliability category: **II** _(SP 6.14)_
- Hose service radius: **40.0 m** _(SP 6.8 ≤45)_

### 3.3. Lighting and supplemental

![Light balance](charts/failed_v1/light_balance.png)

- Target DLI: **22.0 mol/m²/day**
- Natural winter DLI: **2.6 mol/m²/day**
- **Supplemental lighting required**: installed 266.2 W/m², consumption 313256 kWh/year
- Aisle floor illuminance: 8.0 lx _(SP 8.3 ≤10)_

### 3.4. Annual energy consumption

![Annual energy breakdown](charts/failed_v1/annual_energy.png)

### 3.5. Ventilation

- Summer target air changes per hour: **60.0 h⁻¹**
- Vent opening share of envelope: **20.0%** _(SP 7.18 ≥20, ≥10 north of 60°N)_
- Vent opening share of floor: 49.7%
- Forced ventilation: **not required**

### 3.6. Structural loads

- Snow load on roof: **1252.0 kN** (γ=1.4)
- Wind load on walls: **104.0 kN** (q₁₀=1.0, q₂=0.6)
- Trellis load: 150.0 N/m² (γ=1.3)

_Overload factors and normative values per SP 107.13330 clause 5.14._

### 3.7. Geotechnical conditions and foundation

- Foundation soil: **clay**
- Groundwater depth: **0.5 m**
- Recommended foundation type: **pile**
- Minimum embedment depth: **3.0 m**
- Perimeter drainage: **required**
- Waterproofing grade: **enhanced**

> Глина с высоким УГВ — пучинистый грунт. Свайный фундамент с заглублением ниже глубины промерзания; усиленная гидроизоляция и обязательный периметральный дренаж.

_Preliminary recommendations. A proper engineering-geological survey per SP 47.13330 is required for working documentation._

---

## 4. SP 107.13330 compliance check

Rules checked: **36**

### ERROR — SP107.4.4-year-round

Расстояние (разрыв) между зимними теплицами в составе ТОК/РОТК — не менее 6 м для проезда техники.

- Actual: `2.0`
- Required: `6.0`
- **Source** _(SP 107.13330, original Russian text)_: СП 107.13330 п. 4.4:
> «Расстояния между зимними теплицами, входящими в состав ТОК и РОТК, 
определяются шириной проездов и составляют не менее 6 м, между сезонными 
теплицами - не менее 1,5 м.»

### ERROR — ENG.5-yield-feasibility

Площадь выращивания × норма культуры должна покрывать минимум 90% целевой урожайности из ТЗ. Иначе участок физически не вмещает заявленный объём продукции.

- Actual: `вмещает ~16 т/год (tomato @ 50.0 кг/м² × 324 м²)`
- Required: `>= 1800 т/год (90% от ТЗ 2000.0 т)`
- **Source** _(SP 107.13330, original Russian text)_: Инженерная проверка (не из СП): достижимость целевой урожайности


---

_Generated by agro-greenhouse-designer. Outputs are pre-design estimates and require validation by a qualified engineer before detailed documentation._