"""agents/apply_agent.py — Agent 6: Apply Agent (Production)
HARD GATE: apply_confirmed must be True. Writes to Supabase. Optional Twilio notify.
"""
from __future__ import annotations

import os
import random
import time
import uuid

from pipeline.state import PipelineStage, RozgarState


def apply_agent(state: RozgarState) -> RozgarState:
    """
    Agent 6 — Apply Agent
    HARD GATE: state.apply_confirmed must be True.
    Input:  state.worker, state.selected_job, state.apply_confirmed
    Output: state.apply_otp, state.application_id — Application saved to DB
    """
    try:
        state.current_stage = PipelineStage.APPLY

        # ── HARD GATE ──────────────────────────────────────────────────────────
        if state.apply_confirmed is not True:
            state.add_wa_message("bot", "Apply karne ke liye 'Haan' ka jawab den.")
            return state

        if state.worker is None or state.selected_job is None:
            raise ValueError("Worker or selected_job not set")

        state.log("📋 Apply Agent: Submitting application...")

        # 6-digit OTP for employer verification
        otp = str(random.randint(100000, 999999))
        state.apply_otp = otp

        app_id = str(uuid.uuid4())
        state.application_id = app_id

        user_id = getattr(state, "user_id", None) or state.worker.worker_id
        job_id = state.selected_job.job_id

        # Save to DB
        _insert_application(app_id, user_id, job_id, otp)

        # WhatsApp confirmation message
        state.add_wa_message(
            "bot",
            f"✅ Application jama ho gayi!\n\n"
            f"🔧 {state.selected_job.title_hindi}\n"
            f"📍 {state.selected_job.location}\n"
            f"💰 ₹{state.selected_job.wage_per_day}/din\n"
            f"📅 {state.selected_job.start_date} se shuru\n\n"
            f"🔑 Aapka OTP: {otp}\n"
            f"(Is number ko contractor ko batayein jab kaam shuru ho)"
        )

        # Notify employer (Twilio optional)
        _notify_employer(state)

        state.log("✅ Apply Agent: Application submitted successfully")

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _insert_application(app_id: str, user_id: str, job_id: str, otp: str) -> None:
    """Save application to Supabase or SQLite."""
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    try:
        from backend.db.supabase_client import sb_insert, supabase_available
        if supabase_available():
            sb_insert("applications", {
                "id": app_id,
                "worker_id": user_id,
                "job_id": job_id,
                "status": "applied",
                "otp": otp,
                "applied_at": now,
            })
            return
    except Exception as e:
        print(f"[ApplyAgent] Supabase insert failed: {e}")

    # SQLite fallback
    try:
        from db.models import get_session, Application, Job
        with get_session() as session:
            session.add(Application(
                application_id=app_id,
                worker_id=user_id,
                job_id=job_id,
                status="applied",
                otp=otp,
            ))
            # Decrement openings
            job_row = session.get(Job, job_id)
            if job_row and job_row.openings > 0:
                job_row.openings -= 1
                job_row.filled += 1
            session.commit()
    except Exception as e:
        print(f"[ApplyAgent] SQLite insert failed (non-critical): {e}")


def _notify_employer(state: RozgarState) -> None:
    """Send SMS/WhatsApp to employer via Twilio if configured."""
    try:
        sid   = os.getenv("TWILIO_ACCOUNT_SID", "")
        token = os.getenv("TWILIO_AUTH_TOKEN", "")
        from_ = os.getenv("TWILIO_FROM", "")
        if not (sid and token and from_):
            return

        job = state.selected_job
        employer_name = job.employer_name if job else "Employer"
        msg = (
            f"RozgarAI: {state.worker.name} ne aapke '{job.title}' ke liye apply kiya hai! "
            f"OTP: {state.apply_otp}. Dashboard par dekhen."
        )

        from twilio.rest import Client
        client = Client(sid, token)

        # Try to get employer phone from Supabase
        try:
            from backend.db.supabase_client import sb_select
            employers = sb_select("user_roles", {"user_id": job.contractor_id}, limit=1)
            if employers and employers[0].get("phone"):
                client.messages.create(body=msg, from_=from_, to=employers[0]["phone"])
        except Exception:
            pass

    except Exception as e:
        print(f"[ApplyAgent] Twilio notify failed (non-critical): {e}")
