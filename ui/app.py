"""Streamlit demo UI for the agro-greenhouse-designer.

Two modes:
  - "Демо-режим" — replays a pre-recorded GraphState from demo_cache/
                   (no LLM cost, works without an API key)
  - "Свой ключ"  — user pastes their own ANTHROPIC_API_KEY into the sidebar
                   and runs the graph live
"""

from __future__ import annotations

import json
import os
import pickle
import sys
from pathlib import Path

import streamlit as st

# Make src importable when run via `streamlit run ui/app.py`
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.rag.climate_lookup import available_regions  # noqa: E402
from src.schemas.project import (  # noqa: E402
    CropType,
    GreenhouseType,
    ProjectBrief,
    SiteParameters,
    SoilType,
)

st.set_page_config(
    page_title="Agro Greenhouse Designer",
    page_icon=":seedling:",
    layout="wide",
)

st.title("Agro Greenhouse Designer")
st.caption(
    "Мультиагентная система предпроектной разработки тепличных комплексов. "
    "Валидация по СП 107.13330 «Теплицы и парники»."
)

# --- Sidebar: mode + key
with st.sidebar:
    st.header("Режим работы")
    mode = st.radio(
        "Источник ответов",
        ["Демо-режим (бесплатно)", "Свой ANTHROPIC_API_KEY"],
        index=0,
    )
    if mode == "Свой ANTHROPIC_API_KEY":
        api_key = st.text_input("API key", type="password")
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

    st.divider()
    st.markdown(
        "**О проекте:** портфолио-демо, иллюстрирующее паттерн "
        "*LLM-агенты + детерминированные расчёты + RAG по нормативам*."
    )

# --- Form: project brief
st.header("ТЗ на проектирование")
col1, col2 = st.columns(2)
with col1:
    project_name = st.text_input("Название проекта", "Тепличный комплекс «Заря»")
    greenhouse_type = st.selectbox(
        "Тип теплицы",
        [t.value for t in GreenhouseType],
        index=0,
    )
    target_crop = st.selectbox(
        "Культура",
        [c.value for c in CropType],
        index=0,
    )
    target_yield_t = st.number_input("Целевая урожайность, т/год", min_value=1.0, value=500.0, step=10.0)
    budget = st.number_input("Бюджет, млн руб (опц.)", min_value=0.0, value=0.0, step=10.0)

with col2:
    region = st.selectbox("Регион", available_regions(), index=0)
    plot_area = st.number_input("Площадь участка, м²", min_value=100, value=20000, step=100)
    plot_length = st.number_input("Длина участка, м", min_value=10, value=200, step=10)
    plot_width = st.number_input("Ширина участка, м", min_value=10, value=100, step=10)
    soil_type = st.selectbox("Грунт", [t.value for t in SoilType], index=1)

notes = st.text_area("Дополнительные требования / замечания", "")

run = st.button("Запустить проектирование", type="primary", use_container_width=True)

# --- Run
if run:
    brief = ProjectBrief(
        project_name=project_name,
        greenhouse_type=GreenhouseType(greenhouse_type),
        target_crop=CropType(target_crop),
        target_annual_yield_t=target_yield_t,
        site=SiteParameters(
            region=region,
            plot_area_m2=float(plot_area),
            plot_length_m=float(plot_length),
            plot_width_m=float(plot_width),
            soil_type=SoilType(soil_type),
        ),
        budget_rub=budget * 1_000_000 if budget else None,
        notes=notes,
    )

    if mode == "Демо-режим (бесплатно)":
        cache_path = ROOT / "demo_cache" / "default_run.pkl"
        if not cache_path.exists():
            st.error(
                "Демо-кэш не найден. Запустите `python scripts/build_demo_cache.py` "
                "однократно — это запишет прогон агентов на диск."
            )
        else:
            with cache_path.open("rb") as fh:
                final_state = pickle.load(fh)
            st.success("Запуск из кэша. LLM не вызывались.")
            st.subheader("Итоговый отчёт")
            st.markdown(final_state.report_markdown)
            with st.expander("Сырое состояние графа (JSON)"):
                st.code(final_state.model_dump_json(indent=2, exclude={"messages"}))
    else:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Введите ANTHROPIC_API_KEY в сайдбаре.")
        else:
            from src.graph import graph

            with st.spinner("Агенты работают..."):
                result = graph.invoke({"brief": brief})
            final_state = result if isinstance(result, dict) else result
            st.success("Готово.")
            st.subheader("Итоговый отчёт")
            st.markdown(final_state.get("report_markdown", "_(пусто)_"))
            with st.expander("Сырое состояние"):
                st.code(json.dumps({k: str(v)[:500] for k, v in final_state.items()}, indent=2, ensure_ascii=False))
