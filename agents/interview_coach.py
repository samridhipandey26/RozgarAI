"""agents/interview_coach.py — Agent 5: Interview Coach"""
from __future__ import annotations

import json
import os
import re
from typing import List

from pipeline.state import PipelineStage, RozgarState
from ui.strings_hi import TRACE_COACH_DONE

MOCK_TIPS = [
    "Samay par pahunchen aur saaf kapde pehnen — pehli mulakat mein acha impression bahut zaroori hai.",
    "Contractor se seedha poochhen: kaam kitne din ka hai aur paise kab milenge.",
    "Apna kaam ka tarika batayein — koi purana project ya kaam ka example share karein.",
]

COACH_PROMPT = """You are a friendly job coach speaking to an Indian blue-collar worker in simple Hindi.
Worker: {name}, skills: {skills}, experience: {experience} years
Job: {job_title} paying Rs. {wage}/day at {location}

Give exactly 3 short, practical tips in Hindi (Devanagari script) that will help this worker 
when they meet the contractor. Each tip should be 1 sentence, direct, and actionable.
Respond ONLY as a JSON array of 3 strings. No preamble."""


def interview_coach(state: RozgarState) -> RozgarState:
    """
    Agent 5 — Interview Coach
    Input:  state.worker, state.matched_jobs[0]
    Output: state.interview_tips (list of 3 Hindi tips)
    """
    try:
        state.current_stage = PipelineStage.INTERVIEW_COACH

        if state.demo_mode or not os.getenv("ANTHROPIC_API_KEY"):
            state.interview_tips = MOCK_TIPS
        else:
            if state.worker and state.matched_jobs:
                state.interview_tips = _generate_tips(state)
            else:
                state.interview_tips = MOCK_TIPS

        for i, tip in enumerate(state.interview_tips, 1):
            state.add_wa_message("bot", f"Tip {i}: {tip}")

        state.log(TRACE_COACH_DONE)

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _generate_tips(state: RozgarState) -> List[str]:
    import anthropic
    w   = state.worker
    job = state.matched_jobs[0]
    prompt = COACH_PROMPT.format(
        name=w.name,
        skills=", ".join(w.skills),
        experience=w.experience_years,
        job_title=job.title_hindi,
        wage=job.wage_per_day,
        location=job.location,
    )
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`")
    tips = json.loads(raw)
    return tips[:3]
