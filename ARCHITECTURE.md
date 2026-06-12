# RozgarAI Architecture

## Overview
RozgarAI is a production-grade web application built to connect Indian blue-collar workers with local jobs. It features a unique voice-first onboarding flow that uses a 7-agent AI pipeline to build professional resumes and match workers to jobs using real geocoding and FAISS skill matching.

## Tech Stack
- **Frontend**: Next.js 14 (App Router) + Tailwind CSS + React
- **Backend**: FastAPI (Python 3.10+) + Uvicorn
- **Database/Auth**: Supabase (PostgreSQL + Phone OTP + Storage)
- **AI/ML**: 
  - OpenAI Whisper API (Hindi Voice Transcription)
  - Anthropic Claude 3.5 Sonnet (Skill Extraction, Resume Writing, Interview Coaching)
  - FAISS (Skill Matching Embeddings)
- **Geocoding**: OpenStreetMap Nominatim + Haversine distance
- **PDF Generation**: ReportLab (Custom Hindi-compatible layout)

## The 7-Agent Pipeline
When a worker records a voice note, the FastAPI backend streams Server-Sent Events (SSE) back to the Next.js frontend as each agent completes:

1. **Voice Intake**: Transcribes raw WebM audio via Whisper API. Falls back to text if no mic.
2. **Skill Extractor**: Claude parses the transcript into a structured JSON `WorkerProfile` and geocodes their city.
3. **Resume Builder**: Generates a professional 1-page PDF using ReportLab with custom Hindi fonts. Uploads to Supabase Storage.
4. **Job Matcher**: Queries open jobs from Postgres, ranks them using Haversine distance (<100km) and FAISS skill similarity.
5. **Interview Coach**: Claude generates 3 role-specific interview tips based on the exact job/employer matched.
6. **Apply Agent**: (Blocked by HARD GATE). Once the worker clicks "Apply" on the frontend, this agent generates a 6-digit OTP and creates the application in the DB.
7. **Status Tracker**: Polls the DB for employer updates and emits WhatsApp-style status messages to the worker.

## Database Schema (Supabase)
- `users`: Managed by Supabase Auth (Phone OTP).
- `user_roles`: Maps `auth.users.id` to `role` ('worker' | 'employer').
- `worker_profiles`: Name, city, lat, lng, skills array, expected wage, transcript.
- `jobs`: Employer ID, title, role, wage, city, lat, lng, openings, status.
- `applications`: Worker ID, Job ID, OTP, status ('applied', 'contacted', 'confirmed', 'completed').
- `resumes`: Versioned PDF URLs pointing to Supabase Storage buckets.
- `pipeline_logs`: Audit trail of AI agent latencies.

## Fallback Mechanisms
The backend is designed to run locally even without external services (except LLM APIs):
- **No Supabase?** It falls back to local SQLite (`rozgar.db`) and local file storage for PDFs and JSON seed files.
- **No Nominatim?** Uses hardcoded coordinate lookup tables for 10 major UP cities.

## API Endpoints
- `POST /api/auth/send-otp`
- `POST /api/auth/verify-otp`
- `POST /api/pipeline/start` (multipart/form-data for audio)
- `GET /api/pipeline/stream/{session_id}` (SSE)
- `GET /api/jobs/match`
- `POST /api/applications/`

## Deployment
- **Frontend**: Deploy on Vercel. Ensure `NEXT_PUBLIC_API_URL` points to the backend.
- **Backend**: Deploy on Render / AWS AppRunner. Needs `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `SUPABASE_*` credentials.
