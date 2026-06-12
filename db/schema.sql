-- db/schema.sql — RozgarAI Canonical SQLite Schema

CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    city TEXT NOT NULL,
    pin_code TEXT NOT NULL,
    skills TEXT NOT NULL,
    experience_years INTEGER DEFAULT 0,
    preferred_wage_per_day INTEGER DEFAULT 0,
    trust_score REAL DEFAULT 3.0,
    total_jobs_done INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contractors (
    contractor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    company_name TEXT,
    city TEXT NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    contractor_id TEXT NOT NULL REFERENCES contractors(contractor_id),
    title TEXT NOT NULL,
    title_hindi TEXT NOT NULL,
    location TEXT NOT NULL,
    pin_code TEXT NOT NULL,
    wage_per_day INTEGER NOT NULL,
    skills_required TEXT NOT NULL,
    start_date TEXT NOT NULL,
    openings INTEGER DEFAULT 1,
    filled INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    application_id TEXT PRIMARY KEY,
    worker_id TEXT NOT NULL REFERENCES workers(worker_id),
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    status TEXT DEFAULT 'pending',
    otp TEXT,
    otp_verified BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    worker_phone TEXT,
    stage_reached TEXT,
    transcript TEXT,
    matched_job_ids TEXT,
    outcome TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
