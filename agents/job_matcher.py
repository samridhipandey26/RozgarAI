"""agents/job_matcher.py — Agent 4: Job Matcher (Production)
Real Haversine distance + Supabase DB query + FAISS skill matching.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import List, Tuple

from pipeline.state import JobListing, PipelineStage, RozgarState, WorkerProfile

ROOT = Path(__file__).parent.parent

# ── City coordinate fallback ──────────────────────────────────────────────────
CITY_COORDS = {
    "Lucknow":       (26.8467, 80.9462),
    "Kanpur":        (26.4499, 80.3319),
    "Varanasi":      (25.3176, 82.9739),
    "Agra":          (27.1767, 78.0081),
    "Muzaffarnagar": (29.4727, 77.7085),
    "Gorakhpur":     (26.7606, 83.3732),
    "Prayagraj":     (25.4358, 81.8463),
    "Meerut":        (28.9845, 77.7064),
    "Allahabad":     (25.4358, 81.8463),
    "Bareilly":      (28.3670, 79.4304),
}


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def job_matcher(state: RozgarState) -> RozgarState:
    """
    Agent 4 — Job Matcher
    Input:  state.worker (WorkerProfile with lat/lng)
    Output: state.matched_jobs (top 8, sorted by composite score)
    """
    try:
        state.current_stage = PipelineStage.JOB_MATCH

        if state.worker is None:
            raise ValueError("Worker profile not set")

        state.log("🔍 Job Matcher: Searching real jobs database...")

        worker = state.worker
        all_jobs = _load_jobs()

        if not all_jobs:
            state.add_wa_message("bot", "Abhi koi naukri available nahin hai. Baad mein check karein.")
            state.log("⚠️ Job Matcher: No jobs found in database")
            return state

        # Worker lat/lng
        worker_lat = worker.lat or CITY_COORDS.get(worker.city, (26.8467, 80.9462))[0]
        worker_lng = worker.lng or CITY_COORDS.get(worker.city, (26.8467, 80.9462))[1]

        scored: List[Tuple[float, float, dict]] = []
        primary_skill = worker.skills[0] if worker.skills else "helper"
        all_skills = set(worker.skills)

        for job in all_jobs:
            if job.get("status") == "filled":
                continue

            # Job coordinates
            job_lat = job.get("lat") or CITY_COORDS.get(job.get("city", "Lucknow"), (26.8467, 80.9462))[0]
            job_lng = job.get("lng") or CITY_COORDS.get(job.get("city", "Lucknow"), (26.8467, 80.9462))[1]

            dist_km = _haversine(worker_lat, worker_lng, job_lat, job_lng)

            # Skill match (FAISS if available, else keyword)
            job_role = job.get("role_tag", "")
            skill_score = _skill_score(primary_skill, all_skills, job_role,
                                       job.get("skills_required") or [job_role])

            # Wage fit
            wage_fit = _wage_fit(job.get("wage_per_day", 500), worker.preferred_wage_per_day)

            # Distance score
            dist_score = 1.0 / (dist_km / 25 + 1)

            composite = 0.50 * skill_score + 0.30 * wage_fit + 0.20 * dist_score
            scored.append((composite, dist_km, job))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:8]

        matched: List[JobListing] = []
        for score, dist_km, job in top:
            job_id = str(job.get("id") or job.get("job_id") or "")
            job_city = job.get("city", "")
            jl = JobListing(
                job_id=job_id,
                contractor_id=str(job.get("employer_id") or ""),
                employer_name=job.get("employer_name", ""),
                title=job.get("title", ""),
                title_hindi=job.get("title_hindi", ""),
                location=f"{job_city}, UP",
                pin_code=job.get("pin_code") or _city_to_pin(job_city),
                wage_per_day=job.get("wage_per_day", 0),
                skills_required=_parse_skills(job),
                start_date=str(job.get("start_date", "")) if job.get("start_date") else "ASAP",
                openings=job.get("openings", 1),
                lat=job.get("lat"),
                lng=job.get("lng"),
                distance_km=round(dist_km, 1),
                match_score=round(score, 3),
            )
            matched.append(jl)

        state.matched_jobs = matched
        state.selected_job = matched[0] if matched else None

        if matched:
            top_job = matched[0]
            state.add_wa_message(
                "bot",
                f"🎉 Aapke liye {len(matched)} naukri mili!\n\n"
                f"Sabse acchi match:\n"
                f"🔧 {top_job.title_hindi}\n"
                f"💰 ₹{top_job.wage_per_day}/din\n"
                f"📍 {top_job.location}  •  {top_job.distance_km} km door\n"
                f"✅ Match: {int(top_job.match_score * 100)}%",
            )
        else:
            state.add_wa_message("bot", "Is samay koi matching naukri nahin mili. Baad mein try karein.")

        state.log(f"✅ Job Matcher: {len(matched)} jobs found")

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _load_jobs() -> List[dict]:
    """Load from Supabase first, then local JSON fallbacks."""
    try:
        from backend.db.supabase_client import sb_select, supabase_available
        if supabase_available():
            jobs = sb_select("jobs", {"status": "open"}, limit=200)
            if jobs:
                return jobs
    except Exception as e:
        print(f"[JobMatcher] Supabase load failed: {e}")

    # Local JSON fallbacks
    for json_name in ("jobs_seed_v2.json", "jobs_seed.json"):
        path = ROOT / "data" / json_name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))

    return []


def _skill_score(primary: str, all_skills: set, job_role: str, job_skills: list) -> float:
    """Compute skill match score. Try FAISS, else keyword matching."""
    # Try FAISS semantic similarity
    try:
        from utils.embeddings import get_embedding, cosine_similarity
        worker_text = " ".join(list(all_skills))
        job_text = f"{job_role} {' '.join(job_skills)}"
        wv = get_embedding(worker_text)
        jv = get_embedding(job_text)
        faiss_score = cosine_similarity(wv, jv)
        if faiss_score > 0.1:
            return float(faiss_score)
    except Exception:
        pass

    # Keyword fallback
    if primary == job_role:
        return 1.0
    if primary in job_skills or job_role in all_skills:
        return 0.85
    # Partial match (e.g. "electrician" in "electrical_helper")
    for sk in all_skills:
        if sk in job_role or job_role in sk:
            return 0.65
    return 0.30


def _wage_fit(job_wage: int, preferred: int) -> float:
    if preferred <= 0:
        return 1.0
    if job_wage >= preferred:
        return 1.0
    return max(job_wage / preferred, 0.3)


def _parse_skills(job: dict) -> List[str]:
    raw = job.get("skills_required", job.get("role_tag", "helper"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return [raw]
    return []


def _city_to_pin(city: str) -> str:
    PINS = {
        "Lucknow": "226001", "Kanpur": "208001", "Varanasi": "221001",
        "Agra": "282001", "Muzaffarnagar": "251001", "Gorakhpur": "273001",
        "Prayagraj": "211001", "Meerut": "250001",
    }
    return PINS.get(city, "226001")
