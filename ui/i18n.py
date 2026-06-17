"""Simple two-language dictionary for the Streamlit UI.

We don't pull in babel/gettext — the surface is small enough that a plain
dict is clearer and ships with zero extra deps.

Enum *values* are NEVER translated (they go to JSON/rules.yaml as is) —
only their display labels via Streamlit's `format_func`.
"""

from __future__ import annotations

Lang = str  # "ru" | "en"

UI: dict[str, dict[Lang, str]] = {
    # Header / lead
    "title": {"ru": "Agro Greenhouse Designer", "en": "Agro Greenhouse Designer"},
    "caption": {
        "ru": "Мультиагентная система предпроектной разработки тепличных комплексов. "
              "Валидация по СП 107.13330 «Теплицы и парники».",
        "en": "Multi-agent system for greenhouse pre-design. "
              "Validates against Russian SP 107.13330 «Greenhouses and hotbeds».",
    },
    "intro": {
        "ru": "[Repo на GitHub](https://github.com/JukPelme/agro-greenhouse-designer) · "
              "Портфолио-проект, иллюстрирующий паттерн "
              "*LLM-агенты + детерминированные расчёты + RAG по нормативам*.",
        "en": "[Repo on GitHub](https://github.com/JukPelme/agro-greenhouse-designer) · "
              "Portfolio project illustrating the pattern "
              "*LLM agents + deterministic calculations + RAG over building codes*.",
    },

    # Sidebar
    "lang_label": {"ru": "Язык интерфейса", "en": "UI language"},
    "mode_header": {"ru": "Режим работы", "en": "Mode"},
    "mode_source": {"ru": "Источник ответов", "en": "Source"},
    "mode_normal": {
        "ru": "Готовый прогон — норма (без API-ключа)",
        "en": "Cached run — happy path (no API key)",
    },
    "mode_failed": {
        "ru": "Готовый прогон — отказ (без API-ключа)",
        "en": "Cached run — refusal case (no API key)",
    },
    "mode_live": {
        "ru": "Запустить вживую (нужен свой API-ключ)",
        "en": "Run live (bring your own API key)",
    },
    "api_key_label": {"ru": "ANTHROPIC_API_KEY", "en": "ANTHROPIC_API_KEY"},
    "api_key_caption": {
        "ru": "Ключ остаётся в RAM сервера только во время сессии, не пишется на диск "
              "и не логируется. При перезагрузке страницы — стирается. Передаётся "
              "напрямую в Anthropic API через HTTPS. Платформа Streamlit Cloud видит "
              "его в памяти процесса как любой другой пользовательский ввод — для "
              "одноразового тестового запуска ок, для production-нагрузки используйте "
              "свой self-hosted деплой.",
        "en": "The key stays in server RAM for the session only — not written to disk, "
              "not logged. Page reload wipes it. Sent directly to the Anthropic API over "
              "HTTPS. Streamlit Cloud sees it in process memory like any other user input "
              "— fine for a one-off test, use a self-hosted deployment for production.",
    },
    "clear_key_button": {"ru": "Очистить ключ из сессии", "en": "Clear key from session"},
    "clear_key_success": {"ru": "Ключ удалён из окружения.", "en": "Key removed from env."},
    "about_header": {"ru": "О проекте:", "en": "About:"},
    "about_body": {
        "ru": "- 5 агентов LangGraph (Analyst → Designer → Engineer → Validator → Reporter)\n"
              "- Детерминированные расчёты на чистом Python\n"
              "- RAG по реальному PDF СП 107.13330\n"
              "- 13 тестов pytest, ~1700 строк кода",
        "en": "- 5 LangGraph agents (Analyst → Designer → Engineer → Validator → Reporter)\n"
              "- Deterministic calculations in pure Python\n"
              "- RAG over the real SP 107.13330 PDF\n"
              "- 13 pytest tests, ~1700 lines of code",
    },

    # Demo banners
    "demo_normal_banner": {
        "ru": "Демо-режим: проигрывается заранее закэшированный прогон.",
        "en": "Demo mode: replaying a precomputed cached run.",
    },
    "demo_failed_banner": {
        "ru": "Демо-режим: ТЗ заведомо противоречиво — система должна указать на это, "
              "а не выдать правдоподобный-но-ложный результат.",
        "en": "Demo mode: the brief is deliberately infeasible — the system must say so "
              "instead of producing a plausible-but-false answer.",
    },
    "report_subheader": {"ru": "Итоговый отчёт", "en": "Final report"},
    "report_subheader_failed": {"ru": "Итоговый отчёт (с замечаниями)", "en": "Final report (with issues)"},
    "state_expander": {"ru": "State (JSON, без messages)", "en": "State (JSON, without messages)"},
    "issues_expander": {"ru": "Все замечания валидатора", "en": "All validator issues"},
    "cache_not_found": {
        "ru": "Кэш не найден. Запустите `python scripts/build_demo_cache.py`.",
        "en": "Cache not found. Run `python scripts/build_demo_cache.py`.",
    },
    "cache_failed_not_found": {
        "ru": "Кэш не найден. Запустите `python scripts/build_failed_case.py`.",
        "en": "Cache not found. Run `python scripts/build_failed_case.py`.",
    },
    "issue_source_label": {"ru": "Источник:", "en": "Source:"},

    # Live mode
    "live_key_required": {
        "ru": "Введите свой ANTHROPIC_API_KEY в сайдбаре. Один прогон графа тратит ≈ 5 центов на Opus.",
        "en": "Paste your ANTHROPIC_API_KEY in the sidebar. One graph run costs ≈ 5¢ on Opus.",
    },
    "brief_header": {"ru": "ТЗ на проектирование", "en": "Design brief"},
    "project_name": {"ru": "Название проекта", "en": "Project name"},
    "project_name_default": {"ru": "Тепличный комплекс «Заря»", "en": "Greenhouse complex \"Zarya\""},
    "greenhouse_type": {"ru": "Тип теплицы", "en": "Greenhouse type"},
    "crop": {"ru": "Культура", "en": "Crop"},
    "yield_t_year": {"ru": "Урожайность, т/год", "en": "Target yield, t/year"},
    "region": {"ru": "Регион", "en": "Region"},
    "plot_area": {"ru": "Площадь участка, м²", "en": "Plot area, m²"},
    "plot_length": {"ru": "Длина, м", "en": "Length, m"},
    "plot_width": {"ru": "Ширина, м", "en": "Width, m"},
    "soil": {"ru": "Грунт основания", "en": "Foundation soil"},
    "run_button": {"ru": "Запустить проектирование", "en": "Run pre-design"},
    "spinner_text": {
        "ru": "Агенты работают (Designer → Engineer → Validator → Reporter)...",
        "en": "Agents working (Designer → Engineer → Validator → Reporter)...",
    },
    "done_iterations": {"ru": "Готово. Итераций: {n}.", "en": "Done. Iterations: {n}."},
    "state_label": {"ru": "State", "en": "State"},
    "download_md": {"ru": "Скачать отчёт (.md)", "en": "Download report (.md)"},
    "download_pdf": {"ru": "Скачать отчёт (.pdf)", "en": "Download report (.pdf)"},
}


