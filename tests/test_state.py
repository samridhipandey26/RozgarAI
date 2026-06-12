"""tests/test_state.py — Unit tests for RozgarState"""
import pytest
from pipeline.state import RozgarState, WorkerProfile, JobListing, PipelineStage


def test_state_defaults():
    state = RozgarState(session_id="test123")
    assert state.session_id == "test123"
    assert state.current_stage == PipelineStage.VOICE_INTAKE
    assert state.worker is None
    assert state.matched_jobs == []
    assert state.interview_tips == []
    assert state.apply_confirmed is None
    assert state.trace_log == []


def test_state_log():
    state = RozgarState(session_id="t1")
    state.log("Step 1 done")
    state.log("Step 2 done")
    assert len(state.trace_log) == 2
    assert "Step 1 done" in state.trace_log


def test_state_whatsapp():
    state = RozgarState(session_id="t1")
    state.add_wa_message("bot", "Namaste!")
    state.add_wa_message("worker", "Hello")
    assert len(state.whatsapp_messages) == 2
    assert state.whatsapp_messages[0]["role"] == "bot"
    assert state.whatsapp_messages[1]["text"] == "Hello"


def test_worker_profile():
    w = WorkerProfile(
        worker_id="w001", name="Raju", phone="+91999",
        city="Lucknow", pin_code="226001",
        skills=["electrician"], experience_years=5,
        preferred_wage_per_day=600,
    )
    assert w.languages == ["hindi"]
    assert "electrician" in w.skills


def test_job_listing():
    j = JobListing(
        job_id="j001", contractor_id="c001",
        title="Electrician", title_hindi="इलेक्ट्रीशियन",
        location="Lucknow", pin_code="226001",
        wage_per_day=700, skills_required=["electrician"],
        start_date="2026-06-14", openings=2,
    )
    assert j.distance_km is None
    assert j.openings == 2
