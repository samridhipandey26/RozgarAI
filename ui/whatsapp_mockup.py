"""
ui/whatsapp_mockup.py — WhatsApp Chat Simulation Component
===========================================================
Renders a realistic WhatsApp-style chat panel showing the exact
messages Raju would see on his phone, including text, audio, and PDF cards.
"""

from __future__ import annotations

import base64
import os
from typing import List, Optional

import streamlit as st

from pipeline.state import MessageSender, WhatsAppMessage


ROZGAR_AVATAR = "🤖"
WORKER_AVATAR = "👷"


def render_whatsapp_panel(messages: List[WhatsAppMessage], phone_name: str = "Raju Kumar") -> None:
    """Render the full WhatsApp mockup panel."""

    # Inject WhatsApp-style CSS
    st.markdown(
        """
        <style>
        .wa-container {
            background: #0B141A;
            border-radius: 20px;
            overflow: hidden;
            font-family: 'Segoe UI', Arial, sans-serif;
            border: 1px solid #1E2D3A;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            max-height: 600px;
            display: flex;
            flex-direction: column;
        }
        .wa-header {
            background: linear-gradient(135deg, #0D1B2E 0%, #1A2E4A 100%);
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid #1E2D3A;
        }
        .wa-avatar {
            width: 40px; height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #F97316, #EA580C);
            display: flex; align-items: center; justify-content: center;
            font-size: 18px;
        }
        .wa-name { font-weight: 700; font-size: 15px; color: #E2E8F0; }
        .wa-status { font-size: 11px; color: #10B981; }
        .wa-body {
            flex: 1;
            padding: 12px;
            overflow-y: auto;
            background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E");
        }
        .wa-bubble-row-left {
            display: flex; justify-content: flex-start;
            margin-bottom: 8px; align-items: flex-end; gap: 8px;
        }
        .wa-bubble-row-right {
            display: flex; justify-content: flex-end;
            margin-bottom: 8px; align-items: flex-end; gap: 8px;
        }
        .wa-bubble-left {
            background: #1E2D3A;
            color: #E2E8F0;
            padding: 10px 14px;
            border-radius: 18px 18px 18px 4px;
            max-width: 78%;
            font-size: 13px;
            line-height: 1.5;
            box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }
        .wa-bubble-right {
            background: linear-gradient(135deg, #075E54, #128C7E);
            color: #fff;
            padding: 10px 14px;
            border-radius: 18px 18px 4px 18px;
            max-width: 78%;
            font-size: 13px;
            line-height: 1.5;
            box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }
        .wa-timestamp {
            font-size: 10px; color: #94A3B8;
            margin-top: 4px; text-align: right;
        }
        .wa-audio-bubble {
            background: #0D1B2E;
            border: 1px solid #F97316;
            border-radius: 12px;
            padding: 10px 14px;
            display: flex; align-items: center; gap: 10px;
            min-width: 180px;
        }
        .wa-audio-icon { font-size: 24px; }
        .wa-waveform {
            flex: 1;
            height: 24px;
            background: linear-gradient(90deg,
                #F97316 0%, #F97316 10%,
                #64748B 10%, #64748B 25%,
                #F97316 25%, #F97316 30%,
                #64748B 30%, #64748B 50%,
                #F97316 50%, #F97316 60%,
                #64748B 60%, #64748B 75%,
                #F97316 75%, #F97316 85%,
                #64748B 85%, #64748B 100%
            );
            border-radius: 4px;
            opacity: 0.7;
        }
        .wa-audio-dur { font-size: 11px; color: #94A3B8; }
        .wa-pdf-card {
            background: #0D1B2E;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px;
            min-width: 220px;
        }
        .wa-pdf-title { font-weight: 700; font-size: 13px; color: #F97316; }
        .wa-pdf-sub { font-size: 11px; color: #94A3B8; margin-top: 2px; }
        .wa-footer {
            background: #0D1B2E;
            padding: 8px 12px;
            border-top: 1px solid #1E2D3A;
            display: flex; align-items: center; gap: 8px;
        }
        .wa-input-mock {
            flex: 1; background: #1A2E4A;
            border-radius: 20px; padding: 8px 14px;
            color: #64748B; font-size: 13px;
        }
        .hindi-text { font-family: 'Noto Sans Devanagari', 'Arial Unicode MS', Arial, sans-serif; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Phone frame ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="wa-container">
        <div class="wa-header">
            <div class="wa-avatar">👷</div>
            <div>
                <div class="wa-name">{phone_name}</div>
                <div class="wa-status">● Online — RozgarAI</div>
            </div>
            <div style="margin-left:auto; font-size:18px; color:#94A3B8">📞 ⋮</div>
        </div>
        <div class="wa-body" id="wa-body">
    """, unsafe_allow_html=True)

    # ── Messages ────────────────────────────────────────────────────────────────
    if not messages:
        st.markdown("""
        <div style="text-align:center; color:#64748B; margin-top:40px; font-size:13px;">
            🔒 Messages are end-to-end encrypted<br/>
            <span style="font-size:11px;">Demo will start when you submit voice input</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in messages:
            _render_message(msg)

    # ── Close body + footer ────────────────────────────────────────────────────
    st.markdown("""
        </div>
        <div class="wa-footer">
            <span style="font-size:20px; color:#94A3B8">😊</span>
            <div class="wa-input-mock">Sandesh likhiye...</div>
            <span style="font-size:22px; color:#F97316">🎙️</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_message(msg: WhatsAppMessage) -> None:
    """Render a single WhatsApp message bubble."""
    is_worker = msg.sender == MessageSender.WORKER
    row_class    = "wa-bubble-row-right" if is_worker else "wa-bubble-row-left"
    bubble_class = "wa-bubble-right"     if is_worker else "wa-bubble-left"
    avatar       = WORKER_AVATAR if is_worker else ROZGAR_AVATAR

    avatar_html = f'<span style="font-size:22px;">{avatar}</span>'

    # ── Audio bubble ──────────────────────────────────────────────────────────
    if msg.audio_label:
        content_html = f"""
        <div class="wa-audio-bubble">
            <span class="wa-audio-icon">▶️</span>
            <div class="wa-waveform"></div>
            <span class="wa-audio-dur">{msg.audio_label.split("(")[-1].rstrip(")") if "(" in msg.audio_label else "0:08"}</span>
        </div>
        <div class="wa-timestamp">{msg.timestamp} ✓✓</div>
        """
        if msg.pdf_label:
            content_html += _pdf_card_html(msg.pdf_label)
    # ── PDF card only ──────────────────────────────────────────────────────────
    elif msg.pdf_label:
        content_html = _pdf_card_html(msg.pdf_label)
        content_html += f'<div class="wa-timestamp">{msg.timestamp} ✓✓</div>'
    # ── Text bubble ───────────────────────────────────────────────────────────
    else:
        text_escaped = (msg.text or "").replace("\n", "<br/>")
        # Bold markdown
        import re
        text_escaped = re.sub(r"\*(.+?)\*", r"<strong>\1</strong>", text_escaped)
        content_html = f"""
        <div class="{bubble_class} hindi-text">{text_escaped}</div>
        <div class="wa-timestamp">{msg.timestamp} {'✓✓' if not is_worker else '✓'}</div>
        """

    if is_worker:
        st.markdown(f"""
        <div class="{row_class}">
            <div>{content_html}</div>
            {avatar_html}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="{row_class}">
            {avatar_html}
            <div>{content_html}</div>
        </div>
        """, unsafe_allow_html=True)


def _pdf_card_html(label: str) -> str:
    return f"""
    <div class="wa-pdf-card">
        <div style="font-size:24px;">📄</div>
        <div class="wa-pdf-title hindi-text">{label}</div>
        <div class="wa-pdf-sub">PDF Document • RozgarAI</div>
    </div>
    """


def render_pdf_download_button(pdf_bytes: bytes, filename: str) -> None:
    """Show a styled download button for the resume PDF."""
    if not pdf_bytes:
        return
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'data:application/pdf;base64,{b64}'
    st.markdown(
        f"""
        <a href="{href}" download="{filename}" style="
            display: inline-block;
            background: linear-gradient(135deg, #F97316, #EA580C);
            color: white; padding: 10px 20px; border-radius: 10px;
            text-decoration: none; font-weight: 700; font-size: 13px;
            margin-top: 8px; box-shadow: 0 4px 15px rgba(249,115,22,0.3);
        ">📥 Resume Download करें (PDF)</a>
        """,
        unsafe_allow_html=True,
    )
