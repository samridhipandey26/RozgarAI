# RozgarAI

Kaam Khojo. Kaam Do. Aaj.

RozgarAI is a voice-first job matching platform designed specifically for Indian blue-collar workers. It uses a 7-agent LangGraph pipeline to convert a 30-second Hindi voice note into a professional resume and match the worker with local jobs.

## Development Setup

The application is split into a Next.js frontend and a FastAPI backend.

### 1. Backend Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example` with your Supabase, OpenAI, and Anthropic keys.

Run the backend:
```bash
uvicorn backend.main:app --reload --port 8000
```
The API docs will be available at `http://localhost:8000/api/docs`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:3000`.

## Features
- **Voice Onboarding**: Speak in Hindi, get a professional profile.
- **AI Resume Builder**: Auto-generates a one-page PDF resume with translations.
- **Smart Job Matching**: Ranks jobs based on location (Haversine distance) and skills (FAISS embeddings).
- **Interview Coach**: Provides 3 actionable tips for the specific job before applying.
- **HARD GATE Confirmation**: Workers must explicitly confirm before an application is submitted.
- **Real-time Pipeline**: Watch the AI agents work in real-time via Server-Sent Events (SSE).
