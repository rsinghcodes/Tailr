import logging
from langgraph.graph import StateGraph, START, END
from workflows.state import WorkflowState
from workflows.nodes import (
    parse_resume_node,
    parse_jd_node,
    retrieve_context_node,
    plan_node,
    rewrite_node,
    guardrails_node,
    validation_node,
    ats_node,
    render_node,
)

logger = logging.getLogger(__name__)


def build_workflow_graph() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("parse_resume", parse_resume_node)
    graph.add_node("parse_jd", parse_jd_node)
    graph.add_node("retrieve_context", retrieve_context_node)
    graph.add_node("plan", plan_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("guardrails", guardrails_node)
    graph.add_node("validation", validation_node)
    graph.add_node("ats_analysis", ats_node)
    graph.add_node("render", render_node)

    graph.add_edge(START, "parse_resume")
    graph.add_edge("parse_resume", "parse_jd")
    graph.add_edge("parse_jd", "retrieve_context")
    graph.add_edge("retrieve_context", "plan")
    graph.add_edge("plan", "rewrite")
    graph.add_edge("rewrite", "guardrails")
    graph.add_edge("guardrails", "validation")
    graph.add_edge("validation", "ats_analysis")
    graph.add_edge("ats_analysis", "render")
    graph.add_edge("render", END)

    return graph


_compiled_graph = None


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_workflow_graph().compile()
    return _compiled_graph
