"""Streamlit demo UI for agro-greenhouse-designer.

Designed to run cleanly on Streamlit Cloud:
- Demo mode replays a cached GraphState from demo_cache/*.json — no LLM cost.
- Failed-case mode replays a refusal scenario for the same reason.
- Live mode is gated behind a user-supplied API key in the sidebar.

We never call the LLM with the operator's key by default — visitor browses
the project on the operator's dime ONLY if they explicitly enable live mode.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"

import base64, re
_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

def _inline_images(md_text: str) -> str:
    """Replace relative image paths in markdown with base64 data URIs.

    Streamlit Cloud does not serve local files referenced by relative paths,
    so we encode each PNG inline so the rendered HTML carries the image data.
    """
    def repl(m):
        alt, src = m.group(1), m.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        path = DOCS / src
        if not path.exists():
            return m.group(0)
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"![{alt}](data:image/png;base64,{b64})"
    return _IMG_RE.sub(repl, md_text)

sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Agro Greenhouse Designer",
    page_icon=":seedling:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Header ───────────────────────────────────────────────────────────────────
st.title("Agro Greenhouse Designer")
st.caption(
    "Мультиагентная система предпроектной разработки тепличных комплексов. "
    "Валидация по СП 107.13330 «Теплицы и парники»."
)
st.markdown(
    "[Repo на GitHub](https://github.com/JukPelme/agro-greenhouse-designer) · "
    "Портфолио-проект, иллюстрирующий паттерн "
    "*LLM-агенты + детерминированные расчёты + RAG по нормативам*."
)

# ─── Sidebar: режим ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Режим работы")
    mode = st.radio(
        "Источник ответов",
        [
            "Готовый прогон — норма (без API-ключа)",
            "Готовый прогон — отказ (без API-ключа)",
            "Запустить вживую (нужен свой API-ключ)",
        ],
        index=0,
    )

    live_key: str | None = None
    if mode == "Запустить вживую (нужен свой API-ключ)":
        live_key = st.text_input("ANTHROPIC_API_KEY", type="password")
        if live_key:
            os.environ["ANTHROPIC_API_KEY"] = live_key
        st.caption(
            "Ключ остаётся в RAM сервера только во время сессии, не пишется "
            "на диск и не логируется. При перезагрузке страницы — стирается. "
            "Передаётся напрямую в Anthropic API через HTTPS. Платформа "
            "Streamlit Cloud видит его в памяти процесса как любой другой "
            "пользовательский ввод — для одноразового тестового запуска ок, "
            "для production-нагрузки используйте свой self-hosted деплой."
        )
        if st.button("Очистить ключ из сессии", use_container_width=True):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            live_key = None
            st.success("Ключ удалён из окружения.")
            st.rerun()

    st.divider()
    st.markdown(
        "**О проекте:**\n\n"
        "- 5 агентов LangGraph (Analyst → Designer → Engineer → Validator → Reporter)\n"
        "- Детерминированные расчёты на чистом Python\n"
        "- RAG по реальному PDF СП 107.13330\n"
        "- 4 теста pytest, ~1500 строк кода"
    )


def _load_cached(filename: str):
    """Load a cached GraphState — JSON preferred, .pkl as legacy fallback.

    JSON is more robust than pickle across schema migrations:
    extra fields are tolerated, missing ones get defaults, no class refs.
    """
    from src.schemas.state import GraphState

    json_path = ROOT / "demo_cache" / filename.replace(".pkl", ".json")
    if json_path.exists():
        return GraphState.model_validate_json(json_path.read_text(encoding="utf-8"))

    pkl_path = ROOT / "demo_cache" / filename.replace(".json", ".pkl")
    if pkl_path.exists():
        import pickle
        with pkl_path.open("rb") as fh:
            return pickle.load(fh)

    return None


# ─── Демо-режимы: просто проигрываем кэш ──────────────────────────────────────
if mode == "Готовый прогон — норма (без API-ключа)":
    st.success("Демо-режим: проигрывается заранее закэшированный прогон.")
    state = _load_cached("default_run.json")
    if state is None:
        st.error("Кэш не найден. Запустите `python scripts/build_demo_cache.py`.")
    else:
        st.subheader("Итоговый отчёт")
        st.markdown(_inline_images(state.report_markdown), unsafe_allow_html=True)
        with st.expander("State (JSON, без messages)"):
            st.code(state.model_dump_json(indent=2, exclude={"messages"}))

elif mode == "Готовый прогон — отказ (без API-ключа)":
    st.warning(
        "Демо-режим: ТЗ заведомо противоречиво — система должна указать на это, "
        "а не выдать правдоподобный-но-ложный результат."
    )
    state = _load_cached("failed_run.json")
    if state is None:
        st.error("Кэш не найден. Запустите `python scripts/build_failed_case.py`.")
    else:
        st.subheader("Итоговый отчёт (с замечаниями)")
        st.markdown(_inline_images(state.report_markdown), unsafe_allow_html=True)
        with st.expander("Все замечания валидатора"):
            for issue in state.validation.issues:
                st.markdown(
                    f"**{issue.severity.value.upper()} — {issue.rule_id}**\n"
                    f"{issue.message}\n\n"
                    f"_Источник:_ {issue.sp_citation or '—'}"
                )

# ─── Live mode: форма + вызов графа ───────────────────────────────────────────
else:
    if not live_key:
        st.info(
            "Введите свой ANTHROPIC_API_KEY в сайдбаре. Один прогон графа "
            "тратит ≈ 5 центов на Opus."
        )
        st.stop()

    from src.rag.climate_lookup import available_regions
    from src.schemas.project import (
        CropType,
        GreenhouseType,
        ProjectBrief,
        SiteParameters,
        SoilType,
    )

    st.header("ТЗ на проектирование")
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Название проекта", "Тепличный комплекс «Заря»")
        gh_type = st.selectbox("Тип теплицы", [t.value for t in GreenhouseType], index=0)
        crop = st.selectbox("Культура", [c.value for c in CropType], index=0)
        yield_t = st.number_input("Урожайность, т/год", 1.0, value=500.0, step=10.0)

    with col2:
        region = st.selectbox("Регион", available_regions(), index=0)
        plot_area = st.number_input("Площадь участка, м²", 100, value=20000, step=100)
        plot_len = st.number_input("Длина, м", 10, value=200, step=10)
        plot_w = st.number_input("Ширина, м", 10, value=100, step=10)
        soil = st.selectbox("Грунт", [t.value for t in SoilType], index=1)

    if st.button("Запустить проектирование", type="primary", use_container_width=True):
        brief = ProjectBrief(
            project_name=project_name,
            greenhouse_type=GreenhouseType(gh_type),
            target_crop=CropType(crop),
            target_annual_yield_t=yield_t,
            site=SiteParameters(
                region=region,
                plot_area_m2=float(plot_area),
                plot_length_m=float(plot_len),
                plot_width_m=float(plot_w),
                soil_type=SoilType(soil),
            ),
        )

        from src.graph import graph
        from src.schemas.state import GraphState

        with st.spinner("Агенты работают (Designer → Engineer → Validator → Reporter)..."):
            raw = graph.invoke({"brief": brief}, {"recursion_limit": 25})
            state = GraphState(**{k: v for k, v in raw.items() if k != "messages"})

        st.success(f"Готово. Итераций: {state.iteration}.")
        st.subheader("Итоговый отчёт")
        st.markdown(_inline_images(state.report_markdown), unsafe_allow_html=True)
        with st.expander("State"):
            st.code(state.model_dump_json(indent=2, exclude={"messages"}))
