"""
data/db_init.py — SQLite Schema Initialization
===============================================
Creates all tables for RozgarAI prototype database.
Safe to run multiple times (CREATE TABLE IF NOT EXISTS).
"""

import logging
import os
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/rozgar.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection with WAL mode enabled."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Create all tables if they don't exist."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()

        # ── Sessions ──────────────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id      TEXT PRIMARY KEY,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                worker_phone    TEXT,
                status          TEXT DEFAULT 'active',
                mock_mode       INTEGER DEFAULT 0,
                transcript      TEXT,
                raw_input       TEXT
            )
        """)

        # ── Profiles ──────────────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      TEXT NOT NULL,
                profile_json    TEXT NOT NULL,
                resume_path     TEXT,
                tts_path        TEXT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
        """)

        # ── Jobs ──────────────────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id          TEXT PRIMARY KEY,
                employer        TEXT NOT NULL,
                role            TEXT NOT NULL,
                role_hindi      TEXT,
                location        TEXT,
                city            TEXT,
                state           TEXT,
                salary          INTEGER,
                shift           TEXT,
                experience_min  INTEGER DEFAULT 0,
                experience_max  INTEGER DEFAULT 20,
                skills_json     TEXT,
                description_en  TEXT,
                description_hi  TEXT,
                openings        INTEGER DEFAULT 1,
                embedding_json  TEXT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Applications ──────────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                application_id      TEXT PRIMARY KEY,
                session_id          TEXT NOT NULL,
                job_id              TEXT NOT NULL,
                applied_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status              TEXT DEFAULT 'applied',
                status_updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                employer_notified   INTEGER DEFAULT 0,
                match_score         REAL,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id),
                FOREIGN KEY(job_id)     REFERENCES jobs(job_id)
            )
        """)

        # ── Application Status History ─────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id  TEXT NOT NULL,
                status          TEXT NOT NULL,
                changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_hi      TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(application_id)
            )
        """)

        # ── Coaching Sessions ─────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coaching_sessions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      TEXT NOT NULL,
                job_id          TEXT NOT NULL,
                questions_json  TEXT,
                responses_json  TEXT,
                readiness_score INTEGER,
                completed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
        """)

        # ── WhatsApp Message Log ──────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whatsapp_log (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      TEXT,
                direction       TEXT,   -- 'inbound' | 'outbound'
                sender          TEXT,
                body            TEXT,
                media_url       TEXT,
                twilio_sid      TEXT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("Database initialized at: %s", db_path)
        print(f"Database initialized: {db_path}")

    finally:
        conn.close()


def save_session(session_id: str, worker_phone: str, mock_mode: bool = False) -> None:
    """Insert or ignore a new session record."""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO sessions (session_id, worker_phone, mock_mode)
            VALUES (?, ?, ?)
        """, (session_id, worker_phone, int(mock_mode)))
        conn.commit()
    finally:
        conn.close()


def save_profile(session_id: str, profile_json: str, resume_path: str = None, tts_path: str = None) -> None:
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO profiles (session_id, profile_json, resume_path, tts_path)
            VALUES (?, ?, ?, ?)
        """, (session_id, profile_json, resume_path, tts_path))
        conn.commit()
    finally:
        conn.close()


def save_application(application_id: str, session_id: str, job_id: str, match_score: float = 0.0) -> None:
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO applications (application_id, session_id, job_id, match_score)
            VALUES (?, ?, ?, ?)
        """, (application_id, session_id, job_id, match_score))
        conn.commit()
    finally:
        conn.close()


def update_application_status(application_id: str, status: str, message_hi: str = None) -> None:
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE applications SET status=?, status_updated_at=CURRENT_TIMESTAMP
            WHERE application_id=?
        """, (status, application_id))
        conn.execute("""
            INSERT INTO status_history (application_id, status, message_hi)
            VALUES (?, ?, ?)
        """, (application_id, status, message_hi))
        conn.commit()
    finally:
        conn.close()


def log_whatsapp_message(session_id: str, direction: str, body: str, sender: str = None) -> None:
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO whatsapp_log (session_id, direction, sender, body)
            VALUES (?, ?, ?, ?)
        """, (session_id, direction, sender, body))
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
