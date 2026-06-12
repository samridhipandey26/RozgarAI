"""
app.py — RozgarAI Streamlit Demo
==================================
Entry point: streamlit run app.py

3-column layout:
  LEFT (25%)  — Worker input panel
  CENTER (45%)— Live agent pipeline trace + results
  RIGHT (30%) — WhatsApp mockup
  BOTTOM      — Stats bar
"""

from __future__ import annotations

import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── Load .env ──────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

import streamlit as st

# ── Page config — MUST be first Streamlit call ─────────────────────────────────
st.set_page_config(
    page_title="RozgarAI — Kaam Khojo. Kaam Do. Aaj.",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inject CSS ─────────────────────────────────────────────────────────────────
css_path = ROOT / "ui" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)

# ── Imports ─────────────────────────────────────────────────────────────────────
from pipeline.state  import PipelineStage, RozgarState
from pipeline.runner import make_state, run_pipeline_streaming
from ui.components   import (
    render_header, render_agent_trace, render_trace_log,
    render_job_cards, render_interview_tips, render_worker_card,
    render_whatsapp, render_stats_bar, render_pdf_download, render_confetti,
)
from ui.strings_hi   import DEMO_WORKER_INTRO, UI_CITY_LABEL, SKILL_CANONICAL

UP_CITIES = [
    "Lucknow", "Kanpur", "Agra", "Varanasi", "Allahabad",
    "Meerut", "Gorakhpur", "Bareilly", "Aligarh", "Moradabad",
]

# ─────────────────────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────

