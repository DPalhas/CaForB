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
| Frontend tests | `cd frontend && npm test` (Vitest, unit/snapshot) |
| Deep spec | `SPEC.md` (models, schema, prompts, design tokens) — but see staleness note below |

## Commands

```bash
# Backend — Windows venv, so invoke via PowerShell from WSL (not `source .venv/bin/activate`)
powershell.exe -Command ".venv\Scripts\python.exe manage.py migrate"
powershell.exe -Command ".venv\Scripts\python.exe manage.py runserver 8000"   # GraphQL at http://localhost:8000/graphql/

# Frontend — dev server at :3000
cd frontend && npm run dev
cd frontend && npm test              # Vitest (unit/snapshot tests)

# LLM daemon (required for mutations)
ollama serve                            # localhost:11434
ollama run gemma4:12B                   # verify model is pulled (note the :12B tag)
```

## Architecture

### Backend

- `core/services/llm_services.py` is the AI layer (note plural `llm_services`, not singular). `core/schema.py` imports from it; all LLM interaction flows through this module.
- **Multi-model generation (A/B)**: every assessment generates one `InnovationInsight` **per model** in `ACTIVE_MODELS` (env `CAFORB_MODELS`, default `"gemma4:12B,caforb-v1"`). `DEFAULT_SELECTED_MODEL` (env `CAFORB_DEFAULT_MODEL`, default `"caforb-v1"`) is marked `is_selected=True`; `DEFAULT_MODEL = "gemma4:12B"` is only the fallback passed to `generate_innovation_insight`. The `select_insight` mutation re-marks `is_selected`, and `getInsight` exposes peer outputs via a `variants` field.
- `core/services/memory.py` handles assessment history and score trends — imported by `schema.py` for re-assessment context injection.
- CSRF middleware is **intentionally disabled** (`backend/settings.py:50`, commented out with a spurious leading `'` in the string). The GraphQL view is wrapped with `csrf_exempt` in `backend/urls.py:26`. Don't re-enable CSRF without updating both places.
- Database is **SQLite** in dev (`db.sqlite3`); PostgreSQL is a production target only.
- CORS is locked to `http://localhost:3000` via `django-cors-headers`; credentials are allowed.
- **Authentication required** for most GraphQL operations. The schema layer uses `_guard()` to check `request.user.is_authenticated`. Users auth via `login`/`register`/`logout` mutations. Companies and insights are scoped to the authenticated user via `Company.user` FK.
- **Re-assessment flow**: `submit_reassessment` mutation carries forward legacy opportunities (via `previous_insight_id`) and injects prior assessment context into the LLM prompt via `build_assessment_history()`. Score deltas (`score_delta`) are computed server-side.
- **Chatbot over results**: `ask_insight` mutation + `chat_session` query answer follow-up questions about a completed `InnovationInsight`, grounded in its `context_bundle` (injected into the system prompt — no vector DB). `ChatSession`/`ChatMessage` models persist conversations; users can "tag" an opportunity/next step/weakness via `taggedOpportunityId`/`taggedNextStepId`/`taggedWeakness`. Lives in `llm_services.chat_with_insight`/`build_chat_system_prompt`.
- GraphQL endpoint mounts at `/graphql/`. The root `/` redirects to it.

### Frontend

