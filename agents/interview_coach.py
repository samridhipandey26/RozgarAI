"""agents/interview_coach.py — Agent 5: Interview Coach (Production)
Always uses LLM, tailored to the specific matched job. No demo_mode.
"""
from __future__ import annotations

import json
import os
import re
from typing import List

from pipeline.state import PipelineStage, RozgarState

COACH_PROMPT = """You are a friendly job coach helping an Indian blue-collar worker prepare for a job meeting.

Worker: {name}
Primary skill: {skill}
Experience: {experience} years
City: {city}

Job they are applying for:
- Role: {job_title} ({job_title_hindi})
- Employer: {employer}
- Wage: ₹{wage}/day
- Location: {location}

Give exactly 3 practical tips in Hindi (Devanagari script) for when they meet the contractor.
Each tip should be:
- 1-2 short sentences
- Direct and actionable
- Specific to this job role and employer

Respond ONLY as a JSON array of 3 Hindi strings. No preamble, no markdown."""


def interview_coach(state: RozgarState) -> RozgarState:
    """
    Agent 5 — Interview Coach
    Input:  state.worker, state.matched_jobs[0]
    Output: state.interview_tips (3 Hindi tips, role-specific)
    """
    try:
        state.current_stage = PipelineStage.INTERVIEW_COACH

        if not state.worker or not state.matched_jobs:
            state.interview_tips = _generic_tips()
            state.log("⚠️ Interview Coach: Using generic tips (no worker/job data)")
        else:
            state.log("💬 Interview Coach: Generating role-specific tips...")
            state.interview_tips = _generate_tips(state)
            state.log("✅ Interview Coach: Tips ready")

        for i, tip in enumerate(state.interview_tips, 1):
            state.add_wa_message("bot", f"💡 Tip {i}: {tip}")

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _generate_tips(state: RozgarState) -> List[str]:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return _generic_tips()

    w = state.worker
    job = state.matched_jobs[0]

    prompt = COACH_PROMPT.format(
        name=w.name,
        skill=w.skills[0] if w.skills else "helper",
        experience=w.experience_years,
        city=w.city,
        job_title=job.title,
        job_title_hindi=job.title_hindi,
        employer=job.employer_name or "Contractor",
        wage=job.wage_per_day,
        location=job.location,
    )

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

        # Try JSON parse
        try:
            tips = json.loads(raw)
            if isinstance(tips, list) and len(tips) >= 1:
                return [str(t) for t in tips[:3]]
        except json.JSONDecodeError:
            pass

        # Fallback: extract lines that look like tips
        lines = [l.strip().lstrip("1234567890.-) ") for l in raw.split("\n") if len(l.strip()) > 20]
        if len(lines) >= 3:
            return lines[:3]

    except Exception as e:
        print(f"[InterviewCoach] LLM failed: {e}")

    return _generic_tips()


def _generic_tips() -> List[str]:
    return [
        "समय पर पहुंचें और साफ कपड़े पहनें — पहली मुलाकात में अच्छा प्रभाव बहुत ज़रूरी है।",
        "ठेकेदार से सीधे पूछें: काम कितने दिन का है और पैसे कब मिलेंगे।",
        "अपना पिछला काम का अनुभव बताएं — कोई पुराना प्रोजेक्ट या उदाहरण ज़रूर शेयर करें।",
    ]
