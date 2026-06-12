"""agents/apply_agent.py — Agent 6: Apply Agent (HARD GATE)"""
from __future__ import annotations

import random
import uuid
from datetime import datetime

from pipeline.state import PipelineStage, RozgarState
from ui.strings_hi import (
    APPLY_CONSENT_REQUIRED, APPLY_CONFIRMED_MSG,
    APPLY_SUCCESS_TEMPLATE, TRACE_APPLY_DONE, WHATSAPP_OTP_MESSAGE,
)


def apply_agent(state: RozgarState) -> RozgarState:
    """
    Agent 6 — Apply Agent
    HARD GATE: state.apply_confirmed must be True.
    Input:  state.worker, state.selected_job, state.apply_confirmed
    Output: state.apply_otp, inserts application row
    """
    try:
        state.current_stage = PipelineStage.APPLY

        # ── HARD GATE ────────────────────────────────────────────────────────
        if state.apply_confirmed is not True:
            state.error_message = APPLY_CONSENT_REQUIRED
            state.add_wa_message("bot", APPLY_CONSENT_REQUIRED)
            # Do NOT set ERROR stage — gate is expected to pause, not crash
            return state

        if state.worker is None or state.selected_job is None:
            raise ValueError("Worker or selected_job not set")

        # Generate OTP
        otp = str(random.randint(1000, 9999))
        state.apply_otp = otp

        # Write to DB
        app_id = f"app_{uuid.uuid4().hex[:8]}"
        _insert_application(
            app_id=app_id,
            worker_id=state.worker.worker_id,
            job_id=state.selected_job.job_id,
            otp=otp,
        )

        # WhatsApp OTP message
        otp_msg = WHATSAPP_OTP_MESSAGE.format(
            otp=otp,
            location=state.selected_job.location,
        )
        state.add_wa_message("bot", otp_msg)

        # Success message
        success_msg = APPLY_SUCCESS_TEMPLATE.format(
            name=state.worker.name,
            job_title=state.selected_job.title_hindi,
            otp=otp,
            date=state.selected_job.start_date,
            location=state.selected_job.location,
        )
        print(f"[SIMULATED WhatsApp] {success_msg}")

        state.log(TRACE_APPLY_DONE)

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _insert_application(app_id: str, worker_id: str, job_id: str, otp: str) -> None:
    try:
        from db.models import get_session, Application, Job
        with get_session() as session:
            session.add(Application(
                application_id=app_id,
                worker_id=worker_id,
                job_id=job_id,
                status="confirmed",
                otp=otp,
                otp_verified=False,
            ))
            job = session.get(Job, job_id)
            if job and job.openings > 0:
                job.openings -= 1
                job.filled   += 1
            session.commit()
    except Exception as e:
        print(f"[ApplyAgent] DB insert failed (non-critical): {e}")
