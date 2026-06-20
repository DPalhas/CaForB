# CaForB — Innovation Decision-Support Tool
## Architecture Reference Document

> **Project:** MSc Dissertation Prototype — "The Role of Innovation in Driving Business Growth"  
> **Author:** David Palhas | ISCTE-IUL, 2026  
> **Stack:** Django + Strawberry GraphQL (backend) · Next.js App Router (frontend) · PostgreSQL · Ollama + Gemma4 (LLM)  
> **Last updated:** June 2026

---

## 1. Directory Structure

```
CaForB/
├── .venv/                          # Python virtual environment
│
├── backend/                        # Django project config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # DB, CORS, installed apps, Strawberry config
│   ├── urls.py                     # Mounts GraphQL endpoint (/graphql/)
│   └── wsgi.py
│
├── core/                           # Main Django app
│   ├── migrations/
│   │   └── __init__.py
│   ├── services/
│   │   └── llm_service.py          # InnovationAIService — ALL LLM interaction isolated here
│   ├── __init__.py
│   ├── admin.py                    # Model registration for Django admin
│   ├── apps.py
│   ├── models.py                   # Company, QuestionnaireResponse, InnovationInsight, LLMTrace
│   ├── schema.py                   # Strawberry GraphQL types, queries, mutations
│   ├── tests.py
│   └── views.py
│
├── frontend/                       # Next.js App Router project
│   ├── .next/                      # Build output (auto-generated)
│   │   └── types/
│   │       ├── cache-life.d.ts
│   │       ├── routes.d.ts
│   │       └── validator.ts
│   ├── app/                        # App Router root
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx              # Root layout (fonts, providers)
│   │   └── page.tsx                # Landing / entry page
│   ├── public/
│   ├── node_modules/
│   ├── .gitignore
│   ├── AGENTS.md                   # Claude Code agent instructions
│   ├── CLAUDE.md                   # Claude Code project context
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── next-env.d.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.mjs
│   ├── README.md
│   └── tsconfig.json
│
└── README.md
```

---

## 2. Backend Architecture

### Django Apps
| App | Role |
|-----|------|
| `backend/` | Project config — settings, URL routing, ASGI/WSGI |
| `core/` | All business logic — models, GraphQL schema, AI service |

### Key Models (`core/models.py`)
```python
Company                  # Company profile (name, sector, size)
QuestionnaireResponse    # Raw answers (JSONField) linked to a Company
InnovationInsight        # AI output linked 1:1 to a QuestionnaireResponse
LLMTrace                 # Per-call log (input, output, duration) — agent-ready
```
> `LLMTrace` is intentionally included now even though only 1 row is written per session.
> When an agent loop is added, this table captures the full multi-step reasoning chain.

### AI Service Layer (`core/services/llm_service.py`)
- **Class:** `InnovationAIService`
- **Method:** `analyse(company: dict, answers: dict) -> dict`
- Internally calls Ollama (`http://localhost:11434`) with model `gemma4`
- Returns **structured JSON** (maturity score, opportunities, next steps)
- The GraphQL schema never calls Ollama directly — always goes through this class
- **Agent upgrade path:** swap internals of this class only; callers unchanged

### GraphQL (`core/schema.py`)
- Library: **Strawberry** (`strawberry-graphql-django`)
- Endpoint: `/graphql/`
- Current mutations:
  - `submitQuestionnaire(...)` → triggers AI analysis → returns `InsightType`
- Current queries:
  - `getInsight(id)` → returns stored insight

---

## 3. Frontend Architecture

### Framework
- **Next.js** with App Router (`/app` directory)
- **TypeScript** enabled
- **Tailwind CSS** for styling
- GraphQL client: **Apollo Client** (`@apollo/client`)

### Planned Pages (`/app`)
| Route | Page | Status |
|-------|------|--------|
| `/` | Landing / Welcome | 🔲 To build |
| `/assessment` | Multi-step questionnaire | 🔲 To build |
| `/results/[id]` | Innovation insights dashboard | 🔲 To build |
| `/results/[id]/report` | Printable report view | 🔲 To build |

### Questionnaire Sections (maps to agent tools later)
1. `company_profile` — name, sector, size, age
2. `innovation_state` — current practices, past initiatives
3. `strategic_goals` — objectives, time horizon
4. `internal_capabilities` — team, resources, digital maturity
5. `pain_points` — barriers, constraints

---

## 4. LLM Integration

| Setting | Value |
|---------|-------|
| Runtime | Ollama (local) |
| Model | `gemma4` |
| Endpoint | `http://localhost:11434` |
| Protocol | Ollama Python SDK (`ollama.chat()`) |
| Input format | Structured JSON (company + answers) |
| Output format | Structured JSON (score + opportunities + next steps) |

### Prompt Output Contract
```json
{
  "maturity_score": 0.0,
  "opportunities": [
    {
      "type": "incremental | radical",
      "title": "string",
      "rationale": "string",
      "impact": "low | medium | high",
      "difficulty": "low | medium | high",
      "timeframe": "string"
    }
  ],
  "next_steps": ["string"],
  "key_weaknesses": ["string"]
}
```

---

## 5. Agent-Readiness Decisions

These are design choices made **now** that cost nothing but remove friction when an agent is added later:

| Decision | Current behaviour | Future agent behaviour |
|----------|------------------|----------------------|
| `InnovationAIService` isolation | Single Gemma4 call | Replace internals with agent loop |
| Structured JSON prompt contract | Prompt returns JSON | Same schema registered as tool definition |
| `LLMTrace` model | 1 row per session | N rows per session (full trace) |
| `context_bundle` JSONField on `InnovationInsight` | Stores `{}` | Populated with RAG chunks / tool results |
| Questionnaire sections as named blocks | UI steps only | Each section = callable agent tool |

---

## 6. Development Environment

```bash
# Backend
source .venv/bin/activate
cd backend && python manage.py runserver   # http://localhost:8000/graphql/

# Frontend
cd frontend && npm run dev                 # http://localhost:3000

# LLM
ollama serve                               # http://localhost:11434
ollama run gemma4
```

### Key dependencies
**Backend:** `django`, `strawberry-graphql-django`, `psycopg2-binary`, `ollama`, `django-cors-headers`  
**Frontend:** `next`, `react`, `typescript`, `tailwindcss`, `@apollo/client`, `graphql`

---

## 7. Current Build Status

| Component | Status |
|-----------|--------|
| Django project scaffold | ✅ Done |
| `core` app created | ✅ Done |
| `core/services/llm_service.py` exists | ✅ Done |
| `core/models.py` — models defined | 🔲 To confirm |
| `core/schema.py` — GraphQL schema | 🔲 To confirm |
| Next.js scaffold | ✅ Done |
| Apollo Client setup | 🔲 To build |
| Questionnaire pages | 🔲 To build |
| Results dashboard | 🔲 To build |
| Ollama + Gemma4 running locally | 🔲 To confirm |
| PostgreSQL connected | 🔲 To confirm |

---

## 8. What's Missing vs. Planned Structure

Based on current file tree, the following still need to be created:

**Backend (`core/`):**
- `models.py` — needs `Company`, `QuestionnaireResponse`, `InnovationInsight`, `LLMTrace` defined
- `schema.py` — needs Strawberry types and `submitQuestionnaire` mutation
- `llm_service.py` — needs `InnovationAIService` class implemented
- `admin.py` — register all models

**Frontend (`/app`):**
- `/app/assessment/` — questionnaire flow
- `/app/results/[id]/` — dashboard page
- `lib/apollo-client.ts` — Apollo Client config
- `lib/graphql/mutations.ts` — GraphQL mutation definitions

