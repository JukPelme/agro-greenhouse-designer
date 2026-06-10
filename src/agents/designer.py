"""Designer agent: generates a design variant using an LLM bound to typed output.

Inputs:  GraphState.brief, GraphState.climate, GraphState.analyst_notes,
         optional previous GraphState.validation (for iterative refinement)
Outputs: GraphState.design
"""

from __future__ import annotations

from ..schemas.design import DesignVariant
from ..schemas.state import GraphState


SYSTEM_PROMPT = """Ты — главный архитектор тепличных комплексов в проектной организации.

На входе ТЗ, климат региона, замечания аналитика и (опционально) замечания валидатора
с предыдущей итерации. Твоя задача — предложить КОНКРЕТНУЮ компоновку комплекса:
один или несколько блоков теплиц (длина × ширина × высоты), материал ограждения,
вспомогательные зоны.

Правила:
- Геометрия блока: длина кратна 6 м, ширина из ряда 9.6 / 12 / 16 / 19.2 / 25.6 м
- Высота в коньке для year_round: не менее 5.5 м (для культур с подвязкой)
- Светопропускание: glass 0.88, polycarbonate 0.78, polyethylene 0.85 (двойной)
- Не более 75% площади участка под блоки — остальное под подсобки, дороги, разрывы

Если предыдущая валидация выдала ERROR — ОБЯЗАТЕЛЬНО учти замечания и переделай.
Возвращай строго по схеме DesignVariant.
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
