"""agents/status_tracker.py — Agent 7: Status Tracker"""
from __future__ import annotations

from datetime import datetime, timedelta

from pipeline.state import PipelineStage, RozgarState
from ui.strings_hi import TRACE_STATUS_DONE, WHATSAPP_STATUS_DONE


def status_tracker(state: RozgarState) -> RozgarState:
    """
    Agent 7 — Status Tracker
    Input:  state.session_id, state.apply_otp
    Output: state.status_message_hindi
    """
    try:
        state.current_stage = PipelineStage.STATUS_TRACK

        job = state.selected_job
        otp = state.apply_otp or "----"
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d %B")
        location = job.location if job else "bataye gaye jagah"
        job_title = job.title_hindi if job else "kaam"

        status_msg = WHATSAPP_STATUS_DONE.format(
            job_title=job_title,
            otp=otp,
            date=tomorrow,
            location=location,
        )

        state.status_message_hindi = status_msg
        state.add_wa_message("bot", status_msg)

        # Update session in DB
        _update_session(state)

        state.current_stage = PipelineStage.DONE
        state.log(TRACE_STATUS_DONE)

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _update_session(state: RozgarState) -> None:
    try:
        import json
        from db.models import get_session, AppSession
        with get_session() as db:
            sess = db.get(AppSession, state.session_id)
            if sess:
                sess.stage_reached = "done"
                sess.outcome       = "applied"
            else:
                matched_ids = json.dumps(
                    [j.job_id for j in state.matched_jobs]
                )
                db.add(AppSession(
                    session_id=state.session_id,
                    worker_phone=state.worker.phone if state.worker else "",
                    stage_reached="done",
                    transcript=state.transcript_hindi or "",
                    matched_job_ids=matched_ids,
                    outcome="applied",
                ))
            db.commit()
    except Exception as e:
        print(f"[StatusTracker] DB update failed (non-critical): {e}")
