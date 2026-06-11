"""Designer agent: generates a design variant using an LLM bound to typed output.

The prompt explicitly references the СП 107.13330 limits the design must honor.
The Validator still enforces these — the prompt is just front-loaded guidance
to reduce the number of iterations.
"""

from __future__ import annotations

from ..schemas.design import DesignVariant
from ..schemas.state import GraphState

SYSTEM_PROMPT = """Ты — главный архитектор тепличных комплексов в проектной организации.

На входе ТЗ, климат региона, замечания аналитика и (опционально) замечания
валидатора с предыдущей итерации.

Твоя задача — предложить КОНКРЕТНУЮ компоновку комплекса с учётом
СП 107.13330 «Теплицы и парники»:

ГЕОМЕТРИЯ (п. 5.5, 5.8, 5.10, 5.11):
- Длина блока кратна 6 м
- Пролёт однопролётной (angar) теплицы ≤ 21 м; многопролётной (block) ≤ 9 м
- Высота от пола до низа конструкций ≥ 2,4 м (=eave_height_m)
- Цоколь (plinth_height_m) ≥ 0,3 м
- Превышение фундамента над почвой (foundation_above_soil_m) ≥ 0,3 м
- Уклон кровли: ≥45% для прямолинейных скатов (straight), ≥20% для криволинейных (arched)
- Доля светонепроницаемых конструкций (opaque_share_pct):
  ≤15% при стекле, ≤10% при плёнке

МАТЕРИАЛЫ (п. 5.23):
- Толщина стекла ≤ 4 мм (3 мм при шаге шпросов 500 мм, 4 мм при 750 мм)
- Светопропускание стекла τ ≈ 0.88, поликарбоната ≈ 0.78, плёнки двойной ≈ 0.85

ТЕРРИТОРИЯ (п. 4.4, 4.6, 4.16):
- ОБЯЗАТЕЛЬНО заполняй "block_spacing_m" в DesignVariant: реальный минимальный
  разрыв между блоками в твоей компоновке (м). Считай по доступной длине
  участка минус сумма ширин блоков, делённое на число промежутков.
  Если блок один — оставь None.
- Расстояние между зимними теплицами ≥ 6 м, между сезонными ≥ 1,5 м (п. 4.4)
- Высота ограждения территории (fence_height_m) ≥ 1,6 м (п. 4.16)
- Если рядом животноводческие фермы — выдержать разрывы по п. 4.6 (≥150 м)

КУЛЬТУРЫ С ПОДВЯЗКОЙ (томат, огурец):
- Высота в коньке для year_round ≥ 5,5 м (для шпалеры)
- Цвет ограждения светлый, чтобы максимизировать освещённость

Если предыдущая валидация выдала ERROR — ОБЯЗАТЕЛЬНО устрани именно эти
замечания. Не предлагай тот же вариант повторно.

ЖЁСТКИЕ ПРАВИЛА ДЛЯ "rationale":
- НЕ считай в тексте обоснования (никаких "2 × 96×54 = ..."). Все числа
  Engineer посчитает дальше — текст обоснования объясняет ВЫБОР, а не
  выполняет арифметику. Если LLM посчитает в тексте, он почти всегда
  ошибётся — а это самое видное место отчёта.
- НЕ используй внутренние имена полей: пиши "ширина пролёта" вместо
  "span_width_m", "доля светонепроницаемых конструкций" вместо
  "opaque_share_pct", "высота карниза" вместо "eave_height_m".
- Объясни в 3-5 предложениях: какой тип теплицы выбран и почему, какой
  материал ограждения и почему, чем оправдана компоновка (число блоков,
  пролёты), как это укладывается в участок. Без цифр сравнений — только
  качественное обоснование.

Возвращай строго по схеме DesignVariant с заполненными новыми полями.
"""


def designer_node(state: GraphState) -> dict:
    from ..llm import get_structured_llm

    if state.climate is None:
        return {"errors": ["Designer не может работать без климата."]}

    llm = get_structured_llm(DesignVariant)

    prior_issues = ""
    if state.validation and state.validation.issues:
        prior_issues = "\n\n--- Замечания валидатора с прошлой итерации ---\n"
        for issue in state.validation.issues:
            prior_issues += f"[{issue.severity}] {issue.rule_id}: {issue.message}\n"
        prior_issues += "Переделай вариант с учётом этих замечаний.\n"

    human_prompt = f"""ТЗ:
{state.brief.model_dump_json(indent=2)}

Климат региона:
{state.climate.model_dump_json(indent=2)}

Замечания аналитика:
{state.analyst_notes}
{prior_issues}

Предложи вариант №{state.iteration + 1}. variant_id = "v{state.iteration + 1}"
"""

    design: DesignVariant = llm.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": human_prompt},
        ]
    )

    return {
        "design": design,
        "iteration": state.iteration + 1,
    }
