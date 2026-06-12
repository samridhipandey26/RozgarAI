"""utils/tts.py — gTTS Hindi Text-to-Speech wrapper"""
from __future__ import annotations

import io
import os
from pathlib import Path


def synthesize_hindi(text: str, output_path: str | None = None) -> bytes:
    """
    Convert Hindi text to speech using gTTS.
    Returns audio bytes. Optionally saves to output_path.
    """
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        audio_bytes = buf.getvalue()

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)

        return audio_bytes
    except Exception as e:
        print(f"[TTS] gTTS failed: {e}")
        return b""


def tts_to_file(text: str, path: str) -> str | None:
    """Save TTS audio to file, return path or None on failure."""
    audio = synthesize_hindi(text, output_path=path)
    if audio:
        return path
    return None
