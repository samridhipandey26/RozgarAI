"""
ui/agent_trace.py — Live Agent Timeline Component
==================================================
Renders the real-time agent pipeline trace panel in the Streamlit dashboard.
Each agent card shows status, timing, input/output JSON, and LLM prompt.
"""

from __future__ import annotations

import json
import time
from typing import List, Optional

import streamlit as st

from pipeline.state import AgentStatus, AgentTrace


# Status colors and icons
STATUS_CONFIG = {
    AgentStatus.WAITING:  {"color": "#64748B", "icon": "⏳", "label": "Waiting"},
    AgentStatus.RUNNING:  {"color": "#F59E0B", "icon": "⚡", "label": "Running"},
    AgentStatus.DONE:     {"color": "#10B981", "icon": "✅", "label": "Done"},
    AgentStatus.ERROR:    {"color": "#EF4444", "icon": "❌", "label": "Error"},
    AgentStatus.SKIPPED:  {"color": "#94A3B8", "icon": "⏭️", "label": "Skipped"},
}

AGENT_DESCRIPTIONS = {
    1: "Transcribes Hindi voice via Whisper API",
    2: "Extracts structured profile via Claude Sonnet",
    3: "Generates bilingual PDF + Hindi TTS audio",
    4: "Semantic job matching via embeddings",
    5: "Hindi interview coaching — 3 questions",
    6: "Submits application to employer",
    7: "Real-time status tracking & notifications",
}


def render_agent_trace(traces: List[AgentTrace], current_agent: int = 0) -> None:
    """Render the full agent timeline panel."""

    st.markdown(
        """
        <style>
        .agent-card {
            background: #1A2E4A;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            border-left: 4px solid #334155;
            transition: all 0.3s ease;
        }
        .agent-card.running {
            border-left-color: #F59E0B;
            box-shadow: 0 0 20px rgba(249, 115, 22, 0.2);
            animation: pulse 1.5s infinite;
        }
        .agent-card.done {
            border-left-color: #10B981;
        }
        .agent-card.error {
            border-left-color: #EF4444;
        }
        .status-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .timing-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 11px;
            background: #0D1B2E;
            color: #94A3B8;
            margin-left: 8px;
        }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 10px rgba(249, 115, 22, 0.2); }
            50%       { box-shadow: 0 0 25px rgba(249, 115, 22, 0.5); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    for trace in traces:
        _render_agent_card(trace, current_agent)


def _render_agent_card(trace: AgentTrace, current_agent: int) -> None:
    """Render a single agent card."""
    cfg = STATUS_CONFIG[trace.status]
    is_active = (trace.agent_num == current_agent and trace.status == AgentStatus.RUNNING)
    card_class = f"agent-card {trace.status.value}"

    # Build card HTML header
    timing_html = ""
    if trace.elapsed_ms is not None:
        timing_html = f'<span class="timing-badge">⏱ {trace.elapsed_ms}ms</span>'
    elif trace.status == AgentStatus.RUNNING:
        timing_html = '<span class="timing-badge">⏱ running...</span>'

    st.markdown(
        f"""
        <div class="{card_class}">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <span style="font-size:22px;">{cfg['icon']}</span>
                <span style="font-weight:700; font-size:14px; color:#E2E8F0;">
                    Agent {trace.agent_num} — {trace.agent_name}
                </span>
                <span class="status-badge" style="background:{cfg['color']}20; color:{cfg['color']};">
                    {cfg['label']}
                </span>
                {timing_html}
            </div>
            <div style="font-size:11px; color:#94A3B8; margin-bottom:8px;">
                {AGENT_DESCRIPTIONS.get(trace.agent_num, '')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Expandable sections (only show if agent has run)
    if trace.status in (AgentStatus.DONE, AgentStatus.RUNNING, AgentStatus.ERROR):

        col1, col2, col3 = st.columns(3)

        # Input payload
        with col1:
            if trace.input_payload:
                with st.expander("📥 Input", expanded=False):
                    st.json(trace.input_payload)

        # Output payload
        with col2:
            if trace.output_payload:
                with st.expander("📤 Output", expanded=(trace.status == AgentStatus.DONE)):
                    st.json(trace.output_payload)

        # LLM Prompt
        with col3:
            if trace.llm_prompt:
                with st.expander("🧠 LLM Prompt", expanded=False):
                    st.code(trace.llm_prompt, language="text")

        # Error message
        if trace.error_message:
            st.error(f"❌ Error: {trace.error_message}")
