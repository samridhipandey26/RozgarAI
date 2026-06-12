"""
pipeline/runner.py — Pipeline Entrypoint
=========================================
Provides run_pipeline() which executes either:
  - The compiled LangGraph graph (if langgraph is installed)
  - A simple sequential runner as fallback

Also provides run_pipeline_streaming() for Streamlit step-by-step execution.
"""
from __future__ import annotations

import uuid
from typing import Callable, Generator, Optional

from pipeline.state import PipelineStage, RozgarState


def make_state(
    demo_mode: bool = True,
    audio_path: Optional[str] = None,
    session_id: Optional[str] = None,
    apply_confirmed: Optional[bool] = None,
) -> RozgarState:
    """Factory: create a fresh RozgarState."""
    return RozgarState(
        session_id=session_id or uuid.uuid4().hex,
        raw_audio_path=audio_path,
        demo_mode=demo_mode,
        apply_confirmed=apply_confirmed,
    )


def run_pipeline(state: RozgarState) -> RozgarState:
    """
    Run the full pipeline synchronously.
    Uses LangGraph if available, else sequential fallback.
    """

    return RozgarState(
        session_id=session_id or uuid.uuid4().hex,
        raw_audio_path=audio_path,
        demo_mode=demo_mode,
        apply_confirmed=apply_confirmed,
    )


def run_pipeline(state: RozgarState) -> RozgarState:
    """
    Run the full pipeline synchronously.
    Uses LangGraph if available, else sequential fallback.
    """
    return _run_sequential(state)


def run_pipeline_streaming(
    state: RozgarState,
    on_stage: Optional[Callable[[RozgarState, str], None]] = None,
) -> Generator[RozgarState, None, None]:
    """
    Generator that runs each agent one at a time.
    Yields state after each agent completes.
    Calls on_stage(state, agent_name) before each agent if provided.
    Pauses before apply_agent if apply_confirmed is None (awaiting consent).
    """
    from agents import (
        voice_intake, skill_extractor, resume_builder,
        job_matcher, interview_coach, apply_agent, status_tracker,
    )



def run_pipeline_streaming(
    state: RozgarState,
    on_stage: Optional[Callable[[RozgarState, str], None]] = None,
) -> Generator[RozgarState, None, None]:
    """
    Generator that runs each agent one at a time.
    Yields state after each agent completes.
    Calls on_stage(state, agent_name) before each agent if provided.
    Pauses before apply_agent if apply_confirmed is None (awaiting consent).
    """
    from agents import (
        voice_intake, skill_extractor, resume_builder,
        job_matcher, interview_coach, apply_agent, status_tracker,
    )

    agents_seq = [
        ("voice_intake",    voice_intake),
        ("skill_extractor", skill_extractor),
        ("resume_builder",  resume_builder),
        ("job_matcher",     job_matcher),
        ("interview_coach", interview_coach),
        ("apply_gate",      None),           # Pause point
        ("apply_agent",     apply_agent),
        ("status_tracker",  status_tracker),
    ]

    for name, fn in agents_seq:

        # ── Pause for human consent ──────────────────────────────────────────
        if name == "apply_gate":
            if state.apply_confirmed is not True:
                yield state   # Caller must set state.apply_confirmed and re-enter
                return
            continue

        if on_stage:
            on_stage(state, name)

        state = fn(state)
        yield state

        if state.current_stage == PipelineStage.ERROR:
            return
        if state.current_stage == PipelineStage.DONE:
            return


def _run_sequential(state: RozgarState) -> RozgarState:
    """Linear fallback when LangGraph is not installed."""
    from agents import (
        voice_intake, skill_extractor, resume_builder,
        job_matcher, interview_coach, apply_agent, status_tracker,
    )
    for fn in [voice_intake, skill_extractor, resume_builder,
               job_matcher, interview_coach, apply_agent, status_tracker]:
        state = fn(state)
        if state.current_stage == PipelineStage.ERROR:
            break
    return state
