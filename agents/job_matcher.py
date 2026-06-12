"""agents/job_matcher.py — Agent 4: Job Matcher"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import List, Tuple

from pipeline.state import JobListing, PipelineStage, RozgarState, WorkerProfile
from ui.strings_hi import NO_JOBS_FOUND, TRACE_MATCH_DONE, UP_CITY_PINCODE

ROOT = Path(__file__).parent.parent
JOBS_PATH = ROOT / "data" / "jobs_seed.json"

# ── UP district pin-code prefix map ───────────────────────────────────────────
DISTRICT_PINS = {
    "226": "Lucknow",
    "208": "Kanpur",
    "282": "Agra",
    "221": "Varanasi",
    "211": "Allahabad",
    "250": "Meerut",
    "273": "Gorakhpur",
    "243": "Bareilly",
    "202": "Aligarh",
    "244": "Moradabad",
}

# Approx city-to-city distances (km) for UP
CITY_DISTANCES = {
    ("Lucknow",   "Kanpur"):    80,
    ("Lucknow",   "Agra"):     330,
    ("Lucknow",   "Varanasi"): 285,
    ("Lucknow",   "Allahabad"):210,
    ("Lucknow",   "Meerut"):   440,
    ("Lucknow",   "Gorakhpur"):270,
    ("Lucknow",   "Bareilly"): 260,
    ("Kanpur",    "Agra"):     270,
    ("Kanpur",    "Varanasi"): 330,
    ("Agra",      "Meerut"):   220,
}


def _city_distance(c1: str, c2: str) -> float:
    key = (c1, c2)
    rev = (c2, c1)
    return float(CITY_DISTANCES.get(key, CITY_DISTANCES.get(rev, 50)))


def job_matcher(state: RozgarState) -> RozgarState:
    """
    Agent 4 — Job Matcher
    Input:  state.worker
    Output: state.matched_jobs (top 5, sorted by composite score)
    """
    try:
        state.current_stage = PipelineStage.JOB_MATCH

        if state.worker is None:
            raise ValueError("Worker profile not set")

        worker = state.worker
        all_jobs = _load_jobs()

        # Step 1: pin-code proximity filter
        prefix = worker.pin_code[:3]
        nearby = [j for j in all_jobs if j["pin_code"][:3] == prefix]
        if len(nearby) < 3:
            # Expand to same district group
            nearby = all_jobs

        # Step 2: score each job
        scored: List[Tuple[float, dict]] = []
        worker_text = " ".join(worker.skills)

        for job in nearby:
            skill_sim = _skill_similarity(worker_text, " ".join(job["skills_required"]))
            wage_fit  = _wage_fit(job["wage_per_day"], worker.preferred_wage_per_day)
            job_city  = job["location"].split(",")[0].strip()
            dist_km   = _city_distance(worker.city, job_city)
            dist_score = 1.0 / (dist_km / 10 + 1)

            composite = 0.5 * skill_sim + 0.3 * wage_fit + 0.2 * dist_score
            scored.append((composite, job, dist_km))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:5]

        matched: List[JobListing] = []
        for score, job, dist_km in top:
            jl = JobListing(
                job_id=job["job_id"],
                contractor_id=job["contractor_id"],
                title=job["title"],
                title_hindi=job["title_hindi"],
                location=job["location"],
                pin_code=job["pin_code"],
                wage_per_day=job["wage_per_day"],
                skills_required=job["skills_required"],
                start_date=job["start_date"],
                openings=job["openings"],
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
                f"Aapke liye {len(matched)} naukri mili!\n\n"
                f"Sabse acchi match:\n"
                f"{top_job.title_hindi} — Rs. {top_job.wage_per_day}/din\n"
                f"{top_job.location}  •  {top_job.distance_km} km door",
            )
        else:
            state.add_wa_message("bot", NO_JOBS_FOUND)

        state.log(TRACE_MATCH_DONE)

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _load_jobs() -> List[dict]:
    if JOBS_PATH.exists():
        return json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    return []


def _skill_similarity(worker_text: str, job_text: str) -> float:
    from utils.embeddings import get_embedding, cosine_similarity
    wv = get_embedding(worker_text)
    jv = get_embedding(job_text)
    return cosine_similarity(wv, jv)


def _wage_fit(job_wage: int, preferred: int) -> float:
    if preferred <= 0:
        return 1.0
    return 1.0 if job_wage >= preferred else job_wage / preferred
