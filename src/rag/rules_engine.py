"""Rules engine: evaluates rules.yaml against the proposed design + engineering.

This is the *deterministic* layer of validation. The RAG layer (sp_index)
attaches the literal SP wording to each issue after the fact.

DSL features:
- Dotted field paths with `blocks[*]` wildcard.
- When *any* path in a rule uses `blocks[*]`, evaluation runs *per block* —
  applies_when is checked for that block, and `check.field` reads from the
  same block. This avoids the trap where a mixed angar+block design silently
  skips a span-width violation because applies_when looked at *all* blocks.
- `check_type: custom` dispatches to a named handler in `_CUSTOM_CHECKS`
  for rules that don't fit the operator DSL (e.g. ridge > eave + 0.5).
- `between` op takes a [min, max] value.

Anything more complex than these primitives should be a custom handler.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from ..schemas.calc_results import EngineeringReport
from ..schemas.design import DesignVariant, GreenhouseBlock
from ..schemas.project import ClimateData, ProjectBrief
from ..schemas.validation import Severity, ValidationIssue

_RULES_PATH = Path(__file__).parent.parent.parent / "data" / "rules.yaml"
_BLOCK_WILDCARD = "blocks[*]"


def _load_rules() -> list[dict]:
    with _RULES_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)["rules"]


# ── path resolution ──────────────────────────────────────────────────────


def _resolve_field(path: str, ctx: dict[str, Any]) -> list[Any]:
    """Resolve a dotted path with optional [*] wildcard. Returns a list of values."""
    parts = path.split(".")
    current: list[Any] = [ctx]
    for part in parts:
        next_current: list[Any] = []
        wildcard = part.endswith("[*]")
        key = part[:-3] if wildcard else part
        for obj in current:
            if obj is None:
                continue
            value = _get_attr_or_key(obj, key)
            if wildcard and isinstance(value, list):
                next_current.extend(value)
            else:
                next_current.append(value)
        current = next_current
    return [v for v in current if v is not None]


def _get_attr_or_key(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    if hasattr(obj, key):
        return getattr(obj, key)
    return None


# ── operator DSL ─────────────────────────────────────────────────────────


def _single_op(v: Any, op: str, expected: Any) -> bool:
    if op == ">=":
        return v >= expected
    if op == "<=":
        return v <= expected
    if op == ">":
        return v > expected
    if op == "<":
        return v < expected
    if op == "==":
        return v == expected
    if op == "!=":
        return v != expected
    if op == "in":
        return v in expected
    if op == "not_in":
        return v not in expected
    if op == "between":
        return expected[0] <= v <= expected[1]
    raise ValueError(f"Unknown op: {op}")


def _check_op(values: list[Any], op: str, expected: Any) -> bool:
    if not values:
        return True
    return all(_single_op(v, op, expected) for v in values)


# ── applies_when ─────────────────────────────────────────────────────────


def _enum_str(v: Any) -> str:
    return str(v.value if hasattr(v, "value") else v)


def _applies(rule: dict, ctx: dict[str, Any]) -> bool:
    cond = rule.get("applies_when")
    if not cond:
        return True
    for path, expected in cond.items():
        values = _resolve_field(path, ctx)
        if not values:
            return False
        for v in values:
            if isinstance(expected, list):
                if _enum_str(v) not in [_enum_str(e) for e in expected]:
                    return False
            else:
                if _enum_str(v) != _enum_str(expected):
                    return False
    return True


# ── custom checks ────────────────────────────────────────────────────────


def _check_ridge_above_eave(
    brief: ProjectBrief,
    design: DesignVariant,
    engineering: EngineeringReport,
) -> tuple[str, str] | None:
    """ENG.1-ridge-vs-eave — ridge_height ≥ eave_height + 0.5 m for every block.

    Returns (actual_str, required_str) for the violation, or None if passed.
    """
    bad = [
        (b.name, b.ridge_height_m, b.eave_height_m)
        for b in design.blocks
        if b.ridge_height_m < b.eave_height_m + 0.5
    ]
    if not bad:
        return None
    desc = "; ".join(f"{n}: ridge={r} eave={e}" for n, r, e in bad)
    return desc, "ridge ≥ eave + 0.5 м для каждого блока"


# Typical achievable yield (t/ha/year) for greenhouse-grown crops. Source:
# Russian VNII Ovoshchevodstva guides + Cornell CEA references. Pre-design
# numbers — production planning should use crop-cycle-specific values.
_CROP_YIELD_KG_M2: dict[str, float] = {
    "tomato": 50.0,       # 4-6 trusses, year-round high-wire
    "cucumber": 28.0,     # 8-10 month cycle in heated greenhouse
    "lettuce": 35.0,      # multi-cycle hydroponics
    "herbs": 12.0,        # cut-and-come-again
    "strawberry": 25.0,   # double-crop production
}


def _check_yield_feasibility(
    brief: ProjectBrief,
    design: DesignVariant,
    engineering: EngineeringReport,  # noqa: ARG001
) -> tuple[str, str] | None:
    """ENG.5: growing area × crop norm must cover ≥90% of the brief's target yield."""
    growing_area = sum(b.floor_area_m2 for b in design.blocks)
    crop_key = brief.target_crop.value
    crop_norm = _CROP_YIELD_KG_M2.get(crop_key, 30.0)
    capacity_t = growing_area * crop_norm / 1000
    target_t = brief.target_annual_yield_t
    required_capacity = target_t * 0.9  # 10% tolerance for losses, headhouse, etc.
    if capacity_t >= required_capacity:
        return None
    return (
        f"вмещает ~{capacity_t:.0f} т/год ({crop_key} @ {crop_norm} кг/м² × {growing_area:.0f} м²)",
        f">= {required_capacity:.0f} т/год (90% от ТЗ {target_t} т)",
    )


