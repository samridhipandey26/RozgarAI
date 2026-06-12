"""
backend/db/supabase_client.py — Supabase client singleton
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

# We support two modes:
#   1. Real Supabase (SUPABASE_URL + SUPABASE_SERVICE_KEY set) — production
#   2. SQLite fallback (DB_PATH set) — local dev without Supabase credentials

_supabase_client = None


def get_supabase():
    """Return the Supabase admin client (uses service key — server-side only)."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()

    if not url or not key:
        return None  # caller must handle gracefully

    try:
        from supabase import create_client
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        print(f"[Supabase] Client init failed: {e}")
        return None


def supabase_available() -> bool:
    return get_supabase() is not None


# ── Helper wrappers ────────────────────────────────────────────────────────────

def sb_insert(table: str, data: dict) -> Optional[dict]:
    """Insert a row. Returns inserted row or None on error."""
    sb = get_supabase()
    if sb is None:
        return None
    try:
        res = sb.table(table).insert(data).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"[Supabase] insert({table}) failed: {e}")
        return None


def sb_upsert(table: str, data: dict, on_conflict: str = "id") -> Optional[dict]:
    """Upsert a row."""
    sb = get_supabase()
    if sb is None:
        return None
    try:
        res = sb.table(table).upsert(data, on_conflict=on_conflict).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"[Supabase] upsert({table}) failed: {e}")
        return None


def sb_select(table: str, filters: dict | None = None, limit: int = 100) -> list:
    """Select rows with optional equality filters."""
    sb = get_supabase()
    if sb is None:
        return []
    try:
        q = sb.table(table).select("*")
        if filters:
            for k, v in filters.items():
                q = q.eq(k, v)
        res = q.limit(limit).execute()
        return res.data or []
    except Exception as e:
        print(f"[Supabase] select({table}) failed: {e}")
        return []


def sb_update(table: str, row_id: str, data: dict) -> Optional[dict]:
    """Update a row by id."""
    sb = get_supabase()
    if sb is None:
        return None
    try:
        res = sb.table(table).update(data).eq("id", row_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"[Supabase] update({table}) failed: {e}")
        return None


def sb_count(table: str, filters: dict | None = None) -> int:
    """Count rows in a table."""
    sb = get_supabase()
    if sb is None:
        return 0
    try:
        q = sb.table(table).select("id", count="exact")
        if filters:
            for k, v in filters.items():
                q = q.eq(k, v)
        res = q.execute()
        return res.count or 0
    except Exception as e:
        print(f"[Supabase] count({table}) failed: {e}")
        return 0


def sb_upload_pdf(bucket: str, path: str, pdf_bytes: bytes) -> Optional[str]:
    """Upload a PDF to Supabase Storage. Returns public URL or None."""
    sb = get_supabase()
    if sb is None:
        return None
    try:
        sb.storage.from_(bucket).upload(
            path, pdf_bytes,
            {"content-type": "application/pdf", "upsert": "true"}
        )
        url = sb.storage.from_(bucket).get_public_url(path)
        return url
    except Exception as e:
        print(f"[Supabase] storage upload failed: {e}")
        return None
