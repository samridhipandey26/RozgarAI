"""agents/voice_intake.py — Agent 1: Voice Intake"""
from __future__ import annotations

from pipeline.state import PipelineStage, RozgarState
from ui.strings_hi import DEMO_WORKER_INTRO, TRACE_VOICE_DONE


def voice_intake(state: RozgarState) -> RozgarState:
    """
    Agent 1 — Voice Intake
    Input:  state.raw_audio_path (or None for demo mode)
    Output: state.transcript_hindi, state.transcript_english
    """
    try:
        state.current_stage = PipelineStage.VOICE_INTAKE

        if state.raw_audio_path is None or state.demo_mode:
            # Demo mode — use hardcoded Hindi string
            state.transcript_hindi  = DEMO_WORKER_INTRO
            state.transcript_english = (
                "Hello, my name is Raju. I live in Lucknow. "
                "I am an electrician with 5 years of experience. "
                "I need 600 rupees per day."
            )
        else:
            from utils.asr import transcribe_hindi, translate_to_english
            state.transcript_hindi   = transcribe_hindi(state.raw_audio_path)
            state.transcript_english = translate_to_english(state.transcript_hindi)

        state.log(TRACE_VOICE_DONE)
        state.add_wa_message("worker", state.transcript_hindi)

    except Exception as e:
        state.error_message  = str(e)
        state.current_stage  = PipelineStage.ERROR

    return state
