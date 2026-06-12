"""
backend/routers/pipeline.py — 7-agent pipeline with SSE streaming
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.schemas.models import (
    PipelineStartResponse, PipelineConfirmRequest,
)

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])
security = HTTPBearer(auto_error=False)

# ── In-memory session store (replace with Redis in prod) ──────────────────────
_sessions: dict[str, dict] = {}


def _get_user(credentials: HTTPAuthorizationCredentials | None):
    """Validate JWT and return user_id. Returns 'demo' if no auth (dev mode)."""
    if not credentials:
        return "demo-user"
    try:
        from backend.db.supabase_client import get_supabase
        sb = get_supabase()
        if sb:
            user_resp = sb.auth.get_user(credentials.credentials)
            return user_resp.user.id
    except Exception:
        pass
    return "demo-user"


# ── Start pipeline ────────────────────────────────────────────────────────────

@router.post("/start", response_model=PipelineStartResponse)
async def start_pipeline(
    transcript: str = Form(default=""),
    audio: UploadFile | None = File(default=None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Start the 7-agent pipeline.
    Accepts either:
      - audio file (multipart) for voice onboarding
      - transcript text (form field) as text fallback
    Returns session_id to connect to SSE stream.
    """
    user_id = _get_user(credentials)
    session_id = uuid.uuid4().hex

    # Save audio if provided
    audio_path = None
    if audio and audio.filename:
        audio_dir = ROOT / "data" / "temp"
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = str(audio_dir / f"{session_id}_{audio.filename}")
        with open(audio_path, "wb") as f:
            f.write(await audio.read())

    # Initialize session
    _sessions[session_id] = {
        "user_id": user_id,
        "status": "initializing",
        "audio_path": audio_path,
        "transcript": transcript,
        "events": [],
        "apply_event": asyncio.Event(),
        "apply_confirmed": None,
        "state": None,
        "created_at": time.time(),
    }

    # Run pipeline in background
    asyncio.create_task(_run_pipeline_task(session_id))

    return PipelineStartResponse(session_id=session_id)


# ── SSE Stream ────────────────────────────────────────────────────────────────

