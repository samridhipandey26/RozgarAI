-- ============================================================
-- RozgarAI — Supabase Postgres Schema
-- Run this in Supabase SQL Editor (Project → SQL Editor → New query)
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── User roles (extends Supabase auth.users) ────────────────
CREATE TABLE IF NOT EXISTS public.user_roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    role        TEXT NOT NULL CHECK (role IN ('worker', 'employer')),
    name        TEXT,
    phone       TEXT UNIQUE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- ── Worker profiles ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.worker_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    name            TEXT NOT NULL,
    city            TEXT NOT NULL,
    lat             DOUBLE PRECISION,
    lng             DOUBLE PRECISION,
    skill           TEXT NOT NULL,         -- primary canonical skill tag
    skills_all      TEXT[] DEFAULT '{}',   -- all skills extracted
    years_exp       INTEGER DEFAULT 0,
    expected_wage   INTEGER DEFAULT 500,
    languages       TEXT[] DEFAULT '{Hindi}',
    education       TEXT DEFAULT 'Not specified',
    raw_transcript  TEXT,
    onboarding_done BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ── Jobs ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id     UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    employer_name   TEXT,
    title           TEXT NOT NULL,
    title_hindi     TEXT NOT NULL,
    role_tag        TEXT NOT NULL,
    description     TEXT,
    wage_per_day    INTEGER NOT NULL,
    city            TEXT NOT NULL,
    address         TEXT,
    lat             DOUBLE PRECISION,
    lng             DOUBLE PRECISION,
    openings        INTEGER DEFAULT 1,
    filled          INTEGER DEFAULT 0,
    start_date      DATE,
    status          TEXT DEFAULT 'open' CHECK (status IN ('open', 'filled', 'cancelled')),
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ── Applications ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.applications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id   UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id      UUID REFERENCES public.jobs(id) ON DELETE CASCADE,
    status      TEXT DEFAULT 'applied'
                    CHECK (status IN ('applied','contacted','confirmed','completed','rejected')),
    otp         TEXT,
    applied_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(worker_id, job_id)
);

-- ── Resumes ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.resumes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id   UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    version     INTEGER DEFAULT 1,
    pdf_url     TEXT,
    pdf_path    TEXT,                   -- local path (fallback if no Supabase storage)
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- ── Pipeline logs ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.pipeline_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id   UUID,
    session_id  TEXT,
    agent_name  TEXT NOT NULL,
    status      TEXT CHECK (status IN ('running','done','error')),
    latency_ms  INTEGER,
    error_msg   TEXT,
    timestamp   TIMESTAMPTZ DEFAULT now()
);

-- ── Row-Level Security ───────────────────────────────────────
ALTER TABLE public.user_roles       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.worker_profiles  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs             ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_logs    ENABLE ROW LEVEL SECURITY;

-- Workers can read/write their own profile
CREATE POLICY "worker_own_profile" ON public.worker_profiles
    FOR ALL USING (auth.uid() = user_id);

-- Jobs are public-read, employer-write
CREATE POLICY "jobs_public_read" ON public.jobs
    FOR SELECT USING (true);
CREATE POLICY "jobs_employer_write" ON public.jobs
    FOR ALL USING (auth.uid() = employer_id);

-- Applications: worker sees own, employer sees applicants for their jobs
CREATE POLICY "applications_worker" ON public.applications
    FOR ALL USING (auth.uid() = worker_id);
CREATE POLICY "applications_employer" ON public.applications
    FOR SELECT USING (
        job_id IN (SELECT id FROM public.jobs WHERE employer_id = auth.uid())
    );
CREATE POLICY "applications_employer_update" ON public.applications
    FOR UPDATE USING (
        job_id IN (SELECT id FROM public.jobs WHERE employer_id = auth.uid())
    );

-- Resumes: worker sees own
CREATE POLICY "resumes_own" ON public.resumes
    FOR ALL USING (auth.uid() = worker_id);

-- Pipeline logs: service role only (bypass RLS)
CREATE POLICY "pipeline_logs_service" ON public.pipeline_logs
    FOR ALL USING (true);

-- user_roles: own record
CREATE POLICY "user_roles_own" ON public.user_roles
    FOR ALL USING (auth.uid() = user_id);

-- ── Indexes ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_jobs_city ON public.jobs(city);
CREATE INDEX IF NOT EXISTS idx_jobs_role ON public.jobs(role_tag);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);
CREATE INDEX IF NOT EXISTS idx_applications_worker ON public.applications(worker_id);
CREATE INDEX IF NOT EXISTS idx_applications_job ON public.applications(job_id);
CREATE INDEX IF NOT EXISTS idx_resumes_worker ON public.resumes(worker_id);
