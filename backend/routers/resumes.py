"""
backend/routers/resumes.py — Resume generation and download
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.schemas.models import ResumeResponse, ResumeListResponse

router = APIRouter(prefix="/api/resumes", tags=["resumes"])
security = HTTPBearer(auto_error=False)


def _require_user(credentials) -> str:
    if not credentials:
        raise HTTPException(401, "Authentication required")
    try:
        from backend.db.supabase_client import get_supabase
        sb = get_supabase()
        if sb:
            user_resp = sb.auth.get_user(credentials.credentials)
            return user_resp.user.id
    except Exception:
        pass
    raise HTTPException(401, "Invalid token")


def _get_worker_profile(user_id: str) -> dict | None:
    from backend.db.supabase_client import sb_select, supabase_available
    if supabase_available():
        profiles = sb_select("worker_profiles", {"user_id": user_id}, limit=1)
        return profiles[0] if profiles else None
    return None


# ── Generate resume ───────────────────────────────────────────────────────────

@router.post("/generate", response_model=ResumeResponse, status_code=201)
async def generate_resume(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Generate (or regenerate) a PDF resume for the authenticated worker.
    Saves to local disk + Supabase Storage, inserts versioned row in resumes table.
    """
    user_id = _require_user(credentials)

    # Get worker profile
    profile = _get_worker_profile(user_id)
    if not profile:
        raise HTTPException(404, "Worker profile not found — complete onboarding first")

    # Determine next version
    from backend.db.supabase_client import sb_select, sb_insert, sb_upload_pdf, supabase_available
    existing = sb_select("resumes", {"worker_id": user_id}, limit=100) if supabase_available() else []
    version = len(existing) + 1

    # Generate PDF
    try:
        from utils.pdf_gen import generate_resume_pdf_v2
        pdf_path = generate_resume_pdf_v2(
            worker_id=user_id,
            name=profile.get("name", "Kaamgar"),
            role=profile.get("skill", "Worker"),
            city=profile.get("city", ""),
            years_exp=profile.get("years_exp", 0),
            phone="",  # phone not stored in profile for privacy
            skills=profile.get("skills_all") or [profile.get("skill", "helper")],
            education=profile.get("education", "Not specified"),
            languages=profile.get("languages") or ["Hindi"],
            expected_wage=profile.get("expected_wage", 500),
            raw_transcript=profile.get("raw_transcript", ""),
            version=version,
        )
    except Exception as e:
        raise HTTPException(500, f"Resume generation failed: {e}")

    # Upload to Supabase Storage
    pdf_url = None
    if supabase_available():
        try:
            pdf_bytes = Path(pdf_path).read_bytes()
            storage_path = f"resumes/{user_id}/v{version}.pdf"
            pdf_url = sb_upload_pdf("resumes", storage_path, pdf_bytes)
        except Exception as e:
            print(f"[Resume] Storage upload failed (non-critical): {e}")

    # Insert versioned record
    import time as _time
    resume_data = {
        "worker_id": user_id,
        "version": version,
        "pdf_url": pdf_url,
        "pdf_path": str(pdf_path),
        "created_at": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime()),
    }

    resume_id = None
    if supabase_available():
        inserted = sb_insert("resumes", resume_data)
        resume_id = str(inserted["id"]) if inserted else None

    if not resume_id:
        import uuid
        resume_id = str(uuid.uuid4())

    return ResumeResponse(
        id=resume_id,
        worker_id=user_id,
        version=version,
        pdf_url=pdf_url,
        pdf_path=str(pdf_path),
    )


# ── Download resume ───────────────────────────────────────────────────────────

@router.get("/download/{resume_id}")
async def download_resume(
    resume_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Download a resume PDF. Returns the file directly."""
    user_id = _require_user(credentials)

    from backend.db.supabase_client import sb_select, supabase_available

    # Find the resume record
    if supabase_available():
        resumes = sb_select("resumes", {"worker_id": user_id}, limit=100)
        resume = next((r for r in resumes if str(r.get("id")) == resume_id), None)
    else:
        # Try to find local file
        resume = None

    if not resume:
        # Try latest resume for this user
        resumes_dir = ROOT / "data" / "resumes"
        pdf_files = list(resumes_dir.glob(f"{user_id}*.pdf"))
        if pdf_files:
            latest = sorted(pdf_files)[-1]
            return FileResponse(
                str(latest),
                media_type="application/pdf",
                filename=f"RozgarAI_Resume.pdf",
            )
        raise HTTPException(404, "Resume not found")

    pdf_path = resume.get("pdf_path") or resume.get("pdf_url")
    if not pdf_path:
        raise HTTPException(404, "Resume file not found")

    # If it's a URL, redirect
    if pdf_path.startswith("http"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(pdf_path)

    # Local file
    if not Path(pdf_path).exists():
        raise HTTPException(404, "Resume file missing from disk")

    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=f"RozgarAI_Resume_v{resume.get('version', 1)}.pdf",
    )


# ── Download latest resume (convenience) ─────────────────────────────────────

@router.get("/latest")
async def download_latest_resume(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Download worker's latest resume PDF."""
    user_id = _require_user(credentials)

    from backend.db.supabase_client import sb_select, supabase_available

    if supabase_available():
        resumes = sb_select("resumes", {"worker_id": user_id}, limit=100)
        if resumes:
            # Sort by version desc
            latest = sorted(resumes, key=lambda r: r.get("version", 0), reverse=True)[0]
            pdf_path = latest.get("pdf_path")
            pdf_url = latest.get("pdf_url")

            if pdf_url and pdf_url.startswith("http"):
                from fastapi.responses import RedirectResponse
                return RedirectResponse(pdf_url)
            if pdf_path and Path(pdf_path).exists():
                return FileResponse(
                    str(pdf_path), media_type="application/pdf",
                    filename="RozgarAI_Resume.pdf"
                )

    # Fallback: scan local resumes dir
    resumes_dir = ROOT / "data" / "resumes"
    pdf_files = list(resumes_dir.glob(f"*{user_id[:8]}*.pdf")) if user_id else []
    if not pdf_files:
        pdf_files = list(resumes_dir.glob("*.pdf"))

    if pdf_files:
        latest_file = sorted(pdf_files)[-1]
        return FileResponse(
            str(latest_file), media_type="application/pdf",
            filename="RozgarAI_Resume.pdf"
        )

    raise HTTPException(404, "No resume found — complete onboarding first")


# ── List resume versions ──────────────────────────────────────────────────────

@router.get("/list", response_model=ResumeListResponse)
async def list_resumes(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """List all resume versions for the authenticated worker."""
    user_id = _require_user(credentials)

    from backend.db.supabase_client import sb_select, supabase_available

    if supabase_available():
        resumes_data = sb_select("resumes", {"worker_id": user_id}, limit=20)
    else:
        resumes_data = []

    resumes = [
        ResumeResponse(
            id=str(r["id"]),
            worker_id=user_id,
            version=r.get("version", 1),
            pdf_url=r.get("pdf_url"),
            pdf_path=r.get("pdf_path"),
            created_at=str(r.get("created_at", "")),
        )
        for r in resumes_data
    ]
    resumes.sort(key=lambda r: r.version, reverse=True)
    return ResumeListResponse(
        resumes=resumes,
        latest=resumes[0] if resumes else None,
    )
