# RozgarAI 🔧📍

**Kaam Khojo. Kaam Do. Aaj.**

India's Agentic AI platform for blue-collar job matching in tier-2/3 UP cities.

---

## Setup

1. Clone repo and `cd rozgar-ai`
2. `py -m venv venv && venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` → `.env` and fill in API keys *(optional — works without keys in Demo Mode)*
5. `python download_font.py` — downloads Hindi font for PDFs
6. `python db/seed.py` — creates DB + FAISS index
7. `streamlit run app.py`

---

## Architecture

7-agent LangGraph pipeline:

```
Voice Intake → Skill Extractor → Resume Builder → Job Matcher
    → Interview Coach → [CONSENT GATE] → Apply Agent → Status Tracker
```

Each agent is a pure function `f(RozgarState) -> RozgarState` with no Streamlit imports.

---

## Demo Flow (11 steps)

| Step | Action | Result |
|------|--------|--------|
| 1 | Open app | Stats bar + grey dots |
| 2 | Toggle Demo Mode | Raju's profile pre-filled |
| 3 | Click **Kaam Dhundo** | Agent 1 pulses orange |
| 4 | Agent 1 → done | Hindi transcript in log |
| 5 | Agent 2 → done | Worker profile card appears |
| 6 | Agent 3 → done | PDF download link |
| 7 | Agent 4 → done | 3 job cards with match % |
| 8 | Agent 5 → done | 3 Hindi interview tips |
| 9 | WhatsApp shows job alert | Haan/Nahi buttons appear |
| 10 | Click **Haan** | OTP appears in WhatsApp |
| 11 | Agent 7 → done | All green + confetti 🎉 |

---

## File Structure

```
rozgar-ai/
├── app.py                    # Streamlit entry point
├── agents/                   # 7 agent modules
├── pipeline/state.py         # Typed RozgarState dataclass
├── pipeline/graph.py         # LangGraph StateGraph
├── pipeline/runner.py        # Streaming + sync runner
├── db/schema.sql             # SQLite schema
├── db/models.py              # SQLAlchemy ORM
├── db/seed.py                # Seed data + FAISS index builder
├── ui/components.py          # Reusable Streamlit components
├── ui/styles.css             # Full dark-theme CSS
├── ui/strings_hi.py          # All Hindi string constants
├── utils/asr.py              # Whisper wrapper
├── utils/tts.py              # gTTS wrapper
├── utils/pdf_gen.py          # ReportLab PDF generator
├── utils/embeddings.py       # OpenAI/FAISS helpers
├── data/jobs_seed.json       # 8 seed jobs
├── data/workers_seed.json    # 10 seed workers
└── tests/                    # pytest test suite
```

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Orchestration | LangGraph StateGraph |
| LLM | Claude Sonnet (`claude-sonnet-4-6`) |
| ASR | OpenAI Whisper (`whisper-1`, `lang=hi`) |
| TTS | Google gTTS (`lang='hi'`) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Store | FAISS (local, no server) |
| Database | SQLite + SQLAlchemy ORM |
| PDF | ReportLab + Noto Sans Devanagari |
| Demo UI | Streamlit |

---

## Hard Constraints (Enforced)

- No Aadhaar integration
- No real Twilio calls (WhatsApp simulated in UI)
- Apply agent **will not proceed** unless `apply_confirmed is True`
- No loose dicts between agents — only typed `RozgarState`
- No Streamlit imports inside `agents/`
- FAISS index pre-built at seed time

---

*Built for India's 450 million informal workers. If Raju would be confused by it, we removed it.*