@router.get("/stream/{session_id}")
async def stream_pipeline(session_id: str):
    """
    Server-Sent Events endpoint. Connect immediately after /start.
    Streams agent progress events in real time.
    """
    if session_id not in _sessions:
        raise HTTPException(404, "Session not found")

    return StreamingResponse(
        _sse_generator(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _sse_generator(session_id: str) -> AsyncGenerator[str, None]:
    """Yield SSE events as they arrive."""
    sent_idx = 0
    max_wait = 300  # 5 minute timeout

    yield f"data: {json.dumps({'event': 'connected', 'session_id': session_id})}\n\n"

    start = time.time()
    while time.time() - start < max_wait:
        session = _sessions.get(session_id)
        if not session:
            break

        events = session["events"]
        # Send any new events
        while sent_idx < len(events):
            evt = events[sent_idx]
            yield f"data: {json.dumps(evt)}\n\n"
            sent_idx += 1

            # If pipeline is done, close stream
            if evt.get("event") in ("pipeline_done", "pipeline_error"):
                return

        await asyncio.sleep(0.1)

    yield f"data: {json.dumps({'event': 'timeout'})}\n\n"


def _push_event(session_id: str, event: dict) -> None:
    """Thread-safe event push into session store."""
    if session_id in _sessions:
        _sessions[session_id]["events"].append(event)


# ── Pipeline Confirmation Gate ────────────────────────────────────────────────

@router.post("/confirm")
async def confirm_gate(req: PipelineConfirmRequest):
    """
    Called when worker clicks Haan (True) or Nahi (False).
    Unblocks the HARD GATE in the pipeline.
    """
    session = _sessions.get(req.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    session["apply_confirmed"] = req.confirmed
    session["apply_event"].set()

    return {"success": True, "confirmed": req.confirmed}


# ── Background Pipeline Task ──────────────────────────────────────────────────

async def _run_pipeline_task(session_id: str) -> None:
    """Run the full 7-agent pipeline asynchronously, pushing SSE events."""
    session = _sessions[session_id]
    user_id = session["user_id"]
    loop = asyncio.get_event_loop()

    def push(event_type: str, agent: str = None, latency_ms: int = None, data: dict = None):
        _push_event(session_id, {
            "event": event_type,
            "agent": agent,
            "latency_ms": latency_ms,
            "data": data or {},
            "timestamp": time.time(),
        })

    try:
        # Import pipeline
        from pipeline.state import RozgarState, PipelineStage
        from agents.voice_intake import voice_intake
        from agents.skill_extractor import skill_extractor
        from agents.resume_builder import resume_builder
        from agents.job_matcher import job_matcher
        from agents.interview_coach import interview_coach
        from agents.apply_agent import apply_agent
        from agents.status_tracker import status_tracker

        state = RozgarState(session_id=session_id)
        state.raw_audio_path = session.get("audio_path")
        state.demo_mode = False

        # Allow injecting a text transcript directly (fallback mode)
        if session.get("transcript"):
            state.transcript_hindi = session["transcript"]

        session["status"] = "running"
        session["state"] = state

        AGENTS = [
            ("voice_intake",    voice_intake),
            ("skill_extractor", skill_extractor),
            ("resume_builder",  resume_builder),
            ("job_matcher",     job_matcher),
            ("interview_coach", interview_coach),
        ]

        # ── Agents 1–5 ────────────────────────────────────────────────────────
        for agent_name, agent_fn in AGENTS:
            push("agent_started", agent=agent_name)
            t0 = time.time()

            try:
                # Run blocking agent in thread pool
                state = await loop.run_in_executor(None, agent_fn, state)
            except Exception as e:
                push("agent_error", agent=agent_name, data={"error": str(e)})
                push("pipeline_error", data={"error": str(e)})
                session["status"] = "error"
                return

            elapsed = int((time.time() - t0) * 1000)
            push("agent_completed", agent=agent_name, latency_ms=elapsed,
                 data=_agent_output(agent_name, state))

            if state.current_stage.value == "error":
                push("pipeline_error", data={"error": state.error_message})
                session["status"] = "error"
                return

        # ── HARD GATE: Haan/Nahi ──────────────────────────────────────────────
        matched = [
            {
                "id": getattr(j, "job_id", ""),
                "title": j.title,
                "title_hindi": j.title_hindi,
                "wage_per_day": j.wage_per_day,
                "location": j.location,
                "distance_km": j.distance_km,
                "match_score": j.match_score,
                "openings": j.openings,
                "start_date": j.start_date,
            }
            for j in state.matched_jobs
        ] if state.matched_jobs else []

        push("gate_reached", data={
            "gate": "apply",
            "matched_jobs": matched,
            "interview_tips": state.interview_tips,
            "resume_pdf_path": state.resume_pdf_path,
            "whatsapp_messages": state.whatsapp_messages,
        })

        # Wait for confirmation (up to 10 minutes)
        apply_event: asyncio.Event = session["apply_event"]
        try:
            await asyncio.wait_for(apply_event.wait(), timeout=600)
        except asyncio.TimeoutError:
            push("pipeline_error", data={"error": "Gate timeout — no response from user"})
            session["status"] = "timeout"
            return

        confirmed = session["apply_confirmed"]
        state.apply_confirmed = confirmed

        if not confirmed:
            push("pipeline_done", data={
                "confirmed": False,
                "message": "Application cancelled by worker",
            })
            session["status"] = "cancelled"
            return

        # ── Agent 6: Apply ────────────────────────────────────────────────────
        push("agent_started", agent="apply_agent")
        t0 = time.time()
        state = await loop.run_in_executor(None, apply_agent, state)
        elapsed = int((time.time() - t0) * 1000)
        push("agent_completed", agent="apply_agent", latency_ms=elapsed,
             data={"otp": state.apply_otp})

        # ── Agent 7: Status Tracker ───────────────────────────────────────────
        push("agent_started", agent="status_tracker")
        t0 = time.time()
        state = await loop.run_in_executor(None, status_tracker, state)
        elapsed = int((time.time() - t0) * 1000)
        push("agent_completed", agent="status_tracker", latency_ms=elapsed,
             data={"status": state.status_message_hindi})

        push("pipeline_done", data={
            "confirmed": True,
            "otp": state.apply_otp,
            "status_message": state.status_message_hindi,
            "whatsapp_messages": state.whatsapp_messages,
        })
        session["status"] = "done"
        session["state"] = state

    except Exception as e:
        push("pipeline_error", data={"error": str(e)})
        if session_id in _sessions:
            _sessions[session_id]["status"] = "error"


def _agent_output(agent_name: str, state) -> dict:
    """Extract a summary dict for each agent's SSE completion event."""
    if agent_name == "voice_intake":
        return {"transcript": (state.transcript_hindi or "")[:120]}
    if agent_name == "skill_extractor":
        w = state.worker
        return {
            "name": w.name if w else None,
            "city": w.city if w else None,
            "skill": (w.skills[0] if w and w.skills else None),
            "years_exp": w.experience_years if w else None,
        }
    if agent_name == "resume_builder":
        return {"pdf_path": state.resume_pdf_path}
    if agent_name == "job_matcher":
        return {"matches": len(state.matched_jobs)}
    if agent_name == "interview_coach":
        return {"tips_count": len(state.interview_tips)}
    return {}


# ── Session status (polling fallback) ─────────────────────────────────────────

@router.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """Polling fallback — returns current session state."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return {
        "session_id": session_id,
        "status": session["status"],
        "events_count": len(session["events"]),
    }
