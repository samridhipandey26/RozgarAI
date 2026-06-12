"""
data/generate_embeddings.py — Pre-compute Job Embeddings
=========================================================
One-time script to generate and cache OpenAI embeddings
for all job listings in jobs_seed.json.

Run once:  python data/generate_embeddings.py

Requires OPENAI_API_KEY in .env
Saves: data/jobs_embeddings.npy
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

JOBS_PATH       = ROOT / "data" / "jobs_seed.json"
EMBEDDINGS_PATH = ROOT / "data" / "jobs_embeddings.npy"


def build_job_text(job: dict) -> str:
    """Build rich text representation of a job for embedding."""
    return (
        f"Job role: {job.get('role', '')}. "
        f"Employer: {job.get('employer', '')}. "
        f"Location: {job.get('location', '')}. "
        f"Skills required: {', '.join(job.get('skills_required', []))}. "
        f"Description: {job.get('description_en', '')}. "
        f"Shift: {job.get('shift', '')}. "
        f"Salary: {job.get('salary', 0)} per month."
    )


def generate_embeddings() -> None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("❌ OPENAI_API_KEY not set. Set it in .env and retry.")
        print("   To use mock mode without embeddings, just run the dashboard directly.")
        sys.exit(1)

    import openai
    import numpy as np

    client = openai.OpenAI(api_key=api_key)

    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    print(f"📊 Generating embeddings for {len(jobs)} jobs...")
    embeddings = []

    for i, job in enumerate(jobs):
        text = build_job_text(job)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        emb = response.data[0].embedding
        embeddings.append(emb)
        print(f"  [{i+1}/{len(jobs)}] ✓ {job['employer']} — {job['role']}")

    np.save(str(EMBEDDINGS_PATH), embeddings)
    print(f"\n✅ Embeddings saved to: {EMBEDDINGS_PATH}")
    print(f"   Shape: {len(embeddings)} x {len(embeddings[0])} dimensions")


if __name__ == "__main__":
    generate_embeddings()
