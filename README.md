# CaForB — Innovation Decision-Support Tool

CaForB is a web application that helps companies assess their innovation maturity and generates
tailored, AI-driven advisory reports with concrete opportunities, next steps, and identified
weaknesses. It is the working prototype developed for the MSc dissertation *"The Role of
Innovation in Driving Business Growth"* (David Palhas, ISCTE-IUL, 2026).

## What it does

- **Multi-step assessment** — a guided questionnaire covering company profile, innovation state,
  strategic goals, internal capabilities, and pain points.
- **Multi-model insight generation (A/B)** — every assessment produces one advisory report per
  configured LLM (`gemma4:12B` baseline and `caforb-v1` fine-tuned by default), each with a
  maturity score (0–10), opportunities, next steps, and key weaknesses. The user can compare
  variants and select a primary one.
- **Re-assessment with score deltas** — later assessments carry forward prior opportunities and
  inject assessment history into the prompt; score deltas are computed server-side.
- **Chatbot over results** — ask follow-up questions about a completed report, grounded in its
  context (no vector DB).
- **Accounts & scoping** — register/login; companies and reports are scoped per user, with a
  dashboard and per-company history/trend view.

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.0.6 + Strawberry GraphQL (GraphQL endpoint at `/graphql/`) |
| Frontend | Next.js 16.2.7 (App Router, Turbopack) + Apollo Client + Tailwind CSS v4 |
| LLM runtime | Ollama (local, `:11434`) |
| Database | SQLite (dev) — PostgreSQL is a production target |
| Tests | Django `TestCase` (backend) · Vitest (frontend) |

## Project structure

```
CaForB/
├── backend/        # Django project config (settings, urls, asgi/wsgi)
├── core/           # main app: models, GraphQL schema, LLM service, memory, tests
│   └── services/
│       ├── llm_services.py   # all LLM interaction (generation, chat, retries)
│       └── memory.py         # assessment history & score trends
├── frontend/       # Next.js app (App Router, Apollo, Tailwind)
├── datasets_treino_finetune/  # standalone fine-tuning data pipeline (see its README)
└── manage.py       # Django entry point
```

## Prerequisites

- Python 3.12
- Node.js 20+ (Node 20.18+ recommended for Next.js 16)
- [Ollama](https://ollama.com) with these models pulled:
  - `gemma4:12B` — baseline generation model (`ollama pull gemma4:12B`)
  - `caforb-v1` — fine-tuned model, created from the LoRA/GGUF (see
    `datasets_treino_finetune/`, `ollama create caforb-v1 -f datasets_treino_finetune/Modelfile`)
  - `qwen2.5:7b-instruct` — the results chatbot model (`ollama pull qwen2.5:7b-instruct`)

## Setup

### Backend

```bash
python -m venv .venv
# activate, then:
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000     # GraphQL at http://localhost:8000/graphql/
```

> Note: development used a Windows virtualenv under WSL. On Windows the interpreter lives at
> `.venv\Scripts\python.exe`; on Linux/macOS it is `.venv/bin/python`.

### Frontend

```bash
cd frontend
npm install
npm run dev                         # http://localhost:3000
```

### LLM daemon

```bash
ollama serve                        # localhost:11434
```

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CAFORB_MODELS` | `gemma4:12B,caforb-v1` | Models to generate an insight from (one report each) |
| `CAFORB_DEFAULT_MODEL` | `caforb-v1` | Model marked as the selected/primary output |
| `SECRET_KEY` | (in `settings.py`) | Django secret key |
| `CHAT_MODEL` | `qwen2.5:7b-instruct` | Model used by the results chatbot |

CORS is locked to `http://localhost:3000` with credentials allowed.

## Tests

```bash
# Backend (no Ollama required — LLM calls are mocked)
python manage.py test core

# Frontend
cd frontend
npm run build       # TypeScript + Next.js production build (authoritative gate)
npm test            # Vitest unit/snapshot tests
```

## Notes

- `README.md` in the repo root describes the app; `SPEC.md` (if present locally) contains the
  original design spec and may be stale.
- `datasets_treino_finetune/` is an independent fine-tuning pipeline (templates → training data →
  LoRA → GGUF) that produced `caforb-v1`. It is not required to run the app.
