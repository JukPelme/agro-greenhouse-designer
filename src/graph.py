"""LangGraph orchestration.

Flow:
    START → analyst → designer → engineer → validator → [reporter | designer]
                                                ↓                ↑
                                          (errors? & iter<max) → loops back

The validator decides whether to ship the report or send the design back
for revision (up to max_iterations).
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .agents.analyst import analyst_node
from .agents.designer import designer_node
from .agents.engineer import engineer_node
from .agents.reporter import reporter_node
from .agents.validator import validator_node
from .schemas.state import GraphState


def _validator_router(state: GraphState) -> str:
    """Decide whether the design is shippable or needs another pass."""
    if state.validation is None:
        return "reporter"  # nothing checked → report what we have
    if state.validation.passed:
        return "reporter"
    if state.iteration >= state.max_iterations:
        return "reporter"  # give up, ship with issues annotated
    return "designer"  # loop back


def build_graph() -> StateGraph:
    g = StateGraph(GraphState)
    g.add_node("analyst", analyst_node)
    g.add_node("designer", designer_node)
    g.add_node("engineer", engineer_node)
    g.add_node("validator", validator_node)
    g.add_node("reporter", reporter_node)

    g.add_edge(START, "analyst")
    g.add_edge("analyst", "designer")
    g.add_edge("designer", "engineer")
    g.add_edge("engineer", "validator")
    g.add_conditional_edges(
        "validator",
        _validator_router,
        {"reporter": "reporter", "designer": "designer"},
    )
    g.add_edge("reporter", END)

    return g.compile()


# Module-level instance for convenience.
graph = build_graph()
