"""tests/test_pipeline.py — Integration tests for full pipeline"""
import pytest
from pipeline.state import RozgarState, PipelineStage
from pipeline.runner import make_state, run_pipeline


def test_full_demo_pipeline():
    """Run the full pipeline in demo mode — should reach DONE without errors."""
    state = make_state(demo_mode=True)
    state.apply_confirmed = True   # Pre-confirm to pass gate

    result = run_pipeline(state)

    assert result.current_stage == PipelineStage.DONE
    assert result.worker is not None
    assert result.matched_jobs != []
    assert result.resume_pdf_path is not None
    assert result.apply_otp is not None
    assert result.status_message_hindi is not None
    assert len(result.trace_log) >= 7


def test_pipeline_gate_blocks():
    """Pipeline should pause before apply when apply_confirmed is None."""
    from pipeline.runner import run_pipeline_streaming
    state = make_state(demo_mode=True)
    # Do NOT set apply_confirmed

    yielded = []
    for s in run_pipeline_streaming(state):
        yielded.append(s)
        if s.current_stage == PipelineStage.ERROR:
            break

    # Should have stopped before apply agent
    assert all(s.apply_otp is None for s in yielded)


def test_make_state_defaults():
    state = make_state()
    assert state.demo_mode is True
    assert state.session_id is not None
    assert state.current_stage == PipelineStage.VOICE_INTAKE
