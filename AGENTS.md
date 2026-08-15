# CaForB — Agent Instructions

## Environment

- WSL (Windows Subsystem for Linux). Use `/mnt/c/` paths for Windows files; use `powershell.exe -Command "..."` or `cmd.exe /c "..."` to run Windows executables.
- Two virtualenv dirs exist: `.venv/` (has the Django deps) and `venv/` (empty). Both are **Windows** virtualenvs (Python 3.12; packages under `Scripts/`, not `bin/`). `source .venv/bin/activate` does NOT work under WSL — invoke the interpreter directly via `powershell.exe -Command ".venv\Scripts\python.exe ..."` (or run natively on Windows).
- No `requirements.txt` for the backend. `.venv` is currently missing `django-cors-headers` (imported by `backend/settings.py`); install it if `manage.py` fails to boot with `ModuleNotFoundError: No module named 'corsheaders'`.

## Quick reference

| What | Where |
|------|-------|
| Backend entry | `manage.py` (Django **6.0.6** project `backend/`, app `core/`) |
| Frontend entry | `frontend/` (Next.js **16.2.7** App Router, Turbopack) |
| Static analysis | `cd frontend && npm run build` (ESLint + TypeScript + Next.js build in one) |
| Deep spec | `SPEC.md` (models, schema, prompts, design tokens) |

## Commands

```bash
# Backend — Windows venv, so invoke via PowerShell from WSL (not `source .venv/bin/activate`)
powershell.exe -Command ".venv\Scripts\python.exe manage.py migrate"
powershell.exe -Command ".venv\Scripts\python.exe manage.py runserver 8000"   # GraphQL at http://localhost:8000/graphql/

# Frontend — dev server at :3000
cd frontend && npm run dev

# LLM daemon (required for mutations)
ollama serve                            # localhost:11434
ollama run gemma4                       # verify model is pulled
```

## Architecture

### Backend

- `core/services/llm_services.py` is the AI layer (note plural `llm_services`, not singular). It calls Ollama with model `gemma4` by default. `core/schema.py` imports from it. All LLM interaction flows through this module.
- `core/services/memory.py` handles assessment history and score trends — imported by `schema.py` for re-assessment context injection.
- CSRF middleware is **intentionally disabled** (`backend/settings.py:50`, commented out with a spurious leading `'` in the string). The GraphQL view is wrapped with `csrf_exempt` in `backend/urls.py:26`. Don't re-enable CSRF without updating both places.
- Database is **SQLite** in dev (`db.sqlite3`); PostgreSQL is a production target only.
- CORS is locked to `http://localhost:3000` via `django-cors-headers`; credentials are allowed.
- **Authentication required** for most GraphQL operations. The schema layer uses `_guard()` to check `request.user.is_authenticated`. Users must login/register via `login`/`register` mutations. Companies and insights are scoped to the authenticated user via `Company.user` FK.
- **Re-assessment flow**: `submit_reassessment` mutation carries forward legacy opportunities (via `previous_insight_id`) and injects prior assessment context into the LLM prompt via `build_assessment_history()`. Score deltas (`score_delta`) are computed server-side.
- GraphQL endpoint mounts at `/graphql/`. The root `/` redirects to it.

### Frontend

- Next.js **16.2.7** with Turbopack. This version may differ from training data. Before writing Next.js code, check guides in `node_modules/next/dist/docs/` (see `frontend/AGENTS.md`).
- Import alias `@/*` → `frontend/*` (set in `tsconfig.json` paths).
- **Tailwind CSS v4** with a Warm Terracotta & Sage green theme defined as CSS custom properties in `app/globals.css`. The palette uses deep charcoal background (`oklch(0.16 0.01 60)`), terracotta primary (`oklch(0.52 0.12 40)`), and sage accent (`oklch(0.48 0.07 160)`). Design uses glassmorphism (`backdrop-blur-xl`, semi-transparent borders). Don't replace with generic Tailwind defaults.
- shadcn/ui components in `frontend/components/ui/` (`button.tsx`, `slider.tsx`). Use these primitives.
- Apollo Client in `frontend/lib/apollo-client.ts` → `http://localhost:8000/graphql/` with `credentials: "include"` (cookie-based sessions). Custom error link dispatches `auth:session-expired` on "Authentication required" errors.
- AuthProvider in `frontend/lib/auth-context.tsx` wraps the app via `frontend/app/providers.tsx`.
- GraphQL definitions in `frontend/lib/graphql/` (`auth.ts`, `mutations.ts`, `queries.ts`).
- App routes: `/`, `/assessment`, `/results/[id]`, `/login`, `/register`, `/company/[id]`, `/dashboard`.

## LLM integration

- Ollama must be running on `:11434` with `gemma4` pulled, or mutations will fail.
- Prompt returns structured JSON. Parsing is resilient (`_extract_json` in `llm_services.py`) with regex fallbacks for malformed output.
- Budget is estimated server-side from `revenueRange` + `budgetPercentage` before prompt construction.
- Re-assessments inject prior insight context and legacy opportunities into the prompt.

## Testing / verification

- Frontend: `cd frontend && npm run build` (ESLint + TypeScript + Next.js build in one; no separate lint/typecheck scripts).
- Backend: 29 Django tests in `core/tests.py` (django.test.TestCase, LLM calls mocked). Run with `powershell.exe -Command ".venv\Scripts\python.exe manage.py test core"` — no Ollama required. Note: 3 tests are stale (pre-existing failures); the suite is not fully green.
- For end-to-end backend changes, run the server and hit GraphQL at `http://localhost:8000/graphql/`.
