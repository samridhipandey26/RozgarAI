"""utils/asr.py — Whisper ASR wrapper"""
from __future__ import annotations

import os
from pathlib import Path


def transcribe_hindi(audio_path: str) -> str:
    """
    Transcribe audio file to Hindi text using OpenAI Whisper.
    Returns transcript string. Falls back to demo text if no API key.
    """
    from ui.strings_hi import DEMO_WORKER_INTRO

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return DEMO_WORKER_INTRO

    if not Path(audio_path).exists():
        return DEMO_WORKER_INTRO

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="hi",
            )
        return result.text
    except Exception as e:
        print(f"[ASR] Whisper failed: {e} — using demo text")
        return DEMO_WORKER_INTRO


def translate_to_english(hindi_text: str) -> str:
    """Translate Hindi text to English using Claude."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return _mock_translate(hindi_text)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": (
                    f"Translate this Hindi text to English. "
                    f"Preserve all proper nouns and job titles: {hindi_text}"
                ),
            }],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"[ASR] Translation failed: {e}")
        return _mock_translate(hindi_text)


def _mock_translate(hindi_text: str) -> str:
    return (
        "Hello, my name is Raju. I live in Lucknow. "
        "I am an electrician with 5 years of experience. "
        "I need 600 rupees per day."
    )
