"""tests/test_agents.py — Unit tests for individual agents (no Streamlit imports)"""
import pytest
from pipeline.state import RozgarState, WorkerProfile, JobListing, PipelineStage


def _demo_state() -> RozgarState:
    state = RozgarState(session_id="test_session", demo_mode=True)
    return state


def _worker() -> WorkerProfile:
    return WorkerProfile(
        worker_id="w_test", name="Raju Kumar",
        phone="+919876543210", city="Lucknow",
        pin_code="226001", skills=["electrician"],
        experience_years=5, preferred_wage_per_day=600,
    )


class TestVoiceIntake:
    def test_demo_mode(self):
        from agents.voice_intake import voice_intake
        state = _demo_state()
        result = voice_intake(state)
        assert result.transcript_hindi is not None
        assert len(result.transcript_hindi) > 10
        assert result.current_stage != PipelineStage.ERROR

    def test_none_audio_path(self):
        from agents.voice_intake import voice_intake
        state = _demo_state()
        state.raw_audio_path = None
        result = voice_intake(state)
        assert result.transcript_hindi is not None


class TestSkillExtractor:
    def test_demo_mode(self):
        from agents.skill_extractor import skill_extractor
        state = _demo_state()
        state.transcript_hindi = "Main electrician hoon Lucknow mein"
        result = skill_extractor(state)
        assert result.worker is not None
        assert result.worker.name != ""
        assert len(result.worker.skills) > 0
        assert result.current_stage != PipelineStage.ERROR


class TestResumeBuilder:
    def test_generates_pdf(self, tmp_path, monkeypatch):
        from agents.resume_builder import resume_builder
        state = _demo_state()
        state.worker = _worker()
        # Patch output dir to tmp
        import utils.pdf_gen as pg
        monkeypatch.setattr(pg, "RESUMES_DIR", tmp_path)
        result = resume_builder(state)
        # Should not error even if path differs
        assert result.current_stage != PipelineStage.ERROR


class TestJobMatcher:
    def test_returns_matches(self):
        from agents.job_matcher import job_matcher
        state = _demo_state()
        state.worker = _worker()
        result = job_matcher(state)
        assert isinstance(result.matched_jobs, list)
        assert result.current_stage != PipelineStage.ERROR

    def test_scores_set(self):
        from agents.job_matcher import job_matcher
        state = _demo_state()
        state.worker = _worker()
        result = job_matcher(state)
        for job in result.matched_jobs:
            assert job.match_score is not None
            assert 0.0 <= job.match_score <= 1.5   # composite can exceed 1


class TestApplyAgent:
    def test_hard_gate_blocks_without_confirm(self):
        from agents.apply_agent import apply_agent
        state = _demo_state()
        state.worker = _worker()
        state.selected_job = JobListing(
            job_id="j001", contractor_id="c001",
            title="Electrician", title_hindi="इलेक्ट्रीशियन",
            location="Lucknow", pin_code="226001",
            wage_per_day=700, skills_required=["electrician"],
            start_date="2026-06-14", openings=2,
        )
        state.apply_confirmed = None   # NOT confirmed
        result = apply_agent(state)
        assert result.apply_otp is None
        assert result.error_message is not None

    def test_proceeds_when_confirmed(self):
        from agents.apply_agent import apply_agent
        state = _demo_state()
        state.worker = _worker()
        state.selected_job = JobListing(
            job_id="j001", contractor_id="c001",
            title="Electrician", title_hindi="इलेक्ट्रीशियन",
            location="Lucknow", pin_code="226001",
            wage_per_day=700, skills_required=["electrician"],
            start_date="2026-06-14", openings=2,
        )
        state.apply_confirmed = True
        result = apply_agent(state)
        assert result.apply_otp is not None
        assert len(result.apply_otp) == 4
        assert result.apply_otp.isdigit()
