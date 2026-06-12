"""agents/skill_extractor.py — Agent 2: Skill Extractor (Production)
Real LLM extraction + Nominatim geocoding + Supabase save. No hardcoded Raju.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from typing import Optional

from pipeline.state import PipelineStage, RozgarState, WorkerProfile

SYSTEM_PROMPT = """You are a skill extraction assistant for Indian blue-collar workers.
Extract structured information from the worker's self-introduction.
Respond ONLY with a valid JSON object matching this schema exactly:
{
  "name": string (full name, capitalize properly),
  "city": string (UP city name, standardize: "Lucknow" not "lucknow"),
  "skill": string (PRIMARY canonical skill — one of: electrician|plumber|construction_helper|warehouse_loader|driver|mason|painter|welder|security_guard|domestic_help),
  "skills_all": array of strings (all skills mentioned, same canonical values),
  "experience_years": integer,
  "expected_wage": integer (INR per day, estimate from context if not stated — typical range 400-900),
  "languages": array of strings (e.g. ["Hindi", "English"]),
  "education": string (e.g. "ITI Electrician", "Class 10", "Not specified")
}

Colloquial Hindi → canonical skill mapping:
- "bijli ka kaam" / "wiring" / "electrician" → "electrician"
- "nall fitting" / "plumber" / "bathroom" → "plumber"
- "mazdoori" / "construction" / "site kaam" → "construction_helper"
- "loader" / "godam" / "unloading" → "warehouse_loader"
- "gaadi chalata" / "driver" / "truck" → "driver"
- "raj mistry" / "cement" / "tile" / "mason" → "mason"
- "painter" / "painting" → "painter"
- "welder" / "welding" → "welder"
- "security" / "guard" → "security_guard"
- "ghar ka kaam" / "cooking" / "cleaning" → "domestic_help"

UP cities (use exact spelling): Lucknow, Kanpur, Varanasi, Agra, Muzaffarnagar, Gorakhpur, Prayagraj, Meerut
If city not mentioned or not UP, default to "Lucknow".
Never return null for any field. Use sensible defaults."""


def skill_extractor(state: RozgarState) -> RozgarState:
    """
    Agent 2 — Skill Extractor
    Input:  state.transcript_hindi, state.transcript_english
    Output: state.worker (WorkerProfile) — saved to Supabase
    """
    try:
        state.current_stage = PipelineStage.SKILL_EXTRACT

        text = state.transcript_hindi or state.transcript_english or ""
        if not text.strip():
            raise ValueError("No transcript available for skill extraction")

        state.log("🧠 Skill Extractor: Analyzing worker profile...")
        profile_dict = _extract_via_llm(text)

        # Geocode city
        city = profile_dict.get("city", "Lucknow")
        lat, lng = _geocode_city(city)

        worker_id = f"w_{uuid.uuid4().hex[:8]}"

        state.worker = WorkerProfile(
            worker_id=worker_id,
            name=profile_dict.get("name", "Kaamgar"),
            phone=state.worker.phone if state.worker else "+919999999999",
            city=city,
            pin_code=_city_to_pin(city),
            skills=profile_dict.get("skills_all") or [profile_dict.get("skill", "helper")],
            experience_years=profile_dict.get("experience_years", 0),
            preferred_wage_per_day=profile_dict.get("expected_wage", 500),
            languages=profile_dict.get("languages", ["Hindi"]),
        )

        # Save to DB (Supabase or SQLite)
        _save_profile(state, profile_dict, city, lat, lng)

        wa_msg = (
            f"Shukriya, {state.worker.name}!\n\n"
            f"Aapki profile ready hai:\n"
            f"🔧 Skill: {profile_dict.get('skill', 'helper')}\n"
            f"📍 Shahar: {city}\n"
            f"⏳ Anubhav: {state.worker.experience_years} saal\n"
            f"💰 Mazdoori: ₹{state.worker.preferred_wage_per_day}/din"
        )
        state.add_wa_message("bot", wa_msg)
        state.log("✅ Skill Extractor: Profile saved")

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _extract_via_llm(text: str) -> dict:
    """Extract structured profile from transcript using Claude."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"LLM returned invalid JSON: {raw[:200]}")


def _geocode_city(city: str) -> tuple[float, float]:
    """Geocode city using Nominatim, fall back to known coordinates."""
    CITY_COORDS = {
        "Lucknow":       (26.8467, 80.9462),
        "Kanpur":        (26.4499, 80.3319),
        "Varanasi":      (25.3176, 82.9739),
        "Agra":          (27.1767, 78.0081),
        "Muzaffarnagar": (29.4727, 77.7085),
        "Gorakhpur":     (26.7606, 83.3732),
        "Prayagraj":     (25.4358, 81.8463),
        "Meerut":        (28.9845, 77.7064),
        "Allahabad":     (25.4358, 81.8463),  # = Prayagraj
        "Bareilly":      (28.3670, 79.4304),
    }
    # Try Nominatim
    try:
        import requests
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{city}, Uttar Pradesh, India", "format": "json", "limit": 1},
            headers={"User-Agent": "RozgarAI/2.0"},
            timeout=4,
        )
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return CITY_COORDS.get(city, (26.8467, 80.9462))


def _city_to_pin(city: str) -> str:
    PINS = {
        "Lucknow": "226001", "Kanpur": "208001", "Varanasi": "221001",
        "Agra": "282001", "Muzaffarnagar": "251001", "Gorakhpur": "273001",
        "Prayagraj": "211001", "Meerut": "250001", "Allahabad": "211001",
    }
    return PINS.get(city, "226001")


def _save_profile(state: RozgarState, profile_dict: dict, city: str, lat: float, lng: float) -> None:
    """Save worker profile to Supabase (or SQLite fallback)."""
    from backend.db.supabase_client import sb_upsert, supabase_available

    # Use the user_id from the pipeline session if available
    user_id = getattr(state, "user_id", None) or state.worker.worker_id

    profile_data = {
        "user_id": user_id,
        "name": profile_dict.get("name", "Kaamgar"),
        "city": city,
        "lat": lat,
        "lng": lng,
        "skill": profile_dict.get("skill", "helper"),
        "skills_all": profile_dict.get("skills_all", [profile_dict.get("skill", "helper")]),
        "years_exp": profile_dict.get("experience_years", 0),
        "expected_wage": profile_dict.get("expected_wage", 500),
        "languages": profile_dict.get("languages", ["Hindi"]),
        "education": profile_dict.get("education", "Not specified"),
        "raw_transcript": state.transcript_hindi or "",
        "onboarding_done": True,
    }

    if supabase_available():
        sb_upsert("worker_profiles", profile_data, on_conflict="user_id")
    else:
        _sqlite_save(state.worker)


def _sqlite_save(worker: WorkerProfile) -> None:
    try:
        from db.models import get_session, Worker as DBWorker
        import json as _json
        with get_session() as session:
            existing = session.get(DBWorker, worker.worker_id)
            if existing is None:
                session.add(DBWorker(
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
        print(f"[SkillExtractor] SQLite save failed (non-critical): {e}")
