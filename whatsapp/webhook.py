"""
whatsapp/webhook.py — Twilio WhatsApp Webhook Handler
======================================================
FastAPI server that receives incoming WhatsApp messages from Twilio.
In production: routes to pipeline orchestrator.
In prototype: logs and returns TwiML stub response.

Run: uvicorn whatsapp.webhook:app --port 5001
Then expose via ngrok: ngrok http 5001
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import PlainTextResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="RozgarAI WhatsApp Webhook",
    description="Twilio webhook for incoming WhatsApp messages",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "RozgarAI WhatsApp Webhook"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From:    str = Form(default=""),
    Body:    str = Form(default=""),
    MediaUrl0: Optional[str] = Form(default=None),
    MediaContentType0: Optional[str] = Form(default=None),
    NumMedia: int = Form(default=0),
    MessageSid: str = Form(default=""),
) -> Response:
    """
    Twilio sends POST to this endpoint when worker sends a WhatsApp message.
    Expected format: multipart/form-data with Twilio fields.
    """
    logger.info(
        "[Webhook] Incoming WhatsApp | from=%s | body=%s | media=%s",
        From, Body[:50], NumMedia
    )

    # Log to DB
    try:
        from data.db_init import init_db, log_whatsapp_message
        init_db()
        log_whatsapp_message(
            session_id=_phone_to_session(From),
            direction="inbound",
            body=Body,
            sender=From,
        )
    except Exception as e:
        logger.warning("[Webhook] DB log failed: %s", e)

    # Route message
    response_text = _route_message(From, Body, MediaUrl0, MediaContentType0)

    # Return TwiML response
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""

    return Response(content=twiml, media_type="application/xml")


def _route_message(
    phone: str,
    body: str,
    media_url: Optional[str],
    media_content_type: Optional[str],
) -> str:
    """
    Route incoming message to appropriate handler.
    In prototype: returns static responses.
    In production: look up session, call orchestrator.provide_confirmation().
    """
    body_lower = body.strip().lower()

    # Haan/Nahi responses
    if body_lower in ("haan", "haa", "han", "yes", "हाँ", "हां"):
        return "Shukriya! Aapka confirmation mil gaya. Processing ho raha hai... ✅"

    if body_lower in ("nahi", "na", "no", "नहीं", "नही"):
        return "Theek hai! Koi baat nahi. Dobara try karein. 🙏"

    # Job selection (1, 2, 3)
    if body_lower in ("1", "2", "3"):
        return f"Aapne option {body} chuna. Processing ho rahi hai..."

    # Voice/audio note
    if media_url and "audio" in (media_content_type or ""):
        return f"Aapki awaaz sun li. Ek minute... 🎙️"

    # Default greeting
    return (
        "Namaste! Main RozgarAI hoon. 🔶\n"
        "Apna kaam aur shahar batao — main aapke liye sahi naukri dhundhunga!\n"
        "Boliye ya type karein."
    )


def _phone_to_session(phone: str) -> str:
    """Map phone number to session ID (simplified for prototype)."""
    import hashlib
    clean = phone.replace("whatsapp:", "").replace("+", "").replace("-", "")
    return hashlib.md5(clean.encode()).hexdigest()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)
