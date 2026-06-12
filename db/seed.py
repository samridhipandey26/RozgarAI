"""
db/seed.py — RozgarAI Database Seeder
======================================
Run: python db/seed.py

1. Creates / recreates data/rozgar.db
2. Executes schema.sql
3. Inserts seed workers, contractors, jobs
4. Builds FAISS index from job embeddings -> data/jobs.faiss
5. Prints summary
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

DB_PATH     = ROOT / "data" / "rozgar.db"
SCHEMA_PATH = ROOT / "db" / "schema.sql"
JOBS_PATH   = ROOT / "data" / "jobs_seed.json"
WORKERS_PATH= ROOT / "data" / "workers_seed.json"
FAISS_PATH  = ROOT / "data" / "jobs.faiss"
RESUMES_DIR = ROOT / "data" / "resumes"

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# Contractors (hardcoded — 3 per spec)
# ─────────────────────────────────────────────────────────────────────────────
CONTRACTORS = [
    {"contractor_id": "c001", "name": "Ashok Builders",    "phone": "+919901234567",
     "company_name": "Ashok Construction Pvt Ltd", "city": "Lucknow",  "verified": True},
    {"contractor_id": "c002", "name": "Mehta Infra",       "phone": "+919912345678",
     "company_name": "Mehta Infrastructure",       "city": "Agra",    "verified": True},
    {"contractor_id": "c003", "name": "Singh Logistics",   "phone": "+919923456789",
     "company_name": "Singh Transport & Warehousing","city": "Varanasi", "verified": False},
]


def create_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Dropped existing DB: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    print(f"Created DB: {DB_PATH}")
    return conn


def insert_contractors(conn: sqlite3.Connection) -> None:
    for c in CONTRACTORS:
        conn.execute(
            "INSERT OR IGNORE INTO contractors "
            "(contractor_id, name, phone, company_name, city, verified) "
            "VALUES (?,?,?,?,?,?)",
            (c["contractor_id"], c["name"], c["phone"],
             c["company_name"], c["city"], c["verified"]),
        )
    conn.commit()
    print(f"Inserted {len(CONTRACTORS)} contractors")


def insert_workers(conn: sqlite3.Connection) -> None:
    workers = json.loads(WORKERS_PATH.read_text(encoding="utf-8"))
    for w in workers:
        conn.execute(
            "INSERT OR IGNORE INTO workers "
            "(worker_id, name, phone, city, pin_code, skills, "
            " experience_years, preferred_wage_per_day, trust_score, total_jobs_done) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (w["worker_id"], w["name"], w["phone"], w["city"], w["pin_code"],
             json.dumps(w["skills"]), w["experience_years"],
             w["preferred_wage_per_day"], w["trust_score"], w["total_jobs_done"]),
        )
    conn.commit()
    print(f"Inserted {len(workers)} workers")


def insert_jobs(conn: sqlite3.Connection) -> None:
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    for j in jobs:
        conn.execute(
            "INSERT OR IGNORE INTO jobs "
            "(job_id, contractor_id, title, title_hindi, location, pin_code, "
            " wage_per_day, skills_required, start_date, openings) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (j["job_id"], j["contractor_id"], j["title"], j["title_hindi"],
             j["location"], j["pin_code"], j["wage_per_day"],
             json.dumps(j["skills_required"]), j["start_date"], j["openings"]),
        )
    conn.commit()
    print(f"Inserted {len(jobs)} jobs")


def build_faiss_index() -> None:
    """Build FAISS index from job skill embeddings. Saves to data/jobs.faiss."""
    from utils.embeddings import build_and_save_index
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    job_texts = [
        f"Job: {j['title']}. Skills needed: {', '.join(j['skills_required'])}. "
        f"Location: {j['location']}."
        for j in jobs
    ]
    job_ids = [j["job_id"] for j in jobs]
    build_and_save_index(job_texts, job_ids, str(FAISS_PATH))
    print(f"FAISS index saved: {FAISS_PATH}")


def print_summary(conn: sqlite3.Connection) -> None:
    print("\n" + "=" * 50)
    print("RozgarAI Seed Summary")
    print("=" * 50)
    for table in ("workers", "contractors", "jobs", "applications", "sessions"):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:20s}: {count:4d} rows")
    print("=" * 50)
    faiss_ok = FAISS_PATH.exists()
    print(f"  FAISS index       : {'OK' if faiss_ok else 'MISSING (run without OPENAI_API_KEY for mock mode)'}")
    print("=" * 50)
    print("Setup complete! Run: streamlit run app.py")


def main() -> None:
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)

    conn = create_db()
    insert_contractors(conn)
    insert_workers(conn)
    insert_jobs(conn)

    # FAISS is optional — requires OPENAI_API_KEY
    if os.getenv("OPENAI_API_KEY"):
        try:
            build_faiss_index()
        except Exception as e:
            print(f"FAISS index skipped: {e}")
    else:
        print("OPENAI_API_KEY not set — skipping FAISS index (mock mode will be used)")

    print_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