- Next.js **16.2.7** with Turbopack. This version may differ from training data. Before writing Next.js code, check guides in `node_modules/next/dist/docs/` (see `frontend/AGENTS.md`).
- Import alias `@/*` → `frontend/*` (set in `tsconfig.json` paths).
- **Frontend conventions live in `frontend/CONVENTIONS.md` and `frontend/DESIGN-CONVENTIONS.md` — read them before writing UI.** They are the source of truth for naming, folder layout, state rules, spacing/type/radius/shadow scales, and the component inventory.
- **Tailwind CSS v4**. `app/globals.css` has two token layers: the legacy terracotta/sage `:root` set (retained verbatim, used only by `PageBackground`/shadcn) and the current **stone/amber** semantic tokens (`--ui-stone-*`, `--ui-amber-*`, `--ui-glow-rgb`) that drive the real UI. Headings/body/chat-markdown and `lib/score.ts` tiers use `stone`/`amber`/`emerald`/`rose`/`yellow`. Don't swap in new hues or "generic" Tailwind colors; fix contrast within existing colors only.
- Shared domain/GraphQL types go in `lib/types.ts` — never re-declare a local interface. `lib/score.ts` has two distinct scales: `scoreTier()` (3-tier) and `scoreBand()` (4-tier, ScoreCard only) — do not merge them.
- shadcn/ui **v4** components in `frontend/components/ui/` (Base UI under the hood, not radix-ui). Use these primitives: `button`, `card`, `badge`, `slider`, `loading`, `error-state`, `empty-state`.
- Apollo Client in `frontend/lib/apollo-client.ts` → `http://localhost:8000/graphql/` with `credentials: "include"` (cookie-based sessions). Custom error link dispatches `auth:session-expired` on "Authentication required" errors.
- AuthProvider in `frontend/lib/auth-context.tsx` wraps the app via `frontend/app/providers.tsx`.
- GraphQL definitions in `frontend/lib/graphql/` (`auth.ts`, `mutations.ts`, `queries.ts`, `chat.ts`, `errors.ts`).
- Route protection lives in `frontend/proxy.ts` (Next 16 renamed `middleware` → `proxy`). It checks the `sessionid` cookie: redirects to `/login` when missing on `/assessment`, `/results`, `/dashboard`, `/company`, and redirects authenticated users away from `/login`/`/register`.
- App routes: `/`, `/assessment`, `/results/[id]`, `/login`, `/register`, `/company/[id]`, `/dashboard`.

## LLM integration

- Ollama must be running on `:11434` with **both** `gemma4:12B` and `caforb-v1` pulled, or mutations will fail — `ACTIVE_MODELS` defaults to generating from both. `caforb-v1` is the fine-tuned model; import it with `ollama create caforb-v1 -f datasets_treino_finetune/Modelfile` (from `caforb-v1.Q4_K_M.gguf`), not `ollama pull`.
- `_chat_with_retry` retries up to 3 attempts on empty / unparseable / missing-`maturity_score` / invalid-structure responses, appending a stricter JSON-only suffix each retry.
- The results chatbot uses a **second, smaller model** — `CHAT_MODEL = "qwen2.5:7b-instruct"` in `llm_services.py` (see `chat_with_insight`). Pull it too (`ollama pull qwen2.5:7b-instruct`) or chat calls fail. On an 8 GB GPU, Ollama auto-unloads the idle model so only one runs at a time.
- Prompt returns structured JSON. Parsing is resilient (`_extract_json` in `llm_services.py`) with regex fallbacks for malformed output.
- Budget is estimated server-side from `revenueRange` + `budgetPercentage` before prompt construction.
- Re-assessments inject prior insight context and legacy opportunities into the prompt.

## Testing / verification

- Frontend: `cd frontend && npm run build` (ESLint + TypeScript + Next.js build in one). `npm run lint` (eslint) exists as a standalone script, but `build` is the authoritative gate. `npm test` (Vitest) runs unit/snapshot tests under `lib/`.
- Backend: Django tests in `core/tests.py` (django.test.TestCase, LLM calls mocked). Run with `powershell.exe -Command ".venv\Scripts\python.exe manage.py test core"` — no Ollama required.
- For end-to-end backend changes, run the server and hit GraphQL at `http://localhost:8000/graphql/`.

## Repository notes

- `README.md` and parts of `SPEC.md` are stale — trust this file, `frontend/CONVENTIONS.md`/`frontend/DESIGN-CONVENTIONS.md`, and the source over them. `README.md` still references `core/services/llm_service.py` (singular; actual is `llm_services.py`) and a pre-auth, pre-reassessment API. `SPEC.md` §9 describes an "Obsidian Violet" palette that does **not** match `app/globals.css` (actual: stone/amber, with a retained terracotta/sage legacy layer).
- `datasets_treino_finetune/` is a standalone fine-tuning data pipeline (templates → raw → reviewed → augmented → final JSONL, plus `cloud_train.sh`/`caforb-lora/`) that produced the `caforb-v1` model — now wired into the app as the default selected output via `CAFORB_DEFAULT_MODEL`. It is independent of the app runtime; `scripts/auto_fix.py` (repo root) is unrelated tooling.
