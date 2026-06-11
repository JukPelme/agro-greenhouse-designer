"""Rules engine: evaluates rules.yaml against the proposed design + engineering.

This is the *deterministic* layer of validation. The RAG layer (sp_index)
attaches the literal SP wording to each issue after the fact.

The DSL is intentionally tiny — anything more complex is a regular Python
function in `_custom_checks`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..schemas.calc_results import EngineeringReport
from ..schemas.design import DesignVariant
from ..schemas.project import ProjectBrief
from ..schemas.validation import Severity, ValidationIssue

_RULES_PATH = Path(__file__).parent.parent.parent / "data" / "rules.yaml"


def _load_rules() -> list[dict]:
    with _RULES_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)["rules"]


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


def _check_op(values: list[Any], op: str, expected: Any) -> bool:
    if not values:
        return True  # nothing to check — pass
    for v in values:
        if not _single_op(v, op, expected):
            return False
    return True


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
                if v not in expected:
                    return False
            else:
                # Compare by string for enum compatibility.
                if str(v.value if hasattr(v, "value") else v) != str(expected):
                    return False
    return True


def evaluate_rules(
    brief: ProjectBrief,
    design: DesignVariant,
    engineering: EngineeringReport,
) -> tuple[list[ValidationIssue], int]:
    rules = _load_rules()
    ctx = {"brief": brief, "design": design, "engineering": engineering}

    issues: list[ValidationIssue] = []
    checked = 0

    # Virtual computed fields used by some rules.
    aux_share_pct = (
        sum(z.area_m2 for z in design.aux_zones)
        / (design.estimated_footprint_m2 or 1)
        * 100
    )
    design.aux_share_pct = aux_share_pct
    design.min_aisle_width_m = 6.0 if len(design.blocks) > 1 else 0.0

    for rule in rules:
        if not _applies(rule, ctx):
            continue
        check = rule["check"]
        values = _resolve_field(check["field"], ctx)
        checked += 1
        if not _check_op(values, check["op"], check["value"]):
            actual = values[0] if len(values) == 1 else values
            issues.append(
                ValidationIssue(
                    rule_id=rule["rule_id"],
                    severity=Severity(rule.get("severity", "warning")),
                    message=rule["summary"],
                    actual_value=str(actual),
                    required_value=str(check["value"]),
                )
            )

    return issues, checked