_CUSTOM_CHECKS: dict[str, Callable[..., tuple[str, str] | None]] = {
    "ridge_above_eave": _check_ridge_above_eave,
    "yield_feasibility": _check_yield_feasibility,
}


# ── per-rule evaluation ──────────────────────────────────────────────────


def _rule_uses_block_wildcard(rule: dict) -> bool:
    field = rule.get("check", {}).get("field", "")
    if _BLOCK_WILDCARD in field:
        return True
    applies = rule.get("applies_when") or {}
    return any(_BLOCK_WILDCARD in p for p in applies)


def _block_ctx(ctx: dict[str, Any], block: GreenhouseBlock) -> dict[str, Any]:
    """Replace `design.blocks[*]` resolution with a single block for per-block eval."""
    # We re-rewrite paths on the fly via a shim: a copy of design with one block.
    design = ctx["design"]
    shim = design.model_copy(update={"blocks": [block]})
    return {**ctx, "design": shim}


def _eval_simple(
    rule: dict, ctx: dict[str, Any]
) -> tuple[ValidationIssue | None, bool]:
    """Return (issue, was_checked). was_checked=False means no data was found."""
    check = rule["check"]

    if check.get("check_type") == "custom":
        handler = _CUSTOM_CHECKS[check["name"]]
        outcome = handler(ctx["brief"], ctx["design"], ctx["engineering"])
        if outcome is None:
            return None, True
        actual, required = outcome
        return _issue_from(rule, actual, required), True

    values = _resolve_field(check["field"], ctx)
    if not values:
        return _no_data_issue(rule), False
    if _check_op(values, check["op"], check["value"]):
        return None, True
    actual = values[0] if len(values) == 1 else values
    return _issue_from(rule, str(actual), str(check["value"])), True


def _eval_per_block(
    rule: dict, ctx: dict[str, Any]
) -> tuple[ValidationIssue | None, bool]:
    """Iterate every block; collect ALL violators (not just the first) into one issue.

    Returns (issue, was_checked). was_checked=False when applies_when didn't
    match any block (so no work was done) — keeps the rules-checked counter
    honest.
    """
    design: DesignVariant = ctx["design"]
    check = rule["check"]
    violations: list[tuple[str, Any]] = []
    missing_data: list[str] = []
    applied = False

    for block in design.blocks:
        sub_ctx = _block_ctx(ctx, block)
        if not _applies(rule, sub_ctx):
            continue
        applied = True
        values = _resolve_field(check["field"], sub_ctx)
        if not values:
            missing_data.append(block.name)
            continue
        if _check_op(values, check["op"], check["value"]):
            continue
        violations.append((block.name, values[0] if len(values) == 1 else values))

    if not applied:
        return None, False

    if violations:
        desc = "; ".join(f"{name}: {val}" for name, val in violations)
        return _issue_from(rule, desc, str(check["value"])), True

    if missing_data:
        return _no_data_issue(rule), False

    return None, True


def _issue_from(rule: dict, actual: str, required: str) -> ValidationIssue:
    return ValidationIssue(
        rule_id=rule["rule_id"],
        severity=Severity(rule.get("severity", "warning")),
        message=rule["summary"],
        actual_value=actual,
        required_value=required,
    )


def _no_data_issue(rule: dict) -> ValidationIssue:
    """INFO-severity issue when a rule's field path resolved to nothing.

    Prevents silent passes on typos in rules.yaml or missing virtual fields.
    """
    return ValidationIssue(
        rule_id=rule["rule_id"],
        severity=Severity.INFO,
        message=rule["summary"] + " (не удалось проверить — нет данных)",
        actual_value=None,
        required_value=str(rule.get("check", {}).get("value", "")),
    )


# ── virtual computed fields ──────────────────────────────────────────────


def _attach_virtual_fields(design: DesignVariant) -> None:
    """Populate Optional virtual fields the schema declares.

    Writes:
        design.aux_share_pct       — % of aux zones from footprint. None when
                                     footprint is missing/zero (avoids the
                                     "thousands of percents" bug).
        design.min_block_spacing_m — pass-through of design.block_spacing_m
                                     that Designer is expected to fill. We
                                     NEVER invent a value: if it's missing,
                                     SP107.4.4 emits a no-data INFO issue
                                     instead of silently passing.
    """
    footprint = design.estimated_footprint_m2
    if footprint and footprint > 0 and design.aux_zones:
        design.aux_share_pct = sum(z.area_m2 for z in design.aux_zones) / footprint * 100
    elif footprint and footprint > 0:
        design.aux_share_pct = 0.0
    else:
        design.aux_share_pct = None

    design.min_block_spacing_m = design.block_spacing_m  # may be None — intentional


# ── entry point ──────────────────────────────────────────────────────────


def evaluate_rules(
    brief: ProjectBrief,
    design: DesignVariant,
    engineering: EngineeringReport,
    climate: ClimateData | None = None,
) -> tuple[list[ValidationIssue], int]:
    rules = _load_rules()
    _attach_virtual_fields(design)
    ctx: dict[str, Any] = {
        "brief": brief,
        "design": design,
        "engineering": engineering,
        "climate": climate,
    }

    issues: list[ValidationIssue] = []
    checked = 0

    for rule in rules:
        if _rule_uses_block_wildcard(rule):
            issue, was_checked = _eval_per_block(rule, ctx)
        else:
            if not _applies(rule, ctx):
                continue
            issue, was_checked = _eval_simple(rule, ctx)

        if was_checked or issue is not None:
            checked += 1
        if issue:
            issues.append(issue)

    return issues, checked
