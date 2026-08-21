# CaForB — Agent Instructions

## Environment

- WSL (Windows Subsystem for Linux). Use `/mnt/c/` paths for Windows files; use `powershell.exe -Command "..."` or `cmd.exe /c "..."` to run Windows executables.
- Two virtualenv dirs exist: `.venv/` (has the Django deps) and `venv/` (empty). Both are **Windows** virtualenvs (Python 3.12; packages under `Scripts/`, not `bin/`). `source .venv/bin/activate` does NOT work under WSL — invoke the interpreter directly via `powershell.exe -Command ".venv\Scripts\python.exe ..."` (or run natively on Windows).
- No `requirements.txt` for the backend; `.venv` holds all deps (Django 6.0.6, `strawberry-graphql`, `ollama`, `django-cors-headers`). `venv/` has no packages installed — use `.venv`.

## Quick reference

| What | Where |
|------|-------|
| Backend entry | `manage.py` (Django **6.0.6** project `backend/`, app `core/`) |
| Frontend entry | `frontend/` (Next.js **16.2.7** App Router, Turbopack) |
| Static analysis | `cd frontend && npm run build` (ESLint + TypeScript + Next.js build in one) |
| Deep spec | `SPEC.md` (models, schema, prompts, design tokens) — but see staleness note below |

## Commands

```bash
# Backend — Windows venv, so invoke via PowerShell from WSL (not `source .venv/bin/activate`)
powershell.exe -Command ".venv\Scripts\python.exe manage.py migrate"
powershell.exe -Command ".venv\Scripts\python.exe manage.py runserver 8000"   # GraphQL at http://localhost:8000/graphql/

# Frontend — dev server at :3000
cd frontend && npm run dev

# LLM daemon (required for mutations)
ollama serve                            # localhost:11434
ollama run gemma4:12B                   # verify model is pulled (note the :12B tag)
```

## Architecture

### Backend

- `core/services/llm_services.py` is the AI layer (note plural `llm_services`, not singular). It calls Ollama with model `gemma4:12B` by default (`DEFAULT_MODEL` at top of file; `core/schema.py` also falls back to `"gemma4:12B"`). `core/schema.py` imports from it. All LLM interaction flows through this module.
- `core/services/memory.py` handles assessment history and score trends — imported by `schema.py` for re-assessment context injection.
- CSRF middleware is **intentionally disabled** (`backend/settings.py:50`, commented out with a spurious leading `'` in the string). The GraphQL view is wrapped with `csrf_exempt` in `backend/urls.py:26`. Don't re-enable CSRF without updating both places.
- Database is **SQLite** in dev (`db.sqlite3`); PostgreSQL is a production target only.
- CORS is locked to `http://localhost:3000` via `django-cors-headers`; credentials are allowed.
- **Authentication required** for most GraphQL operations. The schema layer uses `_guard()` to check `request.user.is_authenticated`. Users auth via `login`/`register`/`logout` mutations. Companies and insights are scoped to the authenticated user via `Company.user` FK.
- **Re-assessment flow**: `submit_reassessment` mutation carries forward legacy opportunities (via `previous_insight_id`) and injects prior assessment context into the LLM prompt via `build_assessment_history()`. Score deltas (`score_delta`) are computed server-side.
- **Chatbot over results**: `ask_insight` mutation + `chat_session` query answer follow-up questions about a completed `InnovationInsight`, grounded in its `context_bundle` (injected into the system prompt — no vector DB). `ChatSession`/`ChatMessage` models persist conversations; users can "tag" an opportunity/next step via `taggedOpportunityId`/`taggedNextStepId`. Lives in `llm_services.chat_with_insight`/`build_chat_system_prompt`.
- GraphQL endpoint mounts at `/graphql/`. The root `/` redirects to it.

### Frontend

- Next.js **16.2.7** with Turbopack. This version may differ from training data. Before writing Next.js code, check guides in `node_modules/next/dist/docs/` (see `frontend/AGENTS.md`).
- Import alias `@/*` → `frontend/*` (set in `tsconfig.json` paths).
- **Tailwind CSS v4** with a Warm Terracotta & Sage green theme defined as CSS custom properties in `app/globals.css`. The palette uses deep charcoal background (`oklch(0.16 0.01 60)`), terracotta primary (`oklch(0.52 0.12 40)`), and sage accent (`oklch(0.48 0.07 160)`). Design uses glassmorphism (`backdrop-blur-xl`, semi-transparent borders). Don't replace with generic Tailwind defaults.
- shadcn/ui components in `frontend/components/ui/` (`button.tsx`, `slider.tsx`). Use these primitives.
- Apollo Client in `frontend/lib/apollo-client.ts` → `http://localhost:8000/graphql/` with `credentials: "include"` (cookie-based sessions). Custom error link dispatches `auth:session-expired` on "Authentication required" errors.
- AuthProvider in `frontend/lib/auth-context.tsx` wraps the app via `frontend/app/providers.tsx`.
- GraphQL definitions in `frontend/lib/graphql/` (`auth.ts`, `mutations.ts`, `queries.ts`, `errors.ts`).
- Route protection lives in `frontend/proxy.ts` (Next 16 renamed `middleware` → `proxy`). It checks the `sessionid` cookie: redirects to `/login` when missing on `/assessment`, `/results`, `/dashboard`, `/company`, and redirects authenticated users away from `/login`/`/register`.
- App routes: `/`, `/assessment`, `/results/[id]`, `/login`, `/register`, `/company/[id]`, `/dashboard`.

## LLM integration

- Ollama must be running on `:11434` with `gemma4:12B` pulled, or mutations will fail.
- The results chatbot uses a **second, smaller model** — `CHAT_MODEL = "qwen2.5:7b-instruct"` in `llm_services.py` (see `chat_with_insight`). Pull it too (`ollama pull qwen2.5:7b-instruct`) or chat calls fail. On an 8 GB GPU, Ollama auto-unloads the idle model so only one runs at a time.
- Prompt returns structured JSON. Parsing is resilient (`_extract_json` in `llm_services.py`) with regex fallbacks for malformed output.
- Budget is estimated server-side from `revenueRange` + `budgetPercentage` before prompt construction.
- Re-assessments inject prior insight context and legacy opportunities into the prompt.

## Testing / verification

- Frontend: `cd frontend && npm run build` (ESLint + TypeScript + Next.js build in one; no separate lint/typecheck scripts).
- Backend: 42 Django tests in `core/tests.py` (django.test.TestCase, LLM calls mocked). Run with `powershell.exe -Command ".venv\Scripts\python.exe manage.py test core"` — no Ollama required, suite is green (42/42).
- For end-to-end backend changes, run the server and hit GraphQL at `http://localhost:8000/graphql/`.

## Repository notes

- `README.md` and parts of `SPEC.md` are stale — trust this file and the source over them. `README.md` still references `core/services/llm_service.py` (singular; actual is `llm_services.py`) and a pre-auth, pre-reassessment API. `SPEC.md` §9 describes an "Obsidian Violet" palette that does **not** match `app/globals.css` (actual: Warm Terracotta & Sage).
- `datasets_treino_finetune/` is a standalone fine-tuning data pipeline (templates → raw → reviewed → augmented → final JSONL, plus `cloud_train.sh`/`caforb-lora/`) for training a Gemma variant to replace the prompt-engineered `gemma4:12B` call. It is independent of the app runtime; `scripts/auto_fix.py` (repo root) is unrelated tooling.
