"""
whatsapp/sender.py — Twilio WhatsApp Message Sender (Stub)
===========================================================
Production: sends real WhatsApp messages via Twilio API.
Prototype: logs to console and SQLite — no real messages sent.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

TWILIO_ENABLED = bool(
    os.getenv("TWILIO_ACCOUNT_SID") and
    os.getenv("TWILIO_AUTH_TOKEN") and
    os.getenv("TWILIO_WHATSAPP_FROM")
)


def send_text_message(to: str, body: str, session_id: str = None) -> bool:
    """
    Send a WhatsApp text message.
    Returns True on success, False on failure.
    """
    if TWILIO_ENABLED:
        return _send_twilio_text(to, body)
    else:
        _log_mock_message(to, body, "outbound-text", session_id)
        return True


def send_media_message(to: str, body: str, media_url: str, session_id: str = None) -> bool:
    """Send a WhatsApp message with media (audio/PDF)."""
    if TWILIO_ENABLED:
        return _send_twilio_media(to, body, media_url)
    else:
        _log_mock_message(to, f"{body} [media: {media_url}]", "outbound-media", session_id)
        return True


def send_audio_message(to: str, audio_bytes: bytes, session_id: str = None) -> bool:
    """
    Send a Hindi TTS audio message.
    In production: upload to S3/Cloudinary, send URL.
    In prototype: stub.
    """
    logger.info("[WhatsApp] STUB: Would send audio to %s (%d bytes)", to, len(audio_bytes))
    _log_mock_message(to, "[Audio Message]", "outbound-audio", session_id)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Twilio Implementation
# ─────────────────────────────────────────────────────────────────────────────

def _send_twilio_text(to: str, body: str) -> bool:
    try:
        from twilio.rest import Client
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
        )
        msg = client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            to=f"whatsapp:{to}" if not to.startswith("whatsapp:") else to,
            body=body,
        )
        logger.info("[WhatsApp] Sent message | sid=%s | to=%s", msg.sid, to)
        return True
    except Exception as e:
        logger.error("[WhatsApp] Twilio send failed: %s", e)
        return False


def _send_twilio_media(to: str, body: str, media_url: str) -> bool:
    try:
        from twilio.rest import Client
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
        )
        msg = client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            to=f"whatsapp:{to}" if not to.startswith("whatsapp:") else to,
            body=body,
            media_url=[media_url],
        )
        logger.info("[WhatsApp] Sent media | sid=%s | to=%s", msg.sid, to)
        return True
    except Exception as e:
        logger.error("[WhatsApp] Twilio media send failed: %s", e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Mock/Logging
# ─────────────────────────────────────────────────────────────────────────────

def _log_mock_message(to: str, body: str, direction: str, session_id: Optional[str]) -> None:
    logger.info("[WhatsApp-MOCK] %s → %s: %s", direction, to, body[:80])
    try:
        from data.db_init import log_whatsapp_message
        log_whatsapp_message(
            session_id=session_id or "unknown",
            direction=direction,
            body=body,
            sender="rozgarai",
        )
    except Exception:
        pass
