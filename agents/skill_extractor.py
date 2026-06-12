"""agents/skill_extractor.py — Agent 2: Skill Extractor"""
from __future__ import annotations

import json
import os
import re
import uuid

from pipeline.state import PipelineStage, RozgarState, WorkerProfile
from ui.strings_hi import TRACE_SKILLS_DONE, UP_CITY_PINCODE

SYSTEM_PROMPT = """You are a skill extraction assistant for Indian blue-collar workers. 
Extract structured information from the worker's self-introduction.
Respond ONLY with a JSON object matching this schema:
{
  "name": string,
  "city": string,
  "pin_code": string (6 digits, guess from city if not stated),
  "skills": array of strings (use canonical terms: ["electrician", "plumber", "loader", "driver", "mason", "helper", "welder", "carpenter", "painter", "security_guard"]),
  "experience_years": integer,
  "preferred_wage_per_day": integer (in INR, estimate from context if not stated)
}

Examples of colloquial Hindi -> canonical skill mapping:
- "bijli ka kaam karta hoon" -> "electrician"
- "mazdoori karta hoon" -> "loader"
- "gaadi chalata hoon" -> "driver"
- "nall fitting" -> "plumber"
- "cement paatna" -> "mason"
- "security wala" -> "security_guard"

If a field cannot be determined, use sensible defaults. Never return null for skills array."""

# Mock response for Raju (demo mode)
MOCK_PROFILE = {
    "name": "Raju Kumar",
    "city": "Lucknow",
    "pin_code": "226001",
    "skills": ["electrician"],
    "experience_years": 5,
    "preferred_wage_per_day": 600,
}


def skill_extractor(state: RozgarState) -> RozgarState:
    """
    Agent 2 — Skill Extractor
    Input:  state.transcript_hindi, state.transcript_english
    Output: state.worker (WorkerProfile)
    """
    try:
        state.current_stage = PipelineStage.SKILL_EXTRACT

        text = state.transcript_hindi or state.transcript_english or ""
        profile_dict = _extract_via_llm(text) if not state.demo_mode else MOCK_PROFILE

        worker_id = f"w_{uuid.uuid4().hex[:8]}"

        # Resolve pin_code from city if missing
        pin = profile_dict.get("pin_code", "")
        if not pin or len(pin) < 6:
            city = profile_dict.get("city", "Lucknow")
            prefix = UP_CITY_PINCODE.get(city, "226")
            pin = prefix + "001"

        state.worker = WorkerProfile(
            worker_id=worker_id,
            name=profile_dict.get("name", "Kaamgar"),
            phone="+919999999999",
            city=profile_dict.get("city", "Lucknow"),
            pin_code=pin,
            skills=profile_dict.get("skills", ["helper"]),
            experience_years=profile_dict.get("experience_years", 0),
            preferred_wage_per_day=profile_dict.get("preferred_wage_per_day", 500),
        )

        _upsert_worker(state.worker)
        state.log(TRACE_SKILLS_DONE)

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _extract_via_llm(text: str) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return MOCK_PROFILE
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`")
        return json.loads(raw)
    except Exception as e:
        print(f"[SkillExtractor] LLM failed: {e}")
        return MOCK_PROFILE


def _upsert_worker(worker: WorkerProfile) -> None:
    try:
        from db.models import get_session, Worker
        import json as _json
        with get_session() as session:
            existing = session.get(Worker, worker.worker_id)
            if existing is None:
                session.add(Worker(
                    worker_id=worker.worker_id,
                    name=worker.name,
                    phone=worker.phone,
                    city=worker.city,
                    pin_code=worker.pin_code,
                    skills=_json.dumps(worker.skills),
                    experience_years=worker.experience_years,
                    preferred_wage_per_day=worker.preferred_wage_per_day,
                ))
                session.commit()
    except Exception as e:
        print(f"[SkillExtractor] DB upsert failed (non-critical): {e}")
