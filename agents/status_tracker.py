"""agents/status_tracker.py — Agent 7: Status Tracker (Production)
Polls Supabase for real application status. Emits Hindi status message.
"""
from __future__ import annotations

from pipeline.state import PipelineStage, RozgarState

STATUS_MESSAGES_HI = {
    "applied":   "✅ Aapki application jama ho gayi hai. Contractor ka intezaar karein.",
    "contacted": "📞 Contractor ne aapko contact kiya hai! Apna phone check karein.",
    "confirmed": "🎉 Badhai! Aapka kaam pakka ho gaya. Samay par pahunchen.",
    "completed": "🏆 Kaam safaltapoorvak pura hua. Bahut badhiya!",
    "rejected":  "😔 Is baar nahin mila. Doosri naukri try karein.",
}

STATUS_MESSAGES_EN = {
    "applied":   "Application submitted. Waiting for contractor.",
    "contacted": "Contractor has reached out! Check your phone.",
    "confirmed": "Congratulations! Job confirmed. Show up on time.",
    "completed": "Job successfully completed!",
    "rejected":  "Not selected this time. Try another job.",
}


def status_tracker(state: RozgarState) -> RozgarState:
    """
    Agent 7 — Status Tracker
    Input:  state.application_id
    Output: state.status_message_hindi, state.application_status
    Updates application status from DB.
    """
    try:
        state.current_stage = PipelineStage.STATUS_TRACK

        app_id = state.application_id
        if not app_id:
            state.status_message_hindi = STATUS_MESSAGES_HI["applied"]
            state.application_status = "applied"
            state.log("⚠️ Status Tracker: No application_id — using default status")
            return state

        state.log("📊 Status Tracker: Checking application status...")
        status = _fetch_status(app_id)

        state.application_status = status
        state.status_message_hindi = STATUS_MESSAGES_HI.get(status, STATUS_MESSAGES_HI["applied"])

        state.add_wa_message("bot", state.status_message_hindi)
        state.log(f"✅ Status Tracker: Status = {status}")

        # Log to pipeline_logs table
        _log_pipeline(state)

        state.current_stage = PipelineStage.DONE

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _fetch_status(app_id: str) -> str:
    """Fetch application status from Supabase or SQLite."""
    try:
        from backend.db.supabase_client import sb_select, supabase_available
        if supabase_available():
            apps = sb_select("applications", limit=1)
            apps = [a for a in apps if str(a.get("id")) == app_id]
            if apps:
                return apps[0].get("status", "applied")
    except Exception as e:
        print(f"[StatusTracker] Supabase fetch failed: {e}")

    try:
        import sqlite3
        from pathlib import Path
        db_path = Path(__file__).parent.parent / "data" / "rozgar.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            row = conn.execute(
                "SELECT status FROM applications WHERE id=?", (app_id,)
            ).fetchone()
            conn.close()
            return row[0] if row else "applied"
    except Exception:
        pass

    return "applied"


def _log_pipeline(state: RozgarState) -> None:
    """Save pipeline trace to pipeline_logs table."""
    try:
        from backend.db.supabase_client import sb_insert, supabase_available
        import time
        if not supabase_available():
            return

        user_id = getattr(state, "user_id", None) or (state.worker.worker_id if state.worker else None)
        for log_entry in state.trace_log:
            # Extract agent name from log entry if possible
            agent = "pipeline"
            if ":" in log_entry:
                parts = log_entry.split(":")
                agent = parts[0].strip().lstrip("✅⚠️🎙️🔍📄💬📊📋").strip()

            sb_insert("pipeline_logs", {
                "worker_id": user_id,
                "session_id": state.session_id,
                "agent_name": agent,
                "status": "done",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
    except Exception as e:
        print(f"[StatusTracker] Pipeline log save failed (non-critical): {e}")
