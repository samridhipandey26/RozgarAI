"""
backend/main.py — RozgarAI FastAPI Application
================================================
Start with: uvicorn backend.main:app --reload --port 8000
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="RozgarAI API",
    description="Production API for RozgarAI — Voice-first Hindi job platform for blue-collar workers",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

import os as _os

_DEV_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://192.168.1.7:3000",  # local network dev
]
_PROD_ORIGINS = [
    "https://rozgarai.in",
    "https://www.rozgarai.in",
]
_ALLOW_ORIGINS = _DEV_ORIGINS + _PROD_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOW_ORIGINS,
    allow_origin_regex=r"http://192\.168\.\d+\.\d+:\d+",  # any local IP in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

from backend.routers.auth         import router as auth_router
from backend.routers.pipeline     import router as pipeline_router
from backend.routers.jobs         import router as jobs_router
from backend.routers.applications import router as applications_router
from backend.routers.resumes      import router as resumes_router
from backend.routers.stats        import router as stats_router

app.include_router(auth_router)
app.include_router(pipeline_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(resumes_router)
app.include_router(stats_router)

# ── Static files (serve resumes) ─────────────────────────────────────────────

resumes_dir = ROOT / "data" / "resumes"
resumes_dir.mkdir(parents=True, exist_ok=True)
app.mount("/resumes", StaticFiles(directory=str(resumes_dir)), name="resumes")

# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    from backend.db.supabase_client import supabase_available
    return {
        "status": "ok",
        "version": "2.0.0",
        "supabase": supabase_available(),
    }


@app.get("/")
async def root():
    return {
        "message": "RozgarAI API v2 — Kaam Khojo. Kaam Do. Aaj.",
        "docs": "/api/docs",
    }
