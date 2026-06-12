"""agents/resume_builder.py — Agent 3: Resume Builder (Production)
Generates PDF, uploads to Supabase Storage, saves versioned DB record.
"""
from __future__ import annotations

import os
from pathlib import Path

from pipeline.state import PipelineStage, RozgarState


def resume_builder(state: RozgarState) -> RozgarState:
    """
    Agent 3 — Resume Builder
    Input:  state.worker (WorkerProfile with all fields)
    Output: state.resume_pdf_path (local path to generated PDF)
    """
    try:
        state.current_stage = PipelineStage.RESUME_BUILD

        if state.worker is None:
            raise ValueError("Worker profile not set — run skill_extractor first")

        state.log("📄 Resume Builder: Generating professional PDF...")

        w = state.worker
        user_id = getattr(state, "user_id", None) or w.worker_id

        # Determine version
        version = _get_next_version(user_id)

        from utils.pdf_gen import generate_resume_pdf_v2
        pdf_path = generate_resume_pdf_v2(
            worker_id=user_id,
            name=w.name,
            role=w.skills[0] if w.skills else "helper",
            city=w.city,
            years_exp=w.experience_years,
            phone=w.phone if w.phone != "+919999999999" else "",
            skills=w.skills,
            expected_wage=w.preferred_wage_per_day,
            raw_transcript=state.transcript_hindi or "",
            version=version,
        )

        state.resume_pdf_path = pdf_path
        state.log(f"✅ Resume Builder: PDF saved to {Path(pdf_path).name}")

        # Upload to Supabase Storage
        pdf_url = _upload_to_storage(user_id, pdf_path, version)

        # Save to resumes table
        _save_resume_record(user_id, version, pdf_path, pdf_url)

        state.add_wa_message(
            "bot",
            f"✅ Aapki professional resume taiyaar ho gayi!\n\n"
            f"📄 {w.name} — {w.skills[0].replace('_', ' ').title() if w.skills else 'Worker'}\n"
            f"Dashboard se download karein."
        )

    except Exception as e:
        state.error_message = str(e)
        state.current_stage = PipelineStage.ERROR

    return state


def _get_next_version(user_id: str) -> int:
    try:
        from backend.db.supabase_client import sb_select, supabase_available
        if supabase_available():
            existing = sb_select("resumes", {"worker_id": user_id}, limit=100)
            return len(existing) + 1
    except Exception:
        pass
    return 1


def _upload_to_storage(user_id: str, pdf_path: str, version: int) -> str | None:
    try:
        from backend.db.supabase_client import sb_upload_pdf, supabase_available
        if not supabase_available():
            return None
        pdf_bytes = Path(pdf_path).read_bytes()
        storage_path = f"resumes/{user_id}/v{version}.pdf"
        return sb_upload_pdf("resumes", storage_path, pdf_bytes)
    except Exception as e:
        print(f"[ResumeBuilder] Storage upload failed (non-critical): {e}")
        return None


def _save_resume_record(user_id: str, version: int, pdf_path: str, pdf_url: str | None) -> None:
    try:
        from backend.db.supabase_client import sb_insert, supabase_available
        import time
        if supabase_available():
            sb_insert("resumes", {
                "worker_id": user_id,
                "version": version,
                "pdf_url": pdf_url,
                "pdf_path": str(pdf_path),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
    except Exception as e:
        print(f"[ResumeBuilder] DB record save failed (non-critical): {e}")
