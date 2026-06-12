"""agents/resume_builder.py — Agent 3: Resume Builder"""
from __future__ import annotations

from pipeline.state import PipelineStage, RozgarState
from ui.strings_hi import TRACE_RESUME_DONE


def resume_builder(state: RozgarState) -> RozgarState:
    """
    Agent 3 — Resume Builder
    Input:  state.worker
    Output: state.resume_pdf_path
    """
    try:
        state.current_stage = PipelineStage.RESUME_BUILD

        if state.worker is None:
            raise ValueError("Worker profile not set — cannot build resume")

        from utils.pdf_gen import generate_resume_pdf
        w = state.worker
        pdf_path = generate_resume_pdf(
            worker_id=w.worker_id,
            name=w.name,
            phone=w.phone,
            city=w.city,
            pin_code=w.pin_code,
            skills=w.skills,
            experience_years=w.experience_years,
            preferred_wage_per_day=w.preferred_wage_per_day,
        )

        state.resume_pdf_path = pdf_path
        state.log(TRACE_RESUME_DONE)
        state.add_wa_message("bot", f"Aapki resume taiyaar ho gayi! PDF download karein.")

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state
