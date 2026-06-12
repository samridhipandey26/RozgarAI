"""
utils/embeddings.py — OpenAI Embedding + FAISS Index Helpers
=============================================================
FAISS index is pre-built at seed time (db/seed.py).
At runtime, only load_index() is called — never rebuild.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).parent.parent
FAISS_PATH = ROOT / "data" / "jobs.faiss"
META_PATH  = ROOT / "data" / "jobs_faiss_meta.json"

# ── Mock embeddings (no API key needed) ───────────────────────────────────────
_SKILL_VECS: dict[str, np.ndarray] = {}

_CANONICAL_SKILLS = [
    "electrician", "plumber", "loader", "driver", "mason",
    "helper", "welder", "carpenter", "painter", "security_guard",
]

def _get_mock_vec(text: str) -> np.ndarray:
    """Deterministic mock embedding — one-hot over canonical skills."""
    vec = np.zeros(len(_CANONICAL_SKILLS), dtype=np.float32)
    text_lower = text.lower()
    for i, skill in enumerate(_CANONICAL_SKILLS):
        if skill.replace("_", " ") in text_lower or skill in text_lower:
            vec[i] = 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def get_embedding(text: str) -> np.ndarray:
    """Get OpenAI embedding or fall back to mock."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _get_mock_vec(text)
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return np.array(resp.data[0].embedding, dtype=np.float32)
    except Exception:
        return _get_mock_vec(text)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ── FAISS index ────────────────────────────────────────────────────────────────

def build_and_save_index(texts: List[str], ids: List[str], path: str) -> None:
    """Build FAISS flat-L2 index from texts, save to disk."""
    try:
        import faiss
    except ImportError:
        print("faiss-cpu not installed — saving mock embeddings as numpy array")
        vecs = np.stack([get_embedding(t) for t in texts])
        np.save(path + ".npy", vecs)
        Path(META_PATH).write_text(json.dumps(ids), encoding="utf-8")
        return

    vecs = np.stack([get_embedding(t) for t in texts])
    dim  = vecs.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product (cosine after normalize)
    faiss.normalize_L2(vecs)
    index.add(vecs)
    faiss.write_index(index, path)
    Path(META_PATH).write_text(json.dumps(ids), encoding="utf-8")


def load_index():
    """Load FAISS index + id list from disk. Returns (index, ids) or (None, [])."""
    if not FAISS_PATH.exists():
        return None, []
    try:
        import faiss
        index = faiss.read_index(str(FAISS_PATH))
        ids   = json.loads(META_PATH.read_text(encoding="utf-8"))
        return index, ids
    except Exception:
        return None, []


def search_index(query_text: str, k: int = 5) -> List[Tuple[str, float]]:
    """
    Returns top-k (job_id, score) pairs.
    Falls back to mock cosine similarity if FAISS unavailable.
    """
    index, ids = load_index()
    query_vec = get_embedding(query_text)

    if index is None or not ids:
        # Mock: load job data and compute similarity manually
        from utils.embeddings import _mock_search
        return _mock_search(query_vec, k)

    try:
        import faiss
        q = query_vec.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(q)
        scores, indices = index.search(q, min(k, len(ids)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                results.append((ids[idx], float(score)))
        return results
    except Exception:
        return _mock_search(query_vec, k)


def _mock_search(query_vec: np.ndarray, k: int) -> List[Tuple[str, float]]:
    """Mock search using numpy + jobs_seed.json."""
    import json
    from pathlib import Path
    jobs_path = ROOT / "data" / "jobs_seed.json"
    if not jobs_path.exists():
        return []
    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    results = []
    for job in jobs:
        skills_text = " ".join(job["skills_required"])
        jvec = _get_mock_vec(skills_text)
        score = cosine_similarity(query_vec, jvec)
        results.append((job["job_id"], score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]
