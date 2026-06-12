"""
pipeline/state.py — Typed RozgarState (Production v2)
Extended with lat/lng, user_id, languages, and Supabase-compatible fields.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PipelineStage(str, Enum):
    VOICE_INTAKE    = "voice_intake"
    SKILL_EXTRACT   = "skill_extract"
    RESUME_BUILD    = "resume_build"
    JOB_MATCH       = "job_match"
    INTERVIEW_COACH = "interview_coach"
    APPLY           = "apply"
    STATUS_TRACK    = "status_track"
    DONE            = "done"
    ERROR           = "error"


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
    languages: List[str] = field(default_factory=lambda: ["Hindi"])
    education: str = "Not specified"
    # Real geocoordinates — set by skill_extractor via Nominatim
    lat: Optional[float] = None
    lng: Optional[float] = None


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
    lat: Optional[float] = None
    lng: Optional[float] = None
    distance_km: Optional[float] = None
    match_score: Optional[float] = None   # 0.0–1.0 composite score
    employer_name: Optional[str] = None


@dataclass
class RozgarState:
    # ── Identity ────────────────────────────────────────────────────────────
    session_id: str
    user_id: Optional[str] = None          # Supabase auth user UUID

    # ── Stage 1: Voice Intake ────────────────────────────────────────────────
    raw_audio_path: Optional[str] = None
    transcript_hindi: Optional[str] = None
    transcript_english: Optional[str] = None

    # ── Stage 2: Skill Extractor ─────────────────────────────────────────────
    worker: Optional[WorkerProfile] = None

    # ── Stage 3: Resume Builder ──────────────────────────────────────────────
    resume_pdf_path: Optional[str] = None
    resume_pdf_url: Optional[str] = None   # Supabase Storage URL

    # ── Stage 4: Job Matcher ─────────────────────────────────────────────────
    matched_jobs: List[JobListing] = field(default_factory=list)

    # ── Stage 5: Interview Coach ─────────────────────────────────────────────
    selected_job: Optional[JobListing] = None
    interview_tips: List[str] = field(default_factory=list)

    # ── Stage 6: Apply Agent ─────────────────────────────────────────────────
    apply_confirmed: Optional[bool] = None   # HARD GATE — must be True
    apply_otp: Optional[str] = None
    application_id: Optional[str] = None

    # ── Stage 7: Status Tracker ──────────────────────────────────────────────
    status_message_hindi: Optional[str] = None
    application_status: Optional[str] = None  # applied|contacted|confirmed|completed

    # ── Meta ─────────────────────────────────────────────────────────────────
    current_stage: PipelineStage = PipelineStage.VOICE_INTAKE
    error_message: Optional[str] = None
    trace_log: List[str] = field(default_factory=list)
    whatsapp_messages: List[dict] = field(default_factory=list)  # {role, text}

    # ── Legacy compat ─────────────────────────────────────────────────────────
    demo_mode: bool = False  # Always False in production

    def add_wa_message(self, role: str, text: str) -> None:
        """role: 'bot' | 'worker'"""
        self.whatsapp_messages.append({"role": role, "text": text})

    def log(self, msg: str) -> None:
        self.trace_log.append(msg)
