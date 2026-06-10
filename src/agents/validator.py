"""Validator agent: checks design + engineering against rules.yaml and cites SP via RAG.

Two-layer approach:
1. Deterministic checks from rules.yaml (machine-checkable conditions with numbers)
2. RAG citation: for each issue, fetch the literal SP wording from the indexed PDF

Inputs:  GraphState.design, GraphState.engineering, GraphState.brief
Outputs: GraphState.validation
"""

from __future__ import annotations

from ..rag.rules_engine import evaluate_rules
from ..rag.sp_index import cite_sp_paragraph
from ..schemas.state import GraphState
from ..schemas.validation import ValidationReport


def validator_node(state: GraphState) -> dict:
    if state.design is None or state.engineering is None:
        return {"errors": ["Validator: нет design или engineering."]}

    issues, rules_checked = evaluate_rules(
        brief=state.brief,
        design=state.design,
        engineering=state.engineering,
    )

    # Enrich each issue with a literal SP citation via RAG.
    for issue in issues:
        if issue.rule_id and issue.sp_citation is None:
            issue.sp_citation = cite_sp_paragraph(issue.rule_id)

    return {
        "validation": ValidationReport(issues=issues, rules_checked=rules_checked)
    }