# ── Enum value translations ──────────────────────────────────────────────


ENUM_LABELS: dict[str, dict[Lang, str]] = {
    # GreenhouseType
    "year_round": {"ru": "круглогодичная", "en": "year-round"},
    "seasonal": {"ru": "сезонная", "en": "seasonal"},
    "nursery": {"ru": "рассадная", "en": "nursery"},
    # CropType
    "tomato": {"ru": "томат", "en": "tomato"},
    "cucumber": {"ru": "огурец", "en": "cucumber"},
    "lettuce": {"ru": "салат", "en": "lettuce"},
    "herbs": {"ru": "зелень", "en": "herbs"},
    "strawberry": {"ru": "клубника", "en": "strawberry"},
    # SoilType
    "sand": {"ru": "песок", "en": "sand"},
    "loam": {"ru": "суглинок", "en": "loam"},
    "clay": {"ru": "глина", "en": "clay"},
    "rocky": {"ru": "скальный", "en": "rocky"},
}


def t(key: str, lang: Lang, **kwargs: object) -> str:
    """Look up a UI string for the given language, optionally formatting it."""
    text = UI.get(key, {}).get(lang) or UI.get(key, {}).get("en") or key
    return text.format(**kwargs) if kwargs else text


def enum_label(value: str, lang: Lang) -> str:
    """Translate an enum value (e.g. 'tomato') for display only."""
    return ENUM_LABELS.get(value, {}).get(lang) or value
