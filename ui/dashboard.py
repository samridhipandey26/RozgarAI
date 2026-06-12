"""
ui/dashboard.py — RozgarAI Main Streamlit Dashboard
=====================================================
The hackathon demo interface. Visualizes the entire 7-agent pipeline
in real-time with a WhatsApp chat mockup and live agent traces.

Run: streamlit run ui/dashboard.py
"""

from __future__ import annotations

import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# Ensure project root is on the path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from pipeline.state import AgentStatus, RozgarState, WhatsAppMessage
from pipeline.orchestrator import PipelineEvent, RozgarOrchestrator
import strings_hi as hi

# ─────────────────────────────────────────────────────────────────────────────
# Page Config — Must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RozgarAI — Agentic Career Platform",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS Injection
# ─────────────────────────────────────────────────────────────────────────────

def inject_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0 !important; }

    /* ── Branding Header ──────────────────────────────────────────────────── */
    .rozgar-header {
        background: linear-gradient(135deg, #0D1B2E 0%, #1A2E4A 50%, #0D1B2E 100%);
        border-bottom: 2px solid #F97316;
        padding: 16px 24px;
        margin: -1rem -1rem 1rem -1rem;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .rozgar-logo-text {
        font-size: 28px; font-weight: 800; color: #F97316;
        letter-spacing: -0.5px;
    }
    .rozgar-tagline {
        font-size: 13px; color: #94A3B8; margin-top: 2px;
    }
    .rozgar-badge {
        background: rgba(249,115,22,0.15);
        border: 1px solid #F97316;
        color: #F97316;
        padding: 4px 12px; border-radius: 20px;
        font-size: 11px; font-weight: 600;
        margin-left: auto;
    }

    /* ── Section Headers ─────────────────────────────────────────────────── */
    .section-title {
        font-size: 13px; font-weight: 700;
        color: #94A3B8; letter-spacing: 1px;
        text-transform: uppercase; margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #1A2E4A;
    }

    /* ── Input Area ──────────────────────────────────────────────────────── */
    .input-card {
        background: #1A2E4A;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #334155;
        margin-bottom: 16px;
    }
    .mic-button {
        font-size: 40px;
        text-align: center;
        padding: 16px;
        cursor: pointer;
    }

    /* ── Profile Card ─────────────────────────────────────────────────────── */
    .profile-card {
        background: linear-gradient(135deg, #1A2E4A 0%, #0D1B2E 100%);
        border-radius: 16px;
        padding: 16px;
        border: 1px solid #F97316;
        margin-top: 12px;
    }
    .profile-name {
        font-size: 18px; font-weight: 700; color: #F97316;
    }
    .profile-role {
        font-size: 13px; color: #E2E8F0; margin-top: 4px;
    }
    .profile-meta {
        font-size: 11px; color: #94A3B8; margin-top: 8px;
    }
    .profile-skill-tag {
        display: inline-block;
        background: rgba(249,115,22,0.1);
        border: 1px solid rgba(249,115,22,0.3);
        color: #F97316; padding: 2px 8px;
        border-radius: 12px; font-size: 10px;
        margin: 2px;
    }

    /* ── Job Cards ──────────────────────────────────────────────────────── */
    .job-card {
        background: #1A2E4A;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #334155;
        margin-bottom: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .job-card:hover { border-color: #F97316; transform: translateY(-1px); }
    .job-card.selected { border-color: #F97316; background: #1E3A5F; }
    .job-employer { font-size: 14px; font-weight: 700; color: #E2E8F0; }
    .job-role { font-size: 12px; color: #94A3B8; margin-top: 2px; }
    .job-salary { font-size: 16px; font-weight: 700; color: #10B981; }
    .match-badge {
        display: inline-block;
        background: linear-gradient(135deg, #064E3B, #065F46);
        border: 1px solid #10B981;
        color: #10B981; padding: 2px 10px;
        border-radius: 12px; font-size: 12px; font-weight: 700;
    }

    /* ── Coaching Q&A ────────────────────────────────────────────────────── */
    .coach-question {
        background: #1A2E4A;
        border-left: 4px solid #F97316;
        border-radius: 0 12px 12px 0;
        padding: 16px;
        margin-bottom: 12px;
        font-family: 'Noto Sans Devanagari', 'Inter', sans-serif;
        font-size: 15px;
        color: #E2E8F0;
    }
    .coach-feedback {
        background: #064E3B;
        border: 1px solid #10B981;
        border-radius: 12px;
        padding: 12px;
        font-size: 13px;
        color: #A7F3D0;
        margin-top: 8px;
    }
    .readiness-score {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #0D1B2E, #1A2E4A);
        border-radius: 16px;
        border: 1px solid #F97316;
    }

    /* ── Buttons ──────────────────────────────────────────────────────────── */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(249,115,22,0.3) !important;
    }

    /* ── Status Timeline ─────────────────────────────────────────────────── */
    .status-dot {
        display: inline-block;
        width: 12px; height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-row {
        display: flex; align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #1A2E4A;
        font-size: 13px;
    }

    /* ── Demo Mode Banner ─────────────────────────────────────────────────── */
    .demo-banner {
        background: linear-gradient(135deg, #7C2D12, #9A3412);
        border: 1px solid #F97316;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 12px;
        color: #FED7AA;
        margin-bottom: 16px;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────

def init_session() -> None:
    defaults = {
        "state":            None,       # RozgarState
        "orchestrator":     None,       # RozgarOrchestrator
        "pipeline_thread":  None,       # threading.Thread
        "pipeline_running": False,
        "pipeline_stage":   "input",    # input/running/coaching/apply/tracking/done
        "coaching_step":    0,          # 0, 1, 2
        "last_event_count": 0,
        "auto_refresh":     False,
        "selected_job_idx": None,
        "coaching_responses": [],
        "coaching_feedback":  [],
        "rerun_requested":   False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# Event Queue Drainer
# ─────────────────────────────────────────────────────────────────────────────

def drain_events() -> bool:
    """Process all pending events from the orchestrator queue. Returns True if any events."""
    orch: Optional[RozgarOrchestrator] = st.session_state.orchestrator
    if not orch:
        return False

    q = orch.get_event_queue()
    had_events = False
    while not q.empty():
        try:
            event = q.get_nowait()
            _handle_event(event)
            had_events = True
        except queue.Empty:
            break
    return had_events


def _handle_event(event: Dict[str, Any]) -> None:
    evt_type = event.get("type")
    data     = event.get("data", {})
    state: RozgarState = st.session_state.state

    if evt_type == PipelineEvent.AGENT_STARTED:
        pass  # State already updated by orchestrator

    elif evt_type == PipelineEvent.AGENT_COMPLETED:
        agent_num = data.get("agent_num", 0)
        if agent_num == 4:
            # After job matching, move to job selection stage
            st.session_state.pipeline_stage = "job_selection"
        elif agent_num == 5:
            st.session_state.pipeline_stage = "coaching_done"

    elif evt_type == PipelineEvent.GATE_REACHED:
        gate = data.get("gate")
        if gate == "resume":
            st.session_state.pipeline_stage = "resume_gate"
        elif gate == "apply":
            st.session_state.pipeline_stage = "apply_gate"

    elif evt_type == PipelineEvent.GATE_PASSED:
        pass

    elif evt_type == PipelineEvent.PIPELINE_DONE:
        st.session_state.pipeline_stage  = "done"
        st.session_state.pipeline_running = False


# ─────────────────────────────────────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    inject_css()
    init_session()

    state: Optional[RozgarState] = st.session_state.state

    # ── Drain pipeline events ──────────────────────────────────────────────────
    if st.session_state.pipeline_running:
        drain_events()

    # ── Branding Header ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="rozgar-header">
        <div>
            <div class="rozgar-logo-text">🔶 RozgarAI</div>
            <div class="rozgar-tagline">Aapki Naukri, Aapki Awaz — Agentic Career Platform for India</div>
        </div>
        <div class="rozgar-badge">🏆 Hackathon Demo</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Three-column layout ────────────────────────────────────────────────────
    left, center, right = st.columns([1, 2, 1], gap="medium")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LEFT PANEL — Input + Profile
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with left:
        st.markdown('<div class="section-title">📱 Worker Input</div>', unsafe_allow_html=True)
        _render_input_panel()

        if state and state.profile:
            st.markdown('<div class="section-title" style="margin-top:20px;">👷 Worker Profile</div>',
                        unsafe_allow_html=True)
            _render_profile_card(state.profile)

        if state and state.job_matches:
            st.markdown('<div class="section-title" style="margin-top:20px;">💼 Job Matches</div>',
                        unsafe_allow_html=True)
            _render_job_cards(state)

        if state and state.resume_pdf:
            from ui.whatsapp_mockup import render_pdf_download_button
            render_pdf_download_button(
                state.resume_pdf,
                f"resume_{(state.profile or {}).get('name', 'worker').replace(' ','_')}.pdf"
            )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CENTER PANEL — Agent Timeline + Pipeline Viz
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with center:
        st.markdown('<div class="section-title">🤖 Agent Pipeline — Live Trace</div>',
                    unsafe_allow_html=True)

        if state:
            from ui.agent_trace import render_agent_trace
            render_agent_trace(state.agent_traces, state.current_agent)

            # Coaching Q&A (inline in center panel)
            if st.session_state.pipeline_stage in ("coaching", "coaching_done"):
                _render_coaching_ui(state)

            # Gate buttons
            stage = st.session_state.pipeline_stage
            if stage == "resume_gate":
                _render_resume_gate(state)
            elif stage == "apply_gate":
                _render_apply_gate(state)

        else:
            _render_empty_trace()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # RIGHT PANEL — WhatsApp Mockup
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with right:
        st.markdown('<div class="section-title">📱 Worker\'s WhatsApp</div>', unsafe_allow_html=True)
        from ui.whatsapp_mockup import render_whatsapp_panel
        messages = state.whatsapp_messages if state else []
        worker_name = (state.profile or {}).get("name", "Raju Kumar") if state else "Raju Kumar"
        render_whatsapp_panel(messages, worker_name)

    # ── Bottom: Pipeline Diagram ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">🔄 Pipeline State Machine</div>', unsafe_allow_html=True)

    if state:
        total_ms = None
        if state.timestamps.get("pipeline_start") and state.timestamps.get("pipeline_end"):
            total_ms = int((state.timestamps["pipeline_end"] - state.timestamps["pipeline_start"]) * 1000)
        elif state.timestamps.get("pipeline_start") and st.session_state.pipeline_running:
            total_ms = int((time.time() - state.timestamps["pipeline_start"]) * 1000)

        from ui.pipeline_viz import render_pipeline_viz, render_pipeline_status_bar
        render_pipeline_viz(state.agent_traces, state.current_agent, total_ms)
        render_pipeline_status_bar(state.agent_traces, state.current_agent, total_ms)
    else:
        _render_empty_pipeline()

    # ── Auto-refresh while pipeline running ───────────────────────────────────
    if st.session_state.pipeline_running:
        time.sleep(0.8)
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Input Panel
# ─────────────────────────────────────────────────────────────────────────────

def _render_input_panel() -> None:
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
    has_keys  = bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))

    if not has_keys:
        st.markdown("""
        <div class="demo-banner">
            🚀 <strong>Demo Mode Active</strong> — No API keys needed!
            All agents will use intelligent mock data.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="mic-button">🎙️</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center; font-size:12px; color:#94A3B8; margin-bottom:12px;">'
        'Hindi mein boliye ya type karein</div>',
        unsafe_allow_html=True,
    )

    # Demo pre-fill button
    demo_text = "Main 5 saal se truck loading ka kaam karta hoon, Muzaffarnagar mein rehta hoon"
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📋 Demo", key="demo_fill", help="Fill demo text"):
            st.session_state["voice_input_text"] = demo_text

    with col1:
        voice_input = st.text_area(
            "Aap kya kaam karte ho?",
            value=st.session_state.get("voice_input_text", ""),
            placeholder=demo_text,
            height=80,
            key="voice_input_area",
            label_visibility="collapsed",
        )

    # Audio file upload
    audio_file = st.file_uploader(
        "Ya voice note upload karein (OGG/MP3)",
        type=["ogg", "mp3", "wav", "m4a"],
        key="audio_upload",
        label_visibility="collapsed",
    )

    # Mock mode toggle
    use_mock = st.checkbox(
        "🔧 Mock mode (no API keys)",
        value=not has_keys,
        key="mock_toggle",
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Start button
    can_start = bool(voice_input.strip() or audio_file)
    if st.button(
        "🚀 RozgarAI Shuru Karo",
        key="start_btn",
        disabled=not can_start or st.session_state.pipeline_running,
        type="primary",
        use_container_width=True,
    ):
        _start_pipeline(
            text_input=voice_input.strip() if voice_input else None,
            audio_file=audio_file,
            mock_mode=use_mock or not has_keys,
        )
        st.rerun()

    # Reset button
    if st.session_state.state is not None:
        if st.button("🔄 Nayi Shuruaat (Reset)", key="reset_btn", use_container_width=True):
            _reset_session()
            st.rerun()


def _start_pipeline(
    text_input: Optional[str],
    audio_file: Any,
    mock_mode: bool,
) -> None:
    """Initialize state and launch orchestrator thread."""
    from data.db_init import init_db
    try:
        init_db()
    except Exception:
        pass

    state = RozgarState(mock_mode=mock_mode)

    if audio_file:
        state.audio_file     = audio_file.read()
        state.audio_filename = audio_file.name
        state.add_worker_message(None)
        state.whatsapp_messages[-1].audio_label = f"🎙️ Voice Note (0:08)"

    if text_input:
        state.raw_text_input = text_input

    state.add_rozgar_message(text=hi.GREETING)

    orch = RozgarOrchestrator(state)

    thread = threading.Thread(
        target=orch.run_pipeline,
        daemon=True,
        name="rozgar-pipeline",
    )
    thread.start()

    st.session_state.state            = state
    st.session_state.orchestrator     = orch
    st.session_state.pipeline_thread  = thread
    st.session_state.pipeline_running = True
    st.session_state.pipeline_stage   = "running"


def _reset_session() -> None:
    if st.session_state.orchestrator:
        st.session_state.orchestrator.stop()
    for key in ["state", "orchestrator", "pipeline_thread", "pipeline_running",
                "pipeline_stage", "coaching_step", "coaching_responses",
                "coaching_feedback", "selected_job_idx"]:
        if key in st.session_state:
            del st.session_state[key]
    if "voice_input_text" in st.session_state:
        del st.session_state["voice_input_text"]


# ─────────────────────────────────────────────────────────────────────────────
# Profile Card
# ─────────────────────────────────────────────────────────────────────────────

def _render_profile_card(profile: Dict[str, Any]) -> None:
    name    = profile.get("name") or "Karmchari"
    role    = profile.get("role_hindi") or profile.get("role") or "Worker"
    exp     = profile.get("experience_years")
    loc     = profile.get("location") or profile.get("city") or ""
    skills  = profile.get("skills") or []

    skills_html = "".join(
        f'<span class="profile-skill-tag">{s}</span>'
        for s in skills[:6]
    )

    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-name">👷 {name}</div>
        <div class="profile-role">{role}</div>
        <div class="profile-meta">
            {'📅 ' + str(exp) + ' saal | ' if exp else ''}
            {'📍 ' + loc if loc else ''}
        </div>
        <div style="margin-top:10px;">{skills_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Job Cards
# ─────────────────────────────────────────────────────────────────────────────

def _render_job_cards(state: RozgarState) -> None:
    stage = st.session_state.pipeline_stage
    selected_idx = st.session_state.selected_job_idx

    for i, job in enumerate(state.job_matches):
        is_selected = (selected_idx == i)
        card_class = "job-card selected" if is_selected else "job-card"

        role_hi  = job.get("role_hindi") or job.get("role", "")
        dist     = job.get("distance_km", "?")
        salary   = f"₹{job['salary']:,}" if job.get("salary") else ""

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div class="job-employer">{job['employer']}</div>
                    <div class="job-role">{role_hi} • {job.get('shift','Day')} Shift</div>
                    <div class="job-role">📍 {job.get('location','')}
                        {f'• {dist} km' if dist != '?' else ''}</div>
                </div>
                <div style="text-align:right;">
                    <div class="match-badge">{job['match_score']}% match</div>
                    <div class="job-salary" style="margin-top:6px;">{salary}/maah</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Selection button (only shown when not selected and in job_selection stage)
        if stage == "job_selection" and not is_selected:
            if st.button(f"✅ Yeh job chunein", key=f"select_job_{i}", use_container_width=True):
                _select_job(state, i)
                st.rerun()
        elif is_selected:
            st.success("✅ Chunli gayi! Interview taiyari shuru ho rahi hai...")


def _select_job(state: RozgarState, idx: int) -> None:
    """Worker selects a job. Unblock orchestrator to continue to Agent 5."""
    state.selected_job       = state.job_matches[idx]
    state.selected_job_index = idx
    st.session_state.selected_job_idx  = idx
    st.session_state.pipeline_stage    = "coaching"

    # Add to WhatsApp
    employer = state.selected_job.get("employer", "")
    role_hi  = state.selected_job.get("role_hindi") or state.selected_job.get("role")
    state.add_worker_message(f"2")  # Worker types "2" to select
    state.add_rozgar_message(text=hi.JOB_SELECTED.format(employer=employer))

    # The orchestrator's Agent 5 runs after job_selection; it checks state.selected_job
    # Since orchestrator is waiting, we signal it by providing the job selection
    # and let it proceed to Agent 5 (which it does after Agent 4 returns)


# ─────────────────────────────────────────────────────────────────────────────
# Resume Confirmation Gate
# ─────────────────────────────────────────────────────────────────────────────

def _render_resume_gate(state: RozgarState) -> None:
    st.markdown("---")
    st.markdown("""
    <div style="background:#1A2E4A; border:2px solid #F97316; border-radius:16px;
                padding:20px; text-align:center; margin:16px 0;">
        <div style="font-size:20px; margin-bottom:8px;">📋</div>
        <div style="font-size:16px; font-weight:700; color:#F97316; margin-bottom:4px;
                    font-family:'Noto Sans Devanagari',Arial;">
            Resume taiyaar ho gayi!
        </div>
        <div style="font-size:14px; color:#E2E8F0; font-family:'Noto Sans Devanagari',Arial;">
            Kya sab sahi hai? Haan ya Nahi chunein.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ HAAN — Sahi Hai", key="resume_haan",
                     type="primary", use_container_width=True):
            _pass_gate("resume", True, state)
            st.rerun()
    with col2:
        if st.button("❌ NAHI — Dobara Karo", key="resume_nahi",
                     use_container_width=True):
            _pass_gate("resume", False, state)
            st.rerun()


def _render_apply_gate(state: RozgarState) -> None:
    job = state.selected_job or {}
    employer = job.get("employer", "Employer")
    role_hi  = job.get("role_hindi") or job.get("role", "")

    st.markdown("---")
    st.markdown(f"""
    <div style="background:#1A2E4A; border:2px solid #10B981; border-radius:16px;
                padding:20px; text-align:center; margin:16px 0;">
        <div style="font-size:20px; margin-bottom:8px;">🎯</div>
        <div style="font-size:15px; font-weight:700; color:#10B981; margin-bottom:8px;
                    font-family:'Noto Sans Devanagari',Arial;">
            {employer} mein {role_hi} ke liye apply karna chahte ho?
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 HAAN — Apply Karo", key="apply_haan",
                     type="primary", use_container_width=True):
            state.add_worker_message("Haan")
            _pass_gate("apply", True, state)
            st.rerun()
    with col2:
        if st.button("🚫 NAHI — Nahi Chahiye", key="apply_nahi",
                     use_container_width=True):
            state.add_worker_message("Nahi")
            _pass_gate("apply", False, state)
            st.rerun()


def _pass_gate(gate: str, confirmed: bool, state: RozgarState) -> None:
    orch: Optional[RozgarOrchestrator] = st.session_state.orchestrator
    if orch:
        orch.provide_confirmation(gate, confirmed)
    if gate == "resume":
        if confirmed:
            state.add_worker_message("Haan")
            state.add_rozgar_message(text=hi.RESUME_CONFIRMED)
            st.session_state.pipeline_stage = "running"
        else:
            state.add_worker_message("Nahi")
            state.add_rozgar_message(text=hi.RESUME_REJECTED)
            st.session_state.pipeline_stage = "done"
            st.session_state.pipeline_running = False


# ─────────────────────────────────────────────────────────────────────────────
# Interview Coaching Q&A UI
# ─────────────────────────────────────────────────────────────────────────────

def _render_coaching_ui(state: RozgarState) -> None:
    from agents.interview_coach import generate_feedback, compute_readiness_score

    session = state.coaching_session
    if not session:
        return

    questions = session.get("questions", [])
    step = st.session_state.coaching_step
    responses = st.session_state.coaching_responses
    feedback_list = st.session_state.coaching_feedback

    st.markdown("---")
    st.markdown("""
    <div style="font-size:14px; font-weight:700; color:#F97316; margin-bottom:12px;">
        🎯 Interview Coaching
    </div>
    """, unsafe_allow_html=True)

    # Show completed Q&As
    for i, (q, resp, fb) in enumerate(zip(questions[:step], responses, feedback_list)):
        st.markdown(f"""
        <div class="coach-question">
            <strong>Sawaal {i+1}:</strong> {q}
        </div>
        """, unsafe_allow_html=True)
        st.success(f"✅ Aapka jawab: {resp}")
        if fb:
            st.markdown(f'<div class="coach-feedback">💬 {fb}</div>', unsafe_allow_html=True)

    # Current question
    if step < len(questions) and st.session_state.pipeline_stage == "coaching":
        q = questions[step]
        st.markdown(f"""
        <div class="coach-question">
            <strong>Sawaal {step+1}:</strong> {q}
        </div>
        """, unsafe_allow_html=True)

        response = st.text_input(
            "Aapka jawab:",
            key=f"coaching_ans_{step}",
            placeholder="Hindi mein jawab dein...",
        )

        if st.button("✅ Jawab Bhejo", key=f"coaching_submit_{step}",
                     disabled=not response.strip()):
            # Add message to WhatsApp
            state.add_worker_message(response)

            # Get feedback
            fb = generate_feedback(q, response, state)
            state.add_rozgar_message(
                text=hi.COACH_FEEDBACK_GOOD.format(feedback=fb)
            )

            responses.append(response)
            feedback_list.append(fb)
            st.session_state.coaching_responses = responses
            st.session_state.coaching_feedback  = feedback_list
            st.session_state.coaching_step = step + 1

            # Ask next question
            next_step = step + 1
            if next_step < len(questions):
                state.add_rozgar_message(
                    text=hi.COACH_QUESTION_PREFIX.format(
                        num=next_step+1,
                        question=questions[next_step],
                    )
                )
            st.rerun()

    # Coaching complete
    if step >= len(questions) and step > 0:
        session["responses"] = responses
        score = compute_readiness_score(session)
        session["readiness_score"] = score
        session["complete"] = True
        state.coaching_session = session

        stars = "⭐" * score + "☆" * (5 - score)
        st.markdown(f"""
        <div class="readiness-score">
            <div style="font-size:24px;">{stars}</div>
            <div style="font-size:18px; font-weight:700; color:#F97316; margin:8px 0;">
                {hi.COACH_READINESS.format(score=score)}
            </div>
            <div style="font-size:14px; color:#A7F3D0;">{hi.COACH_COMPLETE}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.pipeline_stage == "coaching":
            st.session_state.pipeline_stage = "apply_gate"
            # Unblock the orchestrator to continue to Agent 6
            # The orchestrator returns from Agent 5, then waits for apply gate
            state.add_rozgar_message(
                text=f"🎉 {hi.COACH_COMPLETE}\n\n"
                     f"Ab apply karte hain?"
            )
            orch: Optional[RozgarOrchestrator] = st.session_state.orchestrator
            # The apply gate is handled by _render_apply_gate


# ─────────────────────────────────────────────────────────────────────────────
# Empty State Renderers
# ─────────────────────────────────────────────────────────────────────────────

def _render_empty_trace() -> None:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; color:#64748B;">
        <div style="font-size:48px; margin-bottom:16px;">🤖</div>
        <div style="font-size:16px; font-weight:600; color:#94A3B8;">Agent Pipeline Ready</div>
        <div style="font-size:13px; margin-top:8px;">
            Input submit karo to pipeline shuru hogi.<br/>
            Har agent real-time mein yahan dikhega.
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_empty_pipeline() -> None:
    from ui.pipeline_viz import render_pipeline_viz
    from pipeline.state import AgentTrace, AgentStatus
    empty_traces = [AgentTrace(i+1, f"Agent {i+1}") for i in range(7)]
    render_pipeline_viz(empty_traces)


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
