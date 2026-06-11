"""Matplotlib-based charts for the engineering section of the report.

Design choices:
- All charts use the same muted palette so they look like one set.
- Each chart fits a single column in the rendered Markdown (max 800px wide).
- Functions write PNG files and return relative paths (callers compose Markdown).
- MPLCONFIGDIR is set to a writable cache dir before matplotlib import to
  survive read-only home directories.
"""

from __future__ import annotations

import os
from pathlib import Path

# Ensure matplotlib can write its font cache even when $HOME is partially RO.
os.environ.setdefault("MPLCONFIGDIR", str(Path.home() / ".cache" / "matplotlib"))

import matplotlib

matplotlib.use("Agg")  # headless backend — no display required
import matplotlib.pyplot as plt  # noqa: E402

from ..schemas.state import GraphState  # noqa: E402

_PALETTE = {
    "primary": "#2C5F2D",     # deep green — natural / structural
    "secondary": "#97BC62",   # leaf green — required / installed
    "warning": "#D9A05B",     # warm amber — losses / deficit
    "accent": "#5B8A72",      # muted teal — supplemental
    "neutral": "#6B6B6B",
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "figure.dpi": 110,
        "savefig.bbox": "tight",
    }
)


def _save(fig, out_dir: Path, name: str) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    return path.name  # relative to out_dir — caller composes the full Markdown path


def energy_balance_chart(state: GraphState, out_dir: Path) -> str:
    """Bar chart: transmission / infiltration / peak — kilowatts."""
    h = state.engineering.heat
    fig, ax = plt.subplots(figsize=(7.5, 4))
    bars = ax.bar(
        ["Трансмиссия", "Инфильтрация", "Пиковая\nнагрузка"],
        [h.transmission_loss_kw, h.infiltration_loss_kw, h.total_peak_load_kw],
        color=[_PALETTE["warning"], _PALETTE["accent"], _PALETTE["primary"]],
        width=0.55,
    )
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(h.total_peak_load_kw * 0.02, 1),
            f"{bar.get_height():.0f} кВт",
            ha="center",
            fontsize=10,
        )
    ax.set_ylabel("Мощность, кВт")
    ax.set_title("Теплопотери и пиковая нагрузка")
    ax.set_ylim(0, h.total_peak_load_kw * 1.15)
    return _save(fig, out_dir, "energy_balance")


def light_balance_chart(state: GraphState, out_dir: Path) -> str:
    """DLI: target / natural / supplemental."""
    li = state.engineering.light
    supplemental = max(li.target_dli_mol_m2_day - li.natural_dli_winter_mol_m2_day, 0)

    fig, ax = plt.subplots(figsize=(7.5, 4))
    labels = ["Естественный\nDLI зимой", "Досветка\n(дефицит)", "Целевой DLI"]
    bottoms = [0, li.natural_dli_winter_mol_m2_day, 0]
    values = [li.natural_dli_winter_mol_m2_day, supplemental, li.target_dli_mol_m2_day]
    colors = [_PALETTE["secondary"], _PALETTE["warning"], _PALETTE["primary"]]

    for label, bottom, value, color in zip(labels, bottoms, values, colors, strict=True):
        ax.bar(label, value, bottom=bottom, color=color, width=0.5)
        ax.text(
            label,
            bottom + value + 0.3,
            f"{value:.1f}",
            ha="center",
            fontsize=10,
        )

    ax.set_ylabel("DLI, моль/м²/сут")
    ax.set_title("Баланс освещённости (зимний период)")
    ax.set_ylim(0, max(li.target_dli_mol_m2_day, 1) * 1.25)
    return _save(fig, out_dir, "light_balance")


def annual_energy_chart(state: GraphState, out_dir: Path) -> str:
    """Pie chart: heating vs lighting share of annual energy in MWh."""
    heat_mwh = state.engineering.heat.annual_heat_demand_mwh
    light_mwh = state.engineering.light.supplemental_kwh_year / 1000
    total = heat_mwh + light_mwh
    if total <= 0:
        # Nothing to render — return an empty placeholder.
        return ""

    fig, ax = plt.subplots(figsize=(6, 5))
    sizes = [heat_mwh, light_mwh]
    labels = [
        f"Отопление\n{heat_mwh:.0f} МВт·ч",
        f"Досветка\n{light_mwh:.0f} МВт·ч",
    ]
    wedges, *_ = ax.pie(
        sizes,
        labels=labels,
        colors=[_PALETTE["warning"], _PALETTE["accent"]],
        startangle=90,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2},
    )
    ax.set_title(f"Годовое энергопотребление: {total:.0f} МВт·ч")
    ax.set(aspect="equal")
    return _save(fig, out_dir, "annual_energy")


def water_demand_chart(state: GraphState, out_dir: Path) -> str:
    """Daily / peak-hourly / annual water demand."""
    w = state.engineering.water

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 4))

    # Left: daily & peak hourly in m³
    bars1 = ax1.bar(
        ["Суточный", "Пиковый\nчасовой"],
        [w.daily_demand_m3, w.peak_hourly_m3],
        color=[_PALETTE["primary"], _PALETTE["warning"]],
        width=0.5,
    )
    for bar in bars1:
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.03,
            f"{bar.get_height():.1f} м³",
            ha="center",
            fontsize=10,
        )
    ax1.set_ylabel("Расход, м³")
    ax1.set_title("Расход воды")

    # Right: annual total
    ax2.bar(["Год"], [w.annual_demand_m3 / 1000], color=_PALETTE["accent"], width=0.4)
    ax2.text(
        0,
        w.annual_demand_m3 / 1000 * 1.02,
        f"{w.annual_demand_m3 / 1000:.1f} тыс. м³",
        ha="center",
        fontsize=10,
    )
    ax2.set_ylabel("Годовой расход, тыс. м³")
    ax2.set_title("Годовой объём полива")
    return _save(fig, out_dir, "water_demand")


def render_all(state: GraphState, out_dir: Path) -> dict[str, str]:
    """Render every chart and return a dict {name: filename}."""
    if state.engineering is None:
        return {}
    return {
        "energy_balance": energy_balance_chart(state, out_dir),
        "light_balance": light_balance_chart(state, out_dir),
        "annual_energy": annual_energy_chart(state, out_dir),
        "water_demand": water_demand_chart(state, out_dir),
    }
