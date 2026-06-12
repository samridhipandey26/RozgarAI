"""
pipeline/orchestrator.py — RozgarAI Agent Orchestrator
=======================================================
Sequential pipeline runner that calls each agent in order,
tracks timing, handles errors, and notifies the dashboard
via a callback queue for real-time UI updates.
"""

from __future__ import annotations

import logging
import os
import queue
import threading
import time
from typing import Any, Callable, Dict, Optional

from pipeline.state import AgentStatus, RozgarState

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Event types pushed to Streamlit via callback queue
# ─────────────────────────────────────────────────────────────────────────────

class PipelineEvent:
    AGENT_STARTED    = "agent_started"
    AGENT_COMPLETED  = "agent_completed"
    AGENT_ERROR      = "agent_error"
    GATE_REACHED     = "gate_reached"       # Waiting for Haan/Nahi
    GATE_PASSED      = "gate_passed"
    PIPELINE_DONE    = "pipeline_done"
    STATUS_UPDATE    = "status_update"      # Agent 7 status change
    MESSAGE_ADDED    = "message_added"      # WhatsApp message added


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class RozgarOrchestrator:
    """
    Drives the 7-agent pipeline.

    Usage (from Streamlit):
        orchestrator = RozgarOrchestrator(state)
        orchestrator.set_callback(lambda event, data: st.session_state.update(...))
        thread = threading.Thread(target=orchestrator.run_pipeline)
        thread.start()
        # Later:
        orchestrator.provide_confirmation("resume", True)
    """

    def __init__(self, state: RozgarState) -> None:
        self.state = state
        self._callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        self._event_queue: queue.Queue = queue.Queue()

        # Gate events — set() to unblock, cleared by orchestrator after reading
        self._resume_gate  = threading.Event()
        self._apply_gate   = threading.Event()
        self._resume_confirmed: Optional[bool] = None
        self._apply_confirmed: Optional[bool] = None

        self._stop_flag = threading.Event()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Register a callback to receive pipeline events (runs in pipeline thread)."""
        self._callback = callback

    def get_event_queue(self) -> queue.Queue:
        """Return the event queue for Streamlit to poll."""
        return self._event_queue

    def provide_confirmation(self, gate: str, confirmed: bool) -> None:
        """
        Called by Streamlit when user clicks Haan/Nahi.
        gate: 'resume' | 'apply'
        """
        if gate == "resume":
            self._resume_confirmed = confirmed
            self._resume_gate.set()
        elif gate == "apply":
            self._apply_confirmed = confirmed
            self._apply_gate.set()

    def stop(self) -> None:
        """Request pipeline stop (best effort)."""
        self._stop_flag.set()
        self._resume_gate.set()
        self._apply_gate.set()

    def run_pipeline(self) -> None:
        """
        Main pipeline execution — run in a background thread.
        Calls agents 1 through 7 sequentially with gate pauses.
        """
        # Import agents here to avoid circular imports at module level
        from agents.voice_intake    import transcribe_audio
        from agents.skill_extractor import extract_profile
        from agents.resume_builder  import build_resume
        from agents.job_matcher     import match_jobs
        from agents.interview_coach import run_coaching
        from agents.apply_agent     import submit_application
        from agents.status_tracker  import track_status

        self.state.timestamps["pipeline_start"] = time.time()

        try:
            # ── Agent 1: Voice Intake ──────────────────────────────────────────
            self._run_agent(1, transcribe_audio, {
                "audio_file": bool(self.state.audio_file),
                "raw_text": (self.state.raw_text_input or "")[:60],
            })
            if self._stop_flag.is_set():
                return

            # ── Agent 2: Skill Extractor ───────────────────────────────────────
            self._run_agent(2, extract_profile, {
                "transcript": (self.state.transcript or "")[:80],
            })
            if self._stop_flag.is_set():
                return

            # ── Agent 3: Resume Builder ────────────────────────────────────────
            self._run_agent(3, build_resume, {
                "profile_name": (self.state.profile or {}).get("name"),
                "profile_role": (self.state.profile or {}).get("role"),
            })
            if self._stop_flag.is_set():
                return

            # ──── GATE: Wait for resume confirmation ────────────────────────────
            self.state.awaiting_confirmation = "resume"
            self._emit(PipelineEvent.GATE_REACHED, {"gate": "resume"})
            logger.info("Pipeline paused at resume confirmation gate")

            self._resume_gate.wait()   # Block until Haan/Nahi
            self._resume_gate.clear()
            self.state.resume_confirmed = self._resume_confirmed
            self.state.awaiting_confirmation = None

            self._emit(PipelineEvent.GATE_PASSED, {
                "gate": "resume",
                "confirmed": self._resume_confirmed,
            })

            if not self._resume_confirmed:
                # Worker said Nahi — reset and restart from Agent 1
                logger.info("Resume rejected. Pipeline halted.")
                return

            # ── Agent 4: Job Matcher ───────────────────────────────────────────
            self._run_agent(4, match_jobs, {
                "role": (self.state.profile or {}).get("role"),
                "location": (self.state.profile or {}).get("location"),
            })
            if self._stop_flag.is_set():
                return

            # ──── GATE: Wait for job selection (set by dashboard) ────────────────
            # Job selection is handled by the dashboard directly writing to
            # state.selected_job; orchestrator waits on apply gate instead.

            # ── Agent 5: Interview Coach ───────────────────────────────────────
            self._run_agent(5, run_coaching, {
                "job": (self.state.selected_job or {}).get("role"),
                "employer": (self.state.selected_job or {}).get("employer"),
            })
            if self._stop_flag.is_set():
                return

            # ── Agent 6: Apply Agent ───────────────────────────────────────────
            # Gate: wait for apply confirmation
            self.state.awaiting_confirmation = "apply"
            self._emit(PipelineEvent.GATE_REACHED, {"gate": "apply"})
            self._apply_gate.wait()
            self._apply_gate.clear()
            self.state.apply_confirmed = self._apply_confirmed
            self.state.awaiting_confirmation = None

            self._emit(PipelineEvent.GATE_PASSED, {
                "gate": "apply",
                "confirmed": self._apply_confirmed,
            })

            if not self._apply_confirmed:
                return

            self._run_agent(6, submit_application, {
                "job_id": (self.state.selected_job or {}).get("job_id"),
                "employer": (self.state.selected_job or {}).get("employer"),
            })
            if self._stop_flag.is_set():
                return

            # ── Agent 7: Status Tracker ────────────────────────────────────────
            self._run_agent(7, track_status, {
                "application_id": self.state.application_id,
            })

        except Exception as exc:
            logger.exception("Pipeline crashed: %s", exc)
            self._emit(PipelineEvent.AGENT_ERROR, {"error": str(exc)})
        finally:
            self.state.timestamps["pipeline_end"] = time.time()
            self.state.pipeline_complete = True
            self._emit(PipelineEvent.PIPELINE_DONE, {
                "total_ms": int(
                    (self.state.timestamps.get("pipeline_end", time.time()) -
                     self.state.timestamps.get("pipeline_start", time.time())) * 1000
                )
            })

    # ── Private Helpers ───────────────────────────────────────────────────────

    def _run_agent(
        self,
        agent_num: int,
        agent_fn: Callable[[RozgarState], RozgarState],
        input_summary: Dict[str, Any],
    ) -> None:
        """Run a single agent, update trace, emit events."""
        trace = self.state.get_trace(agent_num)
        trace.input_payload = input_summary
        trace.mark_running()
        self.state.current_agent = agent_num

        self._emit(PipelineEvent.AGENT_STARTED, {
            "agent_num": agent_num,
            "agent_name": trace.agent_name,
        })

        try:
            updated_state = agent_fn(self.state)
            # Agent returns the same state object (mutated in place)
            # but we accept the return value for explicitness
            if updated_state is not None:
                self.state = updated_state

            output_payload = self._extract_output(agent_num)
            trace.mark_done(output_payload)

            self._emit(PipelineEvent.AGENT_COMPLETED, {
                "agent_num": agent_num,
                "agent_name": trace.agent_name,
                "elapsed_ms": trace.elapsed_ms,
                "output": output_payload,
            })

        except Exception as exc:
            error_msg = str(exc)
            trace.mark_error(error_msg)
            self.state.errors[f"agent_{agent_num}"] = error_msg
            logger.error("Agent %d error: %s", agent_num, error_msg)

            self._emit(PipelineEvent.AGENT_ERROR, {
                "agent_num": agent_num,
                "agent_name": trace.agent_name,
                "error": error_msg,
            })
            raise  # Re-raise to halt pipeline

    def _extract_output(self, agent_num: int) -> Dict[str, Any]:
        """Extract a loggable output summary for each agent."""
        s = self.state
        extracts = {
            1: {"transcript": (s.transcript or "")[:100]},
            2: {
                "name": (s.profile or {}).get("name"),
                "role": (s.profile or {}).get("role"),
                "experience_years": (s.profile or {}).get("experience_years"),
                "location": (s.profile or {}).get("location"),
                "skills": (s.profile or {}).get("skills", []),
            },
            3: {
                "pdf_generated": s.resume_pdf is not None,
                "tts_generated": s.resume_tts is not None,
                "pdf_path": s.resume_pdf_path,
            },
            4: {
                "matches_count": len(s.job_matches) if s.job_matches else 0,
                "top_match": (s.job_matches or [{}])[0].get("employer") if s.job_matches else None,
                "top_score": (s.job_matches or [{}])[0].get("match_score") if s.job_matches else None,
            },
            5: {
                "readiness_score": (s.coaching_session or {}).get("readiness_score"),
                "questions_asked": len((s.coaching_session or {}).get("questions", [])),
            },
            6: {
                "application_id": s.application_id,
                "submitted": s.application_submitted,
                "employer": (s.selected_job or {}).get("employer"),
            },
            7: {
                "final_status": s.application_status,
                "transitions": len(s.status_history),
            },
        }
        return extracts.get(agent_num, {})

    def _emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Push an event to the queue and call the optional callback."""
        payload = {"type": event_type, "data": data, "timestamp": time.time()}
        self._event_queue.put(payload)
        if self._callback:
            try:
                self._callback(event_type, data)
            except Exception:
                pass  # Never let callback crash the pipeline