def _init_session():
    defaults = {
        "state":          None,      # RozgarState
        "pipeline_gen":   None,      # generator from run_pipeline_streaming
        "completed":      [],        # agent names done
        "running":        None,
        "elapsed_ms":     {},
        "agent_started":  {},        # {agent: time.time()}
        "phase":          "input",   # input | running | consent | done | error
        "selected_job":   None,
        "demo_mode":      True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────

render_header()
_init_session()

# ─────────────────────────────────────────────────────────────────────────────
# Layout
# ─────────────────────────────────────────────────────────────────────────────

left, center, right = st.columns([1, 1.8, 1.2], gap="medium")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LEFT — Worker Input Panel
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with left:
    st.markdown('<div class="section-label">WORKER INPUT</div>', unsafe_allow_html=True)

    demo_mode = st.toggle("Demo Mode (Raju ka profile)", value=True, key="demo_toggle")
    st.session_state.demo_mode = demo_mode

    if demo_mode:
        st.info(f"**Demo intro:** {DEMO_WORKER_INTRO}")
        name_val  = "Raju Kumar"
        city_val  = "Lucknow"
        skill_val = ["electrician"]
        wage_val  = 600
    else:
        name_val  = st.text_input("Aapka naam", placeholder="e.g. Ramesh Kumar")
        city_val  = st.selectbox(UI_CITY_LABEL, UP_CITIES)
        skill_val = st.multiselect("Aapka kaam (Skills)", SKILL_CANONICAL, default=["helper"])
        wage_val  = st.slider("Roz ki mazdoori (Rs/din)", 300, 1200, 500, step=50)

    audio_file = st.file_uploader(
        "Ya voice note upload karein (WAV/M4A)",
        type=["wav", "m4a", "mp3", "ogg"],
        key="audio_uploader",
    )

    st.markdown("---")

    # ── Worker profile card (after pipeline runs) ─────────────────────────────
    state: RozgarState = st.session_state.state
    if state and state.worker:
        render_worker_card(state.worker)

    if state and state.resume_pdf_path:
        render_pdf_download(state.resume_pdf_path, state.worker.name if state.worker else "worker")

    # ── CTA ───────────────────────────────────────────────────────────────────
    st.markdown("")
    can_run = st.session_state.phase in ("input", "done", "error")

    if st.button(
        "Kaam Dhundo" if can_run else "Pipeline chal rahi hai...",
        type="primary",
        use_container_width=True,
        disabled=not can_run,
        key="cta_btn",
    ):
        # Save audio if uploaded
        audio_path = None
        if audio_file:
            audio_path = str(ROOT / "data" / "temp" / audio_file.name)
            Path(audio_path).parent.mkdir(parents=True, exist_ok=True)
            with open(audio_path, "wb") as f:
                f.write(audio_file.read())

        # Build initial state
        new_state = make_state(
            demo_mode=demo_mode,
            audio_path=audio_path,
            session_id=uuid.uuid4().hex,
        )

        if not demo_mode:
            from pipeline.state import WorkerProfile
            new_state.worker = WorkerProfile(
                worker_id=f"w_{uuid.uuid4().hex[:8]}",
                name=name_val or "Kaamgar",
                phone="+919999999999",
                city=city_val,
                pin_code="226001",
                skills=skill_val or ["helper"],
                experience_years=2,
                preferred_wage_per_day=wage_val,
            )

        # Reset session
        st.session_state.state         = new_state
        st.session_state.completed     = []
        st.session_state.running       = None
        st.session_state.elapsed_ms    = {}
        st.session_state.agent_started = {}
        st.session_state.phase         = "running"
        st.session_state.pipeline_gen  = run_pipeline_streaming(new_state)
        st.session_state.selected_job  = None
        st.rerun()

    if state and st.button("Reset", use_container_width=True, key="reset_btn"):
        for k in ["state", "pipeline_gen", "completed", "running",
                  "elapsed_ms", "agent_started", "selected_job"]:
            st.session_state[k] = None if k in ("state","pipeline_gen","running","selected_job") else ([] if k in ("completed",) else {})
        st.session_state.phase = "input"
        st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CENTER — Pipeline Trace + Results
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with center:
    state: RozgarState = st.session_state.state

    # ── Agent pipeline trace ───────────────────────────────────────────────────
    render_agent_trace(
        completed   = st.session_state.completed,
        running     = st.session_state.running,
        elapsed_ms  = st.session_state.elapsed_ms,
        error_agent = None,
    )

    if state:
        render_trace_log(state.trace_log)

    # ── Advance pipeline one step ──────────────────────────────────────────────
    if st.session_state.phase == "running" and st.session_state.pipeline_gen:
        gen = st.session_state.pipeline_gen

        # Determine which agent is about to run
        AGENT_SEQ = [
            "voice_intake", "skill_extractor", "resume_builder",
            "job_matcher", "interview_coach", "apply_agent", "status_tracker",
        ]
        next_idx = len(st.session_state.completed)
        if next_idx < len(AGENT_SEQ):
            agent_name = AGENT_SEQ[next_idx]
            st.session_state.running = agent_name
            st.session_state.agent_started[agent_name] = time.time()

        try:
            t0 = time.time()
            updated_state = next(gen)
            elapsed = int((time.time() - t0) * 1000)

            # Mark previous agent done
            agent_name = AGENT_SEQ[min(next_idx, len(AGENT_SEQ)-1)]
            st.session_state.elapsed_ms[agent_name] = elapsed
            st.session_state.completed.append(agent_name)
            st.session_state.running = None
            st.session_state.state   = updated_state

            # Check if pipeline paused for consent
            if updated_state.apply_confirmed is None and \
               "interview_coach" in st.session_state.completed and \
               "apply_agent"     not in st.session_state.completed:
                st.session_state.phase = "consent"
            elif updated_state.current_stage == PipelineStage.DONE:
                st.session_state.phase = "done"
            elif updated_state.current_stage == PipelineStage.ERROR:
                st.session_state.phase = "error"

        except StopIteration:
            st.session_state.phase   = "done"
            st.session_state.running = None

        time.sleep(0.05)
        st.rerun()

    # ── Show job cards & tips after pipeline ──────────────────────────────────
    if state and state.matched_jobs:
        st.markdown("---")
        clicked = render_job_cards(state.matched_jobs)
        if clicked:
            state.selected_job = clicked
            st.session_state.selected_job = clicked

    if state and state.interview_tips:
        st.markdown("---")
        render_interview_tips(state.interview_tips)

    # ── Consent gate ──────────────────────────────────────────────────────────
    if st.session_state.phase == "consent":
        state = st.session_state.state
        job   = state.selected_job or (state.matched_jobs[0] if state.matched_jobs else None)
        if job:
            st.markdown("---")
            st.markdown(f"""
            <div style="background:#1A1A1A; border:2px solid #F97316; border-radius:12px;
                        padding:20px; text-align:center; margin:16px 0;">
                <div style="font-size:18px; font-weight:700; color:#F97316; font-family:'Baloo 2';">
                    {job.title_hindi} — ₹{job.wage_per_day}/din
                </div>
                <div style="font-size:14px; color:#9CA3AF; margin-top:6px;">
                    {job.location} &nbsp;•&nbsp; {job.start_date} se shuru
                </div>
                <div style="font-size:15px; color:#F5F5F5; margin-top:12px;">
                    Kya aap is kaam ke liye apply karna chahte hain?
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Haan — Apply Karo", type="primary",
                             use_container_width=True, key="consent_haan"):
                    state.apply_confirmed = True
                    state.selected_job    = job
                    state.add_wa_message("worker", "Haan")
                    # Resume the generator
                    gen = st.session_state.pipeline_gen
                    if gen is None:
                        from pipeline.runner import run_pipeline_streaming
                        gen = run_pipeline_streaming(state)
                        st.session_state.pipeline_gen = gen
                    st.session_state.state = state
                    st.session_state.phase = "running"
                    st.rerun()
            with col2:
                if st.button("Nahi — Chhoddo", use_container_width=True, key="consent_nahi"):
                    state.apply_confirmed = False
                    state.add_wa_message("worker", "Nahi")
                    st.session_state.state = state
                    st.session_state.phase = "done"
                    st.rerun()

    # ── Done state ────────────────────────────────────────────────────────────
    if st.session_state.phase == "done" and state and state.apply_otp:
        st.markdown("---")
        render_confetti()

    if st.session_state.phase == "error" and state and state.error_message:
        st.error(f"Pipeline error: {state.error_message}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RIGHT — WhatsApp Mockup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with right:
    st.markdown('<div class="section-label">WORKER KA WHATSAPP</div>', unsafe_allow_html=True)
    state = st.session_state.state
    messages = state.whatsapp_messages if state else []
    otp      = state.apply_otp if state else None
    render_whatsapp(messages, otp=otp if st.session_state.phase == "done" else None)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOTTOM — Stats Bar
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

render_stats_bar()
