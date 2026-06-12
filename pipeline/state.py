"""
pipeline/state.py — Typed RozgarState
Exact schema per spec. No loose dicts between agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PipelineStage(str, Enum):
    VOICE_INTAKE     = "voice_intake"
    SKILL_EXTRACT    = "skill_extract"
    RESUME_BUILD     = "resume_build"
    JOB_MATCH        = "job_match"
    INTERVIEW_COACH  = "interview_coach"
    APPLY            = "apply"
    STATUS_TRACK     = "status_track"
    DONE             = "done"
    ERROR            = "error"


@dataclass
class WorkerProfile:
    worker_id: str
    name: str
    phone: str
    city: str
    pin_code: str
    skills: List[str] = field(default_factory=list)
    experience_years: int = 0
    preferred_wage_per_day: int = 0
    languages: List[str] = field(default_factory=lambda: ["hindi"])


@dataclass
class JobListing:
    job_id: str
    contractor_id: str
    title: str
    title_hindi: str
    location: str
    pin_code: str
    wage_per_day: int
    skills_required: List[str]
    start_date: str
    openings: int
    distance_km: Optional[float] = None
    match_score: Optional[float] = None   # 0.0–1.0 composite score


@dataclass
class RozgarState:
    # ── Identity ──────────────────────────────────────────────────────────────
    session_id: str

    # ── Stage 1: Voice Intake ─────────────────────────────────────────────────
    raw_audio_path: Optional[str] = None
    transcript_hindi: Optional[str] = None
    transcript_english: Optional[str] = None

    # ── Stage 2: Skill Extractor ──────────────────────────────────────────────
    worker: Optional[WorkerProfile] = None

    # ── Stage 3: Resume Builder ───────────────────────────────────────────────
    resume_pdf_path: Optional[str] = None

    # ── Stage 4: Job Matcher ──────────────────────────────────────────────────
    matched_jobs: List[JobListing] = field(default_factory=list)

    # ── Stage 5: Interview Coach ──────────────────────────────────────────────
    selected_job: Optional[JobListing] = None
    interview_tips: List[str] = field(default_factory=list)

    # ── Stage 6: Apply Agent ──────────────────────────────────────────────────
    apply_confirmed: Optional[bool] = None   # HARD GATE — must be True
    apply_otp: Optional[str] = None

    # ── Stage 7: Status Tracker ───────────────────────────────────────────────
    status_message_hindi: Optional[str] = None

    # ── Meta ──────────────────────────────────────────────────────────────────
    current_stage: PipelineStage = PipelineStage.VOICE_INTAKE
    error_message: Optional[str] = None
    trace_log: List[str] = field(default_factory=list)   # Pipeline viz feed
    whatsapp_messages: List[dict] = field(default_factory=list)  # {role, text}

    # ── Demo mode flag ────────────────────────────────────────────────────────
    demo_mode: bool = False

    def add_wa_message(self, role: str, text: str) -> None:
        """role: 'bot' | 'worker'"""
        self.whatsapp_messages.append({"role": role, "text": text})

    def log(self, msg: str) -> None:
        self.trace_log.append(msg)
