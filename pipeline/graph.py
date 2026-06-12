"""
pipeline/graph.py — LangGraph StateGraph Definition
=====================================================
Defines the 7-node directed graph for the RozgarAI pipeline.
The apply gate (Agent 6) requires human-in-the-loop confirmation.
"""
from __future__ import annotations

from typing import Literal

from pipeline.state import PipelineStage, RozgarState


def _route_after_apply_gate(state: RozgarState) -> Literal["apply_agent", "__end__"]:
    """Conditional edge: only proceed to apply if confirmed."""
    if state.apply_confirmed is True:
        return "apply_agent"
    return "__end__"


def _route_after_jobs(state: RozgarState) -> Literal["interview_coach", "__end__"]:
    """Skip coaching if no jobs matched."""
    if state.matched_jobs:
        return "interview_coach"
    return "__end__"


def build_graph():
    """Build and compile the LangGraph StateGraph. Returns compiled graph."""
    try:
        from langgraph.graph import StateGraph, END
        from agents import (
            voice_intake, skill_extractor, resume_builder,
            job_matcher, interview_coach, apply_agent, status_tracker,
        )

        # LangGraph requires a TypedDict state — we wrap our dataclass
        # by converting to/from dict at graph boundaries
        from typing import TypedDict, Any

        class GraphState(TypedDict, total=False):
            rozgar_state: Any  # carries RozgarState object

        def wrap(fn):
            def _wrapped(gs: dict) -> dict:
                gs["rozgar_state"] = fn(gs["rozgar_state"])
                return gs
            _wrapped.__name__ = fn.__name__
            return _wrapped

        def gate_route(gs: dict):
            state: RozgarState = gs["rozgar_state"]
            return _route_after_apply_gate(state)

        def jobs_route(gs: dict):
            state: RozgarState = gs["rozgar_state"]
            return _route_after_jobs(state)

        g = StateGraph(GraphState)

        g.add_node("voice_intake",    wrap(voice_intake))
        g.add_node("skill_extractor", wrap(skill_extractor))
        g.add_node("resume_builder",  wrap(resume_builder))
        g.add_node("job_matcher",     wrap(job_matcher))
        g.add_node("interview_coach", wrap(interview_coach))
        g.add_node("apply_agent",     wrap(apply_agent))
        g.add_node("status_tracker",  wrap(status_tracker))

        g.set_entry_point("voice_intake")

        g.add_edge("voice_intake",    "skill_extractor")
        g.add_edge("skill_extractor", "resume_builder")
        g.add_edge("resume_builder",  "job_matcher")
        g.add_conditional_edges("job_matcher", jobs_route, {
            "interview_coach": "interview_coach",
            "__end__": END,
        })
        g.add_conditional_edges("interview_coach", gate_route, {
            "apply_agent": "apply_agent",
            "__end__": END,
        })
        g.add_edge("apply_agent",     "status_tracker")
        g.add_edge("status_tracker",  END)

        return g.compile()

    except ImportError:
        # langgraph not installed — fall back to linear runner
        return None
