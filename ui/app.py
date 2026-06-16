"""Streamlit demo UI for agro-greenhouse-designer.

Three modes:
- Cached happy path (default) — replays demo_cache/default_run.json (no LLM cost).
- Cached refusal — replays failed_run.json with validator citations.
- Live — visitor pastes their own ANTHROPIC_API_KEY in the sidebar.

UI strings come from ui/i18n.py so the page works in RU and EN. Enum values
(year_round, tomato, ...) are *not* translated in storage — only their display
labels via format_func.
"""

from __future__ import annotations

import base64
import os
import re
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT))

from ui.i18n import enum_label, t  # noqa: E402

_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def _inline_images(md_text: str) -> str:
    """Inline relative-path PNGs as data URIs so st.markdown can render them."""
    def repl(m: re.Match[str]) -> str:
        alt, src = m.group(1), m.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        path = DOCS / src
        if not path.exists():
            return m.group(0)
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"![{alt}](data:image/png;base64,{b64})"

    return _IMG_RE.sub(repl, md_text)


def _load_cached(filename: str):
    """Load a cached GraphState — JSON preferred, .pkl as legacy fallback."""
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


# ─── Page config & language ───────────────────────────────────────────────────

st.set_page_config(
    page_title="Agro Greenhouse Designer",
    page_icon=":seedling:",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "lang" not in st.session_state:
    st.session_state.lang = "en"  # default to English for international audience

# ─── Header ───────────────────────────────────────────────────────────────────

st.title(t("title", st.session_state.lang))
st.caption(t("caption", st.session_state.lang))
st.markdown(t("intro", st.session_state.lang))


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    lang = st.radio(
        t("lang_label", st.session_state.lang),
        ["en", "ru"],
        index=["en", "ru"].index(st.session_state.lang),
        format_func=lambda x: {"en": "English", "ru": "Русский"}[x],
        horizontal=True,
    )
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()
    L = st.session_state.lang

    st.divider()
    st.header(t("mode_header", L))
    mode_options = [
        t("mode_normal", L),
        t("mode_failed", L),
        t("mode_live", L),
    ]
    mode = st.radio(t("mode_source", L), mode_options, index=0)

    live_key: str | None = None
    if mode == t("mode_live", L):
        live_key = st.text_input(t("api_key_label", L), type="password")
        if live_key:
            os.environ["ANTHROPIC_API_KEY"] = live_key
        st.caption(t("api_key_caption", L))
        if st.button(t("clear_key_button", L), use_container_width=True):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            live_key = None
            st.success(t("clear_key_success", L))
            st.rerun()

    st.divider()
    st.markdown(f"**{t('about_header', L)}**\n\n{t('about_body', L)}")


# ─── Cached modes ─────────────────────────────────────────────────────────────

if mode == t("mode_normal", L):
    st.success(t("demo_normal_banner", L))
    state = _load_cached(f"default_run.{L}.json")
    if state is None:
        st.error(t("cache_not_found", L))
    else:
        st.subheader(t("report_subheader", L))
        st.markdown(_inline_images(state.report_markdown), unsafe_allow_html=True)
        with st.expander(t("state_expander", L)):
            st.code(state.model_dump_json(indent=2, exclude={"messages"}))

elif mode == t("mode_failed", L):
    st.warning(t("demo_failed_banner", L))
    state = _load_cached(f"failed_run.{L}.json")
    if state is None:
        st.error(t("cache_failed_not_found", L))
    else:
        st.subheader(t("report_subheader_failed", L))
        st.markdown(_inline_images(state.report_markdown), unsafe_allow_html=True)
        with st.expander(t("issues_expander", L)):
            for issue in state.validation.issues:
                src = issue.sp_citation or "—"
                st.markdown(
                    f"**{issue.severity.value.upper()} — {issue.rule_id}**\n"
                    f"{issue.message}\n\n"
                    f"_{t('issue_source_label', L)}_ {src}"
                )


# ─── Live mode ────────────────────────────────────────────────────────────────

else:
    if not live_key:
        st.info(t("live_key_required", L))
        st.stop()

    from src.rag.climate_lookup import available_regions
    from src.schemas.project import (
        CropType,
        GreenhouseType,
        ProjectBrief,
        SiteParameters,
        SoilType,
    )

    st.header(t("brief_header", L))
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input(t("project_name", L), t("project_name_default", L))
        gh_type = st.selectbox(
            t("greenhouse_type", L),
            [t.value for t in GreenhouseType],
            index=0,
            format_func=lambda v: enum_label(v, L),
        )
        crop = st.selectbox(
            t("crop", L),
            [c.value for c in CropType],
            index=0,
            format_func=lambda v: enum_label(v, L),
        )
        yield_t = st.number_input(t("yield_t_year", L), 1.0, value=500.0, step=10.0)

    with col2:
        region = st.selectbox(t("region", L), available_regions(), index=0)
        plot_len = st.number_input(t("plot_length", L), 10, value=200, step=10)
        plot_w = st.number_input(t("plot_width", L), 10, value=100, step=10)
        plot_area = float(plot_len) * float(plot_w)
        st.metric(t("plot_area", L), f"{plot_area:,.0f} м²".replace(",", " "))
        soil = st.selectbox(
            t("soil", L),
            [s.value for s in SoilType],
            index=1,
            format_func=lambda v: enum_label(v, L),
        )

    if st.button(t("run_button", L), type="primary", use_container_width=True):
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

        with st.spinner(t("spinner_text", L)):
            raw = graph.invoke({"brief": brief, "lang": L}, {"recursion_limit": 25})
            state = GraphState(**{k: v for k, v in raw.items() if k != "messages"})

        st.success(t("done_iterations", L, n=state.iteration))
        st.subheader(t("report_subheader", L))
        st.markdown(_inline_images(state.report_markdown), unsafe_allow_html=True)
        with st.expander(t("state_label", L)):
            st.code(state.model_dump_json(indent=2, exclude={"messages"}))
