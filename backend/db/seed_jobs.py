"""
backend/db/seed_jobs.py — Seed 50 realistic UP blue-collar job postings
with real geocoded lat/lng coordinates.

Run: python backend/db/seed_jobs.py
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# ── Real city coordinates (city center lat/lng for UP cities) ─────────────────
CITY_COORDS = {
    "Lucknow":      (26.8467, 80.9462),
    "Kanpur":       (26.4499, 80.3319),
    "Varanasi":     (25.3176, 82.9739),
    "Agra":         (27.1767, 78.0081),
    "Muzaffarnagar":(29.4727, 77.7085),
    "Gorakhpur":    (26.7606, 83.3732),
    "Prayagraj":    (25.4358, 81.8463),
    "Meerut":       (28.9845, 77.7064),
}

# ── Employer seed data ─────────────────────────────────────────────────────────
EMPLOYERS = [
    {"id": "emp-001", "name": "Ashok Construction Pvt Ltd",  "city": "Lucknow"},
    {"id": "emp-002", "name": "Mehta Infra Projects",         "city": "Agra"},
    {"id": "emp-003", "name": "Singh Transport & Warehousing","city": "Varanasi"},
    {"id": "emp-004", "name": "Gupta Electricals",            "city": "Kanpur"},
    {"id": "emp-005", "name": "Sharma Builders",              "city": "Meerut"},
    {"id": "emp-006", "name": "Yadav Security Services",      "city": "Gorakhpur"},
    {"id": "emp-007", "name": "Ram Motors Pvt Ltd",           "city": "Prayagraj"},
    {"id": "emp-008", "name": "Verma Plumbing Works",         "city": "Muzaffarnagar"},
    {"id": "emp-009", "name": "Jain Warehousing Co",          "city": "Lucknow"},
    {"id": "emp-010", "name": "Trivedi Home Services",        "city": "Agra"},
]

def emp(city: str) -> dict:
    """Pick an employer by city (or random)."""
    matches = [e for e in EMPLOYERS if e["city"] == city]
    return (matches[0] if matches else EMPLOYERS[0])


def future_date(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


# ── 50 Job Postings ────────────────────────────────────────────────────────────
RAW_JOBS = [
    # ── LUCKNOW (8 jobs) ──────────────────────────────────────────────────────
    {"city":"Lucknow","title":"Electrician","title_hindi":"बिजली मिस्त्री","role_tag":"electrician",
     "wage":650,"openings":3,"days":5,"employer_idx":0,
     "desc":"Residential wiring and panel maintenance"},
    {"city":"Lucknow","title":"Plumber","title_hindi":"नल मिस्त्री","role_tag":"plumber",
     "wage":550,"openings":2,"days":7,"employer_idx":0,
     "desc":"Bathroom fitting and pipeline repair"},
    {"city":"Lucknow","title":"Construction Helper","title_hindi":"निर्माण सहायक","role_tag":"construction_helper",
     "wage":450,"openings":5,"days":3,"employer_idx":0,
     "desc":"Cement mixing and material loading at construction site"},
    {"city":"Lucknow","title":"Warehouse Loader","title_hindi":"गोदाम मज़दूर","role_tag":"warehouse_loader",
     "wage":500,"openings":4,"days":2,"employer_idx":8,
     "desc":"Loading and unloading goods at cold storage facility"},
    {"city":"Lucknow","title":"Driver","title_hindi":"ड्राइवर","role_tag":"driver",
     "wage":700,"openings":2,"days":10,"employer_idx":8,
     "desc":"City delivery van driver, license required"},
    {"city":"Lucknow","title":"Mason","title_hindi":"राज मिस्त्री","role_tag":"mason",
     "wage":600,"openings":3,"days":4,"employer_idx":0,
     "desc":"Brick laying and plastering for residential project"},
    {"city":"Lucknow","title":"Painter","title_hindi":"पेंटर","role_tag":"painter",
     "wage":500,"openings":2,"days":8,"employer_idx":0,
     "desc":"Interior wall painting and primer work"},
    {"city":"Lucknow","title":"Security Guard","title_hindi":"सुरक्षा गार्ड","role_tag":"security_guard",
     "wage":480,"openings":4,"days":1,"employer_idx":8,
     "desc":"Night shift security at warehouse, 12-hour duty"},

    # ── KANPUR (7 jobs) ───────────────────────────────────────────────────────
    {"city":"Kanpur","title":"Electrician","title_hindi":"बिजली मिस्त्री","role_tag":"electrician",
     "wage":600,"openings":2,"days":6,"employer_idx":3,
     "desc":"Industrial electrician for leather factory"},
    {"city":"Kanpur","title":"Welder","title_hindi":"वेल्डर","role_tag":"welder",
     "wage":700,"openings":2,"days":4,"employer_idx":3,
     "desc":"MIG welding for fabrication workshop"},
    {"city":"Kanpur","title":"Plumber","title_hindi":"नल मिस्त्री","role_tag":"plumber",
     "wage":550,"openings":3,"days":5,"employer_idx":3,
     "desc":"Commercial plumbing for textile mill"},
    {"city":"Kanpur","title":"Construction Helper","title_hindi":"निर्माण सहायक","role_tag":"construction_helper",
     "wage":420,"openings":6,"days":2,"employer_idx":3,
     "desc":"Road construction laborer"},
    {"city":"Kanpur","title":"Driver","title_hindi":"ड्राइवर","role_tag":"driver",
     "wage":680,"openings":1,"days":7,"employer_idx":3,
     "desc":"Heavy vehicle driver for goods transport"},
    {"city":"Kanpur","title":"Mason","title_hindi":"राज मिस्त्री","role_tag":"mason",
     "wage":580,"openings":2,"days":9,"employer_idx":3,
     "desc":"Floor tiling work for commercial building"},
    {"city":"Kanpur","title":"Warehouse Loader","title_hindi":"गोदाम मज़दूर","role_tag":"warehouse_loader",
     "wage":480,"openings":5,"days":1,"employer_idx":3,
     "desc":"Grain storage facility loading work"},

    # ── VARANASI (6 jobs) ─────────────────────────────────────────────────────
    {"city":"Varanasi","title":"Mason","title_hindi":"राज मिस्त्री","role_tag":"mason",
     "wage":560,"openings":4,"days":3,"employer_idx":2,
     "desc":"Temple renovation masonry work"},
    {"city":"Varanasi","title":"Electrician","title_hindi":"बिजली मिस्त्री","role_tag":"electrician",
     "wage":620,"openings":2,"days":5,"employer_idx":2,
     "desc":"Hotel electrical maintenance"},
    {"city":"Varanasi","title":"Painter","title_hindi":"पेंटर","role_tag":"painter",
     "wage":480,"openings":3,"days":6,"employer_idx":2,
     "desc":"Exterior painting of heritage building"},
    {"city":"Varanasi","title":"Driver","title_hindi":"ड्राइवर","role_tag":"driver",
     "wage":660,"openings":2,"days":4,"employer_idx":2,
     "desc":"Tourist taxi driver, local knowledge needed"},
    {"city":"Varanasi","title":"Security Guard","title_hindi":"सुरक्षा गार्ड","role_tag":"security_guard",
     "wage":460,"openings":3,"days":1,"employer_idx":5,
     "desc":"Ghat area security, day shift"},
    {"city":"Varanasi","title":"Construction Helper","title_hindi":"निर्माण सहायक","role_tag":"construction_helper",
     "wage":440,"openings":5,"days":2,"employer_idx":2,
     "desc":"Bridge construction site helper"},

    # ── AGRA (6 jobs) ─────────────────────────────────────────────────────────
    {"city":"Agra","title":"Plumber","title_hindi":"नल मिस्त्री","role_tag":"plumber",
     "wage":530,"openings":2,"days":5,"employer_idx":1,
     "desc":"Hotel pipeline installation near Taj Mahal area"},
    {"city":"Agra","title":"Electrician","title_hindi":"बिजली मिस्त्री","role_tag":"electrician",
     "wage":580,"openings":3,"days":7,"employer_idx":1,
     "desc":"Resort electrical wiring"},
    {"city":"Agra","title":"Painter","title_hindi":"पेंटर","role_tag":"painter",
     "wage":470,"openings":2,"days":8,"employer_idx":1,
     "desc":"Marble-effect paint work for hotel rooms"},
    {"city":"Agra","title":"Domestic Help","title_hindi":"घरेलू सहायक","role_tag":"domestic_help",
     "wage":400,"openings":4,"days":3,"employer_idx":9,
     "desc":"Housekeeping for residential colony"},
    {"city":"Agra","title":"Mason","title_hindi":"राज मिस्त्री","role_tag":"mason",
     "wage":560,"openings":3,"days":4,"employer_idx":1,
     "desc":"Marble flooring installation"},
    {"city":"Agra","title":"Welder","title_hindi":"वेल्डर","role_tag":"welder",
     "wage":680,"openings":1,"days":6,"employer_idx":1,
     "desc":"Iron gate fabrication and installation"},

    # ── MUZAFFARNAGAR (5 jobs) ────────────────────────────────────────────────
    {"city":"Muzaffarnagar","title":"Electrician","title_hindi":"बिजली मिस्त्री","role_tag":"electrician",
     "wage":600,"openings":2,"days":4,"employer_idx":7,
     "desc":"Sugar mill electrical maintenance"},
    {"city":"Muzaffarnagar","title":"Plumber","title_hindi":"नल मिस्त्री","role_tag":"plumber",
     "wage":520,"openings":2,"days":5,"employer_idx":7,
     "desc":"Industrial water supply fitting"},
    {"city":"Muzaffarnagar","title":"Welder","title_hindi":"वेल्डर","role_tag":"welder",
     "wage":720,"openings":2,"days":3,"employer_idx":7,
     "desc":"Steel fabrication for agricultural equipment"},
    {"city":"Muzaffarnagar","title":"Construction Helper","title_hindi":"निर्माण सहायक","role_tag":"construction_helper",
     "wage":430,"openings":6,"days":2,"employer_idx":7,
     "desc":"Road widening project labor"},
    {"city":"Muzaffarnagar","title":"Driver","title_hindi":"ड्राइवर","role_tag":"driver",
     "wage":650,"openings":2,"days":8,"employer_idx":7,
     "desc":"Sugarcane transport truck driver"},

    # ── GORAKHPUR (6 jobs) ────────────────────────────────────────────────────
    {"city":"Gorakhpur","title":"Construction Helper","title_hindi":"निर्माण सहायक","role_tag":"construction_helper",
     "wage":440,"openings":8,"days":2,"employer_idx":5,
     "desc":"Railway colony construction site"},
    {"city":"Gorakhpur","title":"Mason","title_hindi":"राज मिस्त्री","role_tag":"mason",
     "wage":570,"openings":3,"days":4,"employer_idx":5,
     "desc":"AIIMS construction brick laying"},
    {"city":"Gorakhpur","title":"Electrician","title_hindi":"बिजली मिस्त्री","role_tag":"electrician",
     "wage":590,"openings":2,"days":5,"employer_idx":5,
     "desc":"Hospital electrical wiring"},
    {"city":"Gorakhpur","title":"Security Guard","title_hindi":"सुरक्षा गार्ड","role_tag":"security_guard",
     "wage":450,"openings":5,"days":1,"employer_idx":5,
     "desc":"University campus security, night shift"},
    {"city":"Gorakhpur","title":"Domestic Help","title_hindi":"घरेलू सहायक","role_tag":"domestic_help",
     "wage":390,"openings":3,"days":3,"employer_idx":5,
     "desc":"Cooking and cleaning for family residence"},
    {"city":"Gorakhpur","title":"Plumber","title_hindi":"नल मिस्त्री","role_tag":"plumber",
     "wage":510,"openings":2,"days":6,"employer_idx":5,
     "desc":"Hospital plumbing maintenance"},

    # ── PRAYAGRAJ (6 jobs) ────────────────────────────────────────────────────
    {"city":"Prayagraj","title":"Mason","title_hindi":"राज मिस्त्री","role_tag":"mason",
     "wage":555,"openings":4,"days":5,"employer_idx":6,
     "desc":"Mela area construction project"},
    {"city":"Prayagraj","title":"Electrician","title_hindi":"बिजली मिस्त्री","role_tag":"electrician",
     "wage":610,"openings":3,"days":6,"employer_idx":6,
     "desc":"Government building electrical repair"},
    {"city":"Prayagraj","title":"Painter","title_hindi":"पेंटर","role_tag":"painter",
     "wage":490,"openings":2,"days":7,"employer_idx":6,
     "desc":"Outdoor advertising hoarding painting"},
    {"city":"Prayagraj","title":"Driver","title_hindi":"ड्राइवर","role_tag":"driver",
     "wage":650,"openings":2,"days":4,"employer_idx":6,
     "desc":"School bus driver, morning shift"},
    {"city":"Prayagraj","title":"Warehouse Loader","title_hindi":"गोदाम मज़दूर","role_tag":"warehouse_loader",
     "wage":460,"openings":4,"days":2,"employer_idx":6,
     "desc":"FCI grain warehouse loading"},
    {"city":"Prayagraj","title":"Security Guard","title_hindi":"सुरक्षा गार्ड","role_tag":"security_guard",
     "wage":465,"openings":3,"days":1,"employer_idx":6,
     "desc":"Court campus security guard"},

    # ── MEERUT (6 jobs) ───────────────────────────────────────────────────────
    {"city":"Meerut","title":"Welder","title_hindi":"वेल्डर","role_tag":"welder",
     "wage":710,"openings":2,"days":4,"employer_idx":4,
     "desc":"Sports goods manufacturing welding"},
    {"city":"Meerut","title":"Electrician","title_hindi":"बिजली मिस्त्री","role_tag":"electrician",
     "wage":630,"openings":2,"days":5,"employer_idx":4,
     "desc":"Shopping mall electrical maintenance"},
    {"city":"Meerut","title":"Plumber","title_hindi":"नल मिस्त्री","role_tag":"plumber",
     "wage":545,"openings":3,"days":6,"employer_idx":4,
     "desc":"Apartment complex plumbing work"},
    {"city":"Meerut","title":"Construction Helper","title_hindi":"निर्माण सहायक","role_tag":"construction_helper",
     "wage":445,"openings":6,"days":3,"employer_idx":4,
     "desc":"Metro construction site helper"},
    {"city":"Meerut","title":"Driver","title_hindi":"ड्राइवर","role_tag":"driver",
     "wage":670,"openings":2,"days":7,"employer_idx":4,
     "desc":"E-commerce delivery driver, bike or car"},
    {"city":"Meerut","title":"Mason","title_hindi":"राज मिस्त्री","role_tag":"mason",
     "wage":575,"openings":3,"days":5,"employer_idx":4,
     "desc":"Residential colony tile work"},
]


def build_jobs() -> list[dict]:
    """Convert raw job defs to full job dicts with UUID, lat/lng, dates."""
    jobs = []
    for raw in RAW_JOBS:
        city = raw["city"]
        lat, lng = CITY_COORDS[city]
        # Add slight jitter so jobs in same city aren't stacked
        import random
        jitter = 0.02
        lat += random.uniform(-jitter, jitter)
        lng += random.uniform(-jitter, jitter)
        emp_data = EMPLOYERS[raw["employer_idx"]]
        job = {
            "id": str(uuid.uuid4()),
            "employer_id": None,          # will be replaced with real UUID after auth seed
            "employer_name": emp_data["name"],
            "title": raw["title"],
            "title_hindi": raw["title_hindi"],
            "role_tag": raw["role_tag"],
            "description": raw.get("desc", ""),
            "wage_per_day": raw["wage"],
            "city": city,
            "address": f"{city}, Uttar Pradesh",
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "openings": raw["openings"],
            "filled": 0,
            "start_date": future_date(raw["days"]),
            "status": "open",
        }
        jobs.append(job)
    return jobs


def seed_to_supabase(jobs: list[dict]) -> None:
    """Insert jobs into Supabase."""
    from backend.db.supabase_client import get_supabase
    sb = get_supabase()
    if sb is None:
        print("❌ Supabase not configured — writing to data/jobs_seed_v2.json instead")
        out = ROOT / "data" / "jobs_seed_v2.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ Wrote {len(jobs)} jobs to {out}")
        return

    # Insert in batches of 10
    batch_size = 10
    inserted = 0
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        try:
            res = sb.table("jobs").upsert(batch).execute()
            inserted += len(batch)
            print(f"  Inserted batch {i//batch_size + 1}: {len(batch)} jobs")
        except Exception as e:
            print(f"  Batch {i//batch_size + 1} failed: {e}")

    print(f"✅ Seeded {inserted}/{len(jobs)} jobs to Supabase")


def seed_to_sqlite(jobs: list[dict]) -> None:
    """Insert jobs into SQLite (local dev fallback)."""
    import sqlite3
    db_path = ROOT / "data" / "rozgar.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))

    # Create minimal jobs table if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            employer_id TEXT,
            employer_name TEXT,
            title TEXT NOT NULL,
            title_hindi TEXT NOT NULL,
            role_tag TEXT,
            description TEXT,
            wage_per_day INTEGER,
            city TEXT,
            address TEXT,
            lat REAL,
            lng REAL,
            openings INTEGER DEFAULT 1,
            filled INTEGER DEFAULT 0,
            start_date TEXT,
            status TEXT DEFAULT 'open'
        )
    """)
    conn.commit()

    inserted = 0
    for j in jobs:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO jobs
                (id, employer_id, employer_name, title, title_hindi, role_tag,
                 description, wage_per_day, city, address, lat, lng,
                 openings, filled, start_date, status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                j["id"], j.get("employer_id"), j["employer_name"],
                j["title"], j["title_hindi"], j["role_tag"],
                j.get("description", ""), j["wage_per_day"],
                j["city"], j.get("address", ""), j["lat"], j["lng"],
                j["openings"], j["filled"], j["start_date"], j["status"],
            ))
            inserted += 1
        except Exception as e:
            print(f"  SQLite insert failed for {j['title']}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Seeded {inserted}/{len(jobs)} jobs to SQLite: {db_path}")


def main():
    import random
    random.seed(42)  # Reproducible jitter

    print("=" * 55)
    print("RozgarAI — Job Seed Script")
    print("=" * 55)
    print(f"Building {len(RAW_JOBS)} job postings across {len(CITY_COORDS)} cities...")

    jobs = build_jobs()

    # Also save JSON snapshot for FAISS indexing
    out_json = ROOT / "data" / "jobs_seed_v2.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"📄 JSON snapshot: {out_json}")

    # Try Supabase first, fall back to SQLite
    sb_url = os.getenv("SUPABASE_URL", "")
    if sb_url:
        seed_to_supabase(jobs)
    else:
        print("ℹ️  SUPABASE_URL not set — using SQLite fallback")
        seed_to_sqlite(jobs)

    # City summary
    from collections import Counter
    city_counts = Counter(j["city"] for j in jobs)
    print("\n📍 Jobs by city:")
    for city, count in sorted(city_counts.items()):
        print(f"   {city:20s}: {count} jobs")
    print(f"\n🎯 Total: {len(jobs)} jobs ready")


if __name__ == "__main__":
    main()
