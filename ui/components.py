"""
ui/components.py — Reusable Streamlit Component Functions
==========================================================
All components are pure functions — no global state.
No pipeline imports (agents stay independently testable).
"""
from __future__ import annotations

import base64
from datetime import datetime
from typing import List, Optional

import streamlit as st

from pipeline.state import JobListing, PipelineStage, RozgarState, WorkerProfile
from ui.strings_hi import PIPELINE_STAGE_LABELS, PIPELINE_STAGE_EMOJI, SKILL_LABELS_HI


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

def render_header() -> None:
    st.markdown("""
    <div class="rz-header">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="12" r="8" fill="#F97316" opacity="0.2"/>
            <path d="M16 4 C11.6 4 8 7.6 8 12 C8 18 16 28 16 28 C16 28 24 18 24 12 C24 7.6 20.4 4 16 4Z"
                  fill="#F97316"/>
            <circle cx="16" cy="12" r="4" fill="#0D0D0D"/>
            <path d="M13 15 L10 18 L12 20 L15 17 M19 9 L22 6 L20 4 L17 7" stroke="#F97316"
                  stroke-width="2" stroke-linecap="round"/>
        </svg>
        <div>
            <div class="rz-logo">RozgarAI</div>
            <div class="rz-tagline">Kaam Khojo. Kaam Do. Aaj. &nbsp;|&nbsp; काम खोजो। काम दो। आज।</div>
        </div>
        <div class="rz-badge">HACKATHON DEMO</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AGENT PIPELINE TRACE
# ─────────────────────────────────────────────────────────────────────────────

AGENT_NAMES_HI = {
    "voice_intake":    "1. Awaaz intake",
    "skill_extractor": "2. Kaam ki pehchaan",
    "resume_builder":  "3. Resume banana",
    "job_matcher":     "4. Job matching",
    "interview_coach": "5. Interview tips",
    "apply_agent":     "6. Application bhejna",
    "status_tracker":  "7. Status update",
}

AGENT_ORDER = [
    "voice_intake", "skill_extractor", "resume_builder",
    "job_matcher",  "interview_coach", "apply_agent", "status_tracker",
]


def render_agent_trace(
    completed: List[str],
    running: Optional[str],
    elapsed_ms: dict,
    error_agent: Optional[str] = None,
) -> None:
    """
    Render the 7-agent pipeline trace.
    completed: list of agent names that finished
    running:   currently active agent name (or None)
    elapsed_ms: {agent_name: milliseconds}
    """
    st.markdown('<div class="section-label">LIVE AGENT PIPELINE</div>', unsafe_allow_html=True)

    for agent in AGENT_ORDER:
        if agent == error_agent:
            dot_class = "agent-dot-error"
            row_class = "agent-row error"
        elif agent in completed:
            dot_class = "agent-dot-done"
            row_class = "agent-row done"
        elif agent == running:
            dot_class = "agent-dot-running"
            row_class = "agent-row running"
        else:
            dot_class = "agent-dot-pending"
            row_class = "agent-row"

        ms = elapsed_ms.get(agent)
        time_str = f"{ms}ms" if ms else "—"
        emoji = PIPELINE_STAGE_EMOJI.get(agent.replace("_", "_"), "")

        st.markdown(f"""
        <div class="{row_class}">
            <div class="agent-dot {dot_class}"></div>
            <span class="agent-name">{AGENT_NAMES_HI.get(agent, agent)}</span>
            <span class="agent-time">{time_str}</span>
        </div>
        """, unsafe_allow_html=True)


def render_trace_log(log_entries: List[str]) -> None:
    if not log_entries:
        return
    lines = "\n".join(f"> {e}" for e in log_entries)
    st.markdown(f'<div class="log-console">{lines}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# JOB CARDS
# ─────────────────────────────────────────────────────────────────────────────

def render_job_cards(jobs: List[JobListing]) -> Optional[JobListing]:
    """Render job cards. Returns the job the user clicked (or None)."""
    selected = None
    st.markdown('<div class="section-label">AAPKE LIYE NAUKRI</div>', unsafe_allow_html=True)

    for i, job in enumerate(jobs):
        pct = int((job.match_score or 0) * 100)
        dist = f"{job.distance_km} km" if job.distance_km else "nearby"
        skills_html = " ".join(
            f'<span class="skill-pill">{s}</span>'
            for s in job.skills_required[:3]
        )
        st.markdown(f"""
        <div class="job-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div class="job-title">{job.title_hindi}</div>
                    <div style="font-size:12px; color:#9CA3AF;">{job.title}</div>
                    <div class="job-meta">📍 {job.location} &nbsp;•&nbsp; {dist} door</div>
                    <div class="job-meta">📅 {job.start_date} se shuru &nbsp;•&nbsp; {job.openings} jagah</div>
                    <div style="margin-top:8px;">{skills_html}</div>
                </div>
                <div style="text-align:right;">
                    <div class="job-wage">₹{job.wage_per_day}/din</div>
                    <div style="margin-top:6px;"><span class="match-badge">{pct}% match</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Is job ke liye apply karo", key=f"job_select_{i}"):
            selected = job

    return selected


# ─────────────────────────────────────────────────────────────────────────────
# INTERVIEW TIPS
# ─────────────────────────────────────────────────────────────────────────────

def render_interview_tips(tips: List[str]) -> None:
    st.markdown('<div class="section-label">INTERVIEW TIPS</div>', unsafe_allow_html=True)
    for i, tip in enumerate(tips, 1):
        st.markdown(f"""
        <div class="tip-card">
            <div class="tip-number">TIP {i}</div>
            {tip}
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# WORKER PROFILE CARD
# ─────────────────────────────────────────────────────────────────────────────

def render_worker_card(worker: WorkerProfile) -> None:
    skills_html = " ".join(
        f'<span class="skill-pill">{SKILL_LABELS_HI.get(s, s)}</span>'
        for s in worker.skills
    )
    st.markdown(f"""
    <div class="job-card" style="border-left-color: #22C55E;">
        <div style="font-size:20px; font-weight:800; color:#F5F5F5; font-family:'Baloo 2';">
            👷 {worker.name}
        </div>
        <div style="font-size:12px; color:#6B7280; margin: 4px 0;">
            📍 {worker.city} &nbsp;•&nbsp; {worker.experience_years} saal ka experience
        </div>
        <div style="font-size:12px; color:#22C55E;">
            ₹{worker.preferred_wage_per_day}/din chahiye
        </div>
        <div style="margin-top:10px;">{skills_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# WHATSAPP MOCKUP
# ─────────────────────────────────────────────────────────────────────────────

def render_whatsapp(messages: List[dict], otp: Optional[str] = None) -> None:
    st.markdown("""
    <div class="whatsapp-container">
        <div class="whatsapp-header">
            <div class="whatsapp-avatar">🔧</div>
            <div>
                <div class="whatsapp-name">RozgarAI Bot</div>
                <div class="whatsapp-status">● Online</div>
            </div>
        </div>
        <div class="whatsapp-body">
    """, unsafe_allow_html=True)

    now = datetime.now().strftime("%H:%M")

    for msg in messages:
        role    = msg.get("role", "bot")
        text    = msg.get("text", "")
        is_user = role == "worker"
        cls     = "whatsapp-bubble-outgoing" if is_user else "whatsapp-bubble-incoming"
        text_html = text.replace("\n", "<br/>")

        st.markdown(f"""
        <div style="display:flex; justify-content:{'flex-end' if is_user else 'flex-start'}; margin-bottom:4px;">
            <div>
                <div class="{cls}">{text_html}</div>
                <div class="whatsapp-timestamp">{now} {'✓✓' if is_user else ''}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # OTP big display
    if otp:
        st.markdown(f'<div class="otp-display">{otp}</div>', unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# STATS BAR
# ─────────────────────────────────────────────────────────────────────────────

def render_stats_bar() -> None:
    """Pull stats from SQLite and render bottom stats bar."""
    workers, jobs_filled, avg_wage, cities = _get_stats()
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-block">
            <div class="stat-value">{workers}</div>
            <div class="stat-label">Workers Registered</div>
        </div>
        <div class="stat-block">
            <div class="stat-value">{jobs_filled}</div>
            <div class="stat-label">Jobs Filled Today</div>
        </div>
        <div class="stat-block">
            <div class="stat-value">₹{avg_wage}</div>
            <div class="stat-label">Avg Daily Wage</div>
        </div>
        <div class="stat-block">
            <div class="stat-value">{cities}</div>
            <div class="stat-label">Active Cities</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _get_stats():
    try:
        from db.models import get_session, Worker, Application, Job
        from sqlalchemy import func, distinct
        with get_session() as db:
            workers = db.query(func.count(Worker.worker_id)).scalar() or 0
            today_str = datetime.now().strftime("%Y-%m-%d")
            jobs_filled = db.query(func.count(Application.application_id)).filter(
                Application.applied_at.like(f"{today_str}%")
            ).scalar() or 0
            avg_wage = db.query(func.avg(Job.wage_per_day)).scalar()
            avg_wage = int(avg_wage) if avg_wage else 625
            cities = db.query(func.count(distinct(Job.location.op("LIKE")("% %")))).scalar() or 8
        return workers, jobs_filled, avg_wage, cities
    except Exception:
        return 247, 12, 625, 8


# ─────────────────────────────────────────────────────────────────────────────
# PDF DOWNLOAD BUTTON
# ─────────────────────────────────────────────────────────────────────────────

def render_pdf_download(pdf_path: str, worker_name: str) -> None:
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(
            f'<a href="data:application/pdf;base64,{b64}" '
            f'download="{worker_name}_resume.pdf" '
            f'style="display:inline-block; background:#F97316; color:white; '
            f'padding:8px 20px; border-radius:8px; font-weight:700; text-decoration:none; '
            f'font-size:13px; margin-top:8px;">'
            f'Resume Download (PDF)</a>',
            unsafe_allow_html=True,
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# CONFETTI
# ─────────────────────────────────────────────────────────────────────────────

def render_confetti() -> None:
    st.markdown("""
    <div class="confetti-wrap">🎉 🎊 🎉</div>
    <div style="text-align:center; font-family:'Baloo 2'; font-size:18px; color:#22C55E; margin-top:8px;">
        Ho gaya! Raju ka kaam pakka!
    </div>
    """, unsafe_allow_html=True)
    st.balloons()
