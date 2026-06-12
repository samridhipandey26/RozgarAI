"""agents/voice_intake.py — Agent 1: Voice Intake (Production)
Real Whisper transcription. No hardcoded Raju. Graceful text fallback.
"""
from __future__ import annotations

import os
from pipeline.state import PipelineStage, RozgarState


def voice_intake(state: RozgarState) -> RozgarState:
    """
    Agent 1 — Voice Intake
    Input:  state.raw_audio_path (or state.transcript_hindi pre-set from text input)
    Output: state.transcript_hindi, state.transcript_english
    """
    try:
        state.current_stage = PipelineStage.VOICE_INTAKE

        # If transcript was already provided (text fallback from frontend)
        if state.transcript_hindi:
            state.log("✅ Voice Intake: Text input received directly")
            state.add_wa_message("worker", state.transcript_hindi)
            # Still try to translate for downstream LLMs
            if not state.transcript_english:
                state.transcript_english = _translate_to_english(state.transcript_hindi)
            return state

        # Try real Whisper transcription
        if state.raw_audio_path:
            state.log("🎙️ Voice Intake: Transcribing audio with Whisper...")
            transcript = _transcribe_whisper(state.raw_audio_path)
            state.transcript_hindi = transcript
            state.transcript_english = _translate_to_english(transcript)
            state.log("✅ Voice Intake: Transcription complete")
            state.add_wa_message("worker", state.transcript_hindi)
        else:
            # No audio, no text — ask for input
            state.transcript_hindi = ""
            state.transcript_english = ""
            state.log("⚠️ Voice Intake: No audio or text input received")
            state.add_wa_message("bot", "Kripya apna parichay dijiye — bolke ya likhke।")

    except Exception as e:
        state.error_message = f"Voice intake failed: {e}"
        state.current_stage = PipelineStage.ERROR

    return state


def _transcribe_whisper(audio_path: str) -> str:
    """Transcribe using OpenAI Whisper API (hindi language forced)."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set — cannot transcribe audio")

    import openai
    from pathlib import Path

    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    client = openai.OpenAI(api_key=api_key)
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="hi",
            prompt="Yeh ek Hindi mein worker ka parichay hai. Iska kaam aur anubhav batao.",
        )
    return result.text


def _translate_to_english(hindi_text: str) -> str:
    """Translate Hindi transcript to English using Claude."""
    if not hindi_text.strip():
        return ""
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return hindi_text  # Return original if no key

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": (
                    f"Translate this Hindi worker introduction to English. "
                    f"Keep all proper nouns (names, cities) unchanged. "
                    f"Be concise:\n\n{hindi_text}"
                ),
            }],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"[VoiceIntake] Translation failed: {e}")
        return hindi_text
