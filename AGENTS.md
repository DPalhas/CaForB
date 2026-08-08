# CaForB — Agent Instructions

## Environment Setup

- You are running inside a WSL (Windows Subsystem for Linux) instance.
- To interact with or modify files on the Windows host machine, always use the mounted paths starting with /mnt/c/.
- To execute commands on the Windows host, you must invoke Windows executables directly. Use powershell.exe -Command "..." or cmd.exe /c "..." instead of standard Linux shell commands.

## Quick reference

| What | Where |
|------|-------|
| Backend entry | `manage.py` (Django project: `backend/`, app: `core/`) |
| Frontend entry | `frontend/` (Next.js 16 App Router) |
| Static analysis | `cd frontend && npm run build` (lint + typecheck in one command) |
| Deep spec | `SPEC.md` (models, schema, prompts, design tokens) |

## Commands

```bash
# Backend — activate venv, migrate, run
source .venv/bin/activate
python manage.py migrate
python manage.py runserver 8000        # GraphQL at http://localhost:8000/graphql/

# Frontend — dev server at :3000
cd frontend && npm run dev

# LLM — required daemon for backend mutations
ollama serve                            # localhost:11434
ollama run gemma4                       # verify model is pulled

# Full verify (frontend only)
cd frontend && npm run build            # lint → typecheck → build
```

## Architecture notes

- `core/services/llm_services.py` is the AI layer (named `llm_services.py`, not `llm_service.py` as README says). It calls Ollama with `gemma4`. The GraphQL schema (`core/schema.py`) imports from it. All LLM interaction flows through this module.
- CSRF middleware is **intentionally disabled** (`backend/settings.py:50`). The GraphQL view is wrapped with `csrf_exempt` in `backend/urls.py:26`. Don't re-enable CSRF without updating both places.
- Database is **SQLite** in dev (`db.sqlite3`); PostgreSQL is a production target only.
- CORS is locked to `http://localhost:3000` via `django-cors-headers`.

## Frontend conventions

- Next.js **16.2.7** with Turbopack. This version may differ from training data. Before writing Next.js code, check guides in `node_modules/next/dist/docs/` (see `frontend/AGENTS.md`).
- Import alias `@/*` → `frontend/*` (set in `tsconfig.json` paths).
- **Tailwind CSS v4** with an Obsidian Violet theme defined as CSS custom properties in `app/globals.css`. The design uses glassmorphism (`backdrop-blur-xl`, semi-transparent borders) on a deep obsidian background. Don't replace with generic Tailwind defaults.
- shadcn/ui components live in `frontend/components/ui/`. Use these primitives over raw HTML.
- Apollo Client is configured in `frontend/lib/apollo-client.ts` pointing to `http://localhost:8000/graphql/`.
- GraphQL query/mutation definitions are in `frontend/lib/graphql/`.

## LLM integration

- Ollama must be running locally on `:11434` with model `gemma4` pulled, or the `submitQuestionnaire` mutation will fail.
- The prompt returns structured JSON. Parsing is resilient (`_extract_json` in `llm_services.py`) with multiple fallback strategies for malformed output.
- Budget is estimated server-side from `revenueRange` + `budgetPercentage` before prompt construction.

## Testing / verification

- There is no dedicated test runner configured. The canonical verification step is `npm run build` in `frontend/`, which runs ESLint + TypeScript checking + Next.js build.
- For backend changes, verify by running the server and hitting the GraphQL endpoint.