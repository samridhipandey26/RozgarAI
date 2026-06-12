"""
backend/routers/jobs.py — Job listings, matching, employer posting
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.schemas.models import JobCreate, JobResponse, GeocodeRequest, GeocodeResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
security = HTTPBearer(auto_error=False)

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
}


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return distance in km between two lat/lng points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _geocode_nominatim(address: str) -> tuple[float, float] | None:
    """Geocode using OpenStreetMap Nominatim (no API key needed)."""
    try:
        import requests
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1, "countrycodes": "in"},
            headers={"User-Agent": "RozgarAI/2.0 (samridhi@rozgarai.in)"},
            timeout=5,
        )
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"[Geocode] Nominatim failed: {e}")
    return None


def _get_job_lat_lng(city: str, address: str) -> tuple[float, float]:
    """Get lat/lng for a job posting, using Nominatim or city fallback."""
    # Try Nominatim with full address
    result = _geocode_nominatim(f"{address}, {city}, Uttar Pradesh, India")
    if result:
        return result
    # Fallback to city centroid
    return CITY_COORDS.get(city, (26.8467, 80.9462))


def _get_user_optional(credentials: HTTPAuthorizationCredentials | None) -> str | None:
    if not credentials:
        return None
    try:
        from backend.db.supabase_client import get_supabase
        sb = get_supabase()
        if sb:
            user_resp = sb.auth.get_user(credentials.credentials)
            return user_resp.user.id
    except Exception:
        pass
    return None


def _require_user(credentials: HTTPAuthorizationCredentials | None) -> str:
    uid = _get_user_optional(credentials)
    if not uid:
        raise HTTPException(401, "Authentication required")
    return uid


# ── Load jobs (Supabase or SQLite fallback) ───────────────────────────────────

def _load_all_jobs() -> list[dict]:
    """Load all open jobs. Tries Supabase first, falls back to local JSON/SQLite."""
    from backend.db.supabase_client import sb_select, supabase_available

    if supabase_available():
        return sb_select("jobs", {"status": "open"}, limit=500)

    # JSON fallback
    json_path = ROOT / "data" / "jobs_seed_v2.json"
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))

    # Legacy seed
    legacy = ROOT / "data" / "jobs_seed.json"
    if legacy.exists():
        return json.loads(legacy.read_text(encoding="utf-8"))

    return []


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/match", response_model=List[JobResponse])
async def match_jobs(
    skill: str = Query(default=""),
    city: str = Query(default="Lucknow"),
    lat: Optional[float] = Query(default=None),
    lng: Optional[float] = Query(default=None),
    wage: Optional[int] = Query(default=None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Return ranked job matches for a worker.
    Uses Haversine distance + skill match + wage fit.
    """
    # Get worker lat/lng
    worker_lat, worker_lng = lat, lng
    if not worker_lat or not worker_lng:
        # Try to get from worker profile
        user_id = _get_user_optional(credentials)
        if user_id:
            from backend.db.supabase_client import sb_select
            profiles = sb_select("worker_profiles", {"user_id": user_id}, limit=1)
            if profiles:
                p = profiles[0]
                worker_lat = p.get("lat") or CITY_COORDS.get(city, (26.8467, 80.9462))[0]
                worker_lng = p.get("lng") or CITY_COORDS.get(city, (26.8467, 80.9462))[1]

    if not worker_lat or not worker_lng:
        worker_lat, worker_lng = CITY_COORDS.get(city, (26.8467, 80.9462))

    all_jobs = _load_all_jobs()

    scored = []
    for job in all_jobs:
        if job.get("status") == "filled":
            continue

        job_lat = job.get("lat") or CITY_COORDS.get(job.get("city", "Lucknow"), (26.8467, 80.9462))[0]
        job_lng = job.get("lng") or CITY_COORDS.get(job.get("city", "Lucknow"), (26.8467, 80.9462))[1]

        dist_km = _haversine(worker_lat, worker_lng, job_lat, job_lng)

        # Skill match score
        job_role = job.get("role_tag", "")
        skill_match = 1.0 if skill and skill.lower() in job_role.lower() else 0.3
        if skill and any(s in job_role.lower() for s in skill.lower().split()):
            skill_match = 0.8

        # Wage fit
        job_wage = job.get("wage_per_day", 500)
        preferred = wage or 500
        wage_fit = 1.0 if job_wage >= preferred else job_wage / preferred

        # Distance score (inverse, penalise >100km)
        dist_score = 1.0 / (dist_km / 20 + 1)

        composite = 0.5 * skill_match + 0.3 * wage_fit + 0.2 * dist_score
        scored.append((composite, dist_km, job))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, dist_km, job in scored[:10]:
        results.append(JobResponse(
            id=str(job.get("id", job.get("job_id", ""))),
            employer_id=str(job.get("employer_id", "")) if job.get("employer_id") else None,
            employer_name=job.get("employer_name", ""),
            title=job.get("title", ""),
            title_hindi=job.get("title_hindi", ""),
            role_tag=job.get("role_tag", ""),
            description=job.get("description", ""),
            wage_per_day=job.get("wage_per_day", 0),
            city=job.get("city", ""),
            address=job.get("address", ""),
            lat=job.get("lat"),
            lng=job.get("lng"),
            openings=job.get("openings", 1),
            filled=job.get("filled", 0),
            start_date=str(job.get("start_date", "")) if job.get("start_date") else None,
            status=job.get("status", "open"),
            created_at=str(job.get("created_at", "")) if job.get("created_at") else None,
            distance_km=round(dist_km, 1),
            match_score=round(score, 3),
            match_pct=int(score * 100),
        ))

    return results


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    city: Optional[str] = Query(default=None),
    role: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=50),
):
    """List all open jobs with optional filters."""
    all_jobs = _load_all_jobs()

    filtered = all_jobs
    if city:
        filtered = [j for j in filtered if j.get("city", "").lower() == city.lower()]
    if role:
        filtered = [j for j in filtered if role.lower() in j.get("role_tag", "").lower()]

    start = (page - 1) * page_size
    page_jobs = filtered[start:start + page_size]

    return [
        JobResponse(
            id=str(j.get("id", j.get("job_id", ""))),
            employer_name=j.get("employer_name", ""),
            title=j.get("title", ""),
            title_hindi=j.get("title_hindi", ""),
            role_tag=j.get("role_tag", ""),
            description=j.get("description", ""),
            wage_per_day=j.get("wage_per_day", 0),
            city=j.get("city", ""),
            address=j.get("address", ""),
            lat=j.get("lat"),
            lng=j.get("lng"),
            openings=j.get("openings", 1),
            filled=j.get("filled", 0),
            start_date=str(j.get("start_date", "")) if j.get("start_date") else None,
            status=j.get("status", "open"),
        )
        for j in page_jobs
    ]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get a single job by ID."""
    from backend.db.supabase_client import sb_select, supabase_available
    if supabase_available():
        jobs = sb_select("jobs", limit=1)
        jobs = [j for j in jobs if str(j.get("id")) == job_id]
    else:
        all_jobs = _load_all_jobs()
        jobs = [j for j in all_jobs if str(j.get("id", j.get("job_id", ""))) == job_id]

    if not jobs:
        raise HTTPException(404, "Job not found")
    j = jobs[0]
    return JobResponse(
        id=str(j.get("id", j.get("job_id", ""))),
        employer_name=j.get("employer_name", ""),
        title=j.get("title", ""),
        title_hindi=j.get("title_hindi", ""),
        role_tag=j.get("role_tag", ""),
        description=j.get("description", ""),
        wage_per_day=j.get("wage_per_day", 0),
        city=j.get("city", ""),
        openings=j.get("openings", 1),
        filled=j.get("filled", 0),
        status=j.get("status", "open"),
    )


@router.post("/", response_model=JobResponse, status_code=201)
async def post_job(
    job: JobCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Employer posts a new job. Auto-geocodes the address."""
    user_id = _require_user(credentials)

    # Geocode address
    lat, lng = _get_job_lat_lng(job.city, job.address)

    from backend.db.supabase_client import sb_insert, supabase_available

    job_data = {
        "employer_id": user_id,
        "title": job.title,
        "title_hindi": job.title_hindi,
        "role_tag": job.role_tag,
        "description": job.description or "",
        "wage_per_day": job.wage_per_day,
        "city": job.city,
        "address": job.address,
        "lat": lat,
        "lng": lng,
        "openings": job.openings,
        "start_date": job.start_date.isoformat() if job.start_date else None,
        "status": "open",
    }

    if supabase_available():
        inserted = sb_insert("jobs", job_data)
        if not inserted:
            raise HTTPException(500, "Failed to save job")
        job_id = inserted.get("id", "")
    else:
        # Fallback: append to JSON
        import uuid
        job_id = str(uuid.uuid4())
        job_data["id"] = job_id
        json_path = ROOT / "data" / "jobs_seed_v2.json"
        jobs_list = json.loads(json_path.read_text()) if json_path.exists() else []
        jobs_list.append(job_data)
        json_path.write_text(json.dumps(jobs_list, indent=2, default=str))

    return JobResponse(
        id=job_id,
        employer_id=user_id,
        title=job.title,
        title_hindi=job.title_hindi,
        role_tag=job.role_tag,
        description=job.description,
        wage_per_day=job.wage_per_day,
        city=job.city,
        address=job.address,
        lat=lat,
        lng=lng,
        openings=job.openings,
        status="open",
    )


@router.patch("/{job_id}/status")
async def update_job_status(
    job_id: str,
    body: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Employer marks job as filled/cancelled."""
    user_id = _require_user(credentials)
    new_status = body.get("status", "filled")

    from backend.db.supabase_client import sb_update, supabase_available
    if supabase_available():
        sb_update("jobs", job_id, {"status": new_status})

    return {"success": True, "status": new_status}


# ── Geocode endpoint ──────────────────────────────────────────────────────────

@router.post("/geocode", response_model=GeocodeResponse)
async def geocode_address(req: GeocodeRequest):
    """Geocode an address using Nominatim."""
    result = _geocode_nominatim(req.address)
    if not result:
        raise HTTPException(422, "Could not geocode address")
    return GeocodeResponse(lat=result[0], lng=result[1])
