# Continuous Innovation Assessment — Full Implementation Process

> **Author:** David Palhas | ISCTE-IUL, 2026
> **Goal:** Transform CaForB from a one-shot questionnaire app into a continuous,
> iterative innovation assessment platform with memory, agent loop, and a
> fine-tuned model trained on the extended (reassessment) contract.
> **Last updated:** August 2026

---

## Table of Contents

1. [Design: The Extended Input/Output Contract](#1-design-the-extended-inputoutput-contract)
2. [Stream A — Application Changes](#2-stream-a--application-changes)
3. [Stream B — Dataset Pipeline Changes](#3-stream-b--dataset-pipeline-changes)
4. [Step C — Train the Model](#4-step-c--train-the-model)
5. [Step D — Verify & Evaluate](#5-step-d--verify--evaluate)
6. [Implementation Order](#6-implementation-order)
7. [What Stays the Same](#7-what-stays-the-same)
8. [Risks & Mitigations](#8-risks--mitigations)

---

## 1. Design: The Extended Input/Output Contract

The model must handle **two task types** gracefully. They differ only in whether a
prior-assessment summary is present in the input.

### 1.1 First Assessment (unchanged from current format)

**Input** — standard text prompt built from the 17-field survey answers.

**Output:**
```json
{
  "maturity_score": 5.5,
  "opportunities": [
    {
      "id": "opp_1",
      "type": "incremental",
      "title": "string",
      "rationale": "string",
      "execution_plan": {
        "first_actions": ["..."],
        "resources_needed": ["..."],
        "success_metric": "...",
        "milestones": ["..."]
      },
      "impact": "medium",
      "difficulty": "low",
      "timeframe": "3-6 months"
    }
  ],
  "next_steps": [
    {"action": "...", "owner": "...", "timeframe": "..."}
  ],
  "key_weaknesses": ["..."]
}
```

### 1.2 Reassessment (new — built from prior assessments)

**Input** — extended prompt that prepends a "Prior Assessment Summary" block
before the standard questionnaire fields:

```
---
PRIOR ASSESSMENT SUMMARY (Assessment #1, dated 2026-03-15)
Previous Maturity Score: 5.5

Previously Identified Opportunities:
1. [incremental] "Implement CRM system" (Impact: medium, Difficulty: low,
   Timeframe: 3-6 months)
   Status: COMPLETED — reduced response time by 40%

2. [incremental] "Launch customer feedback program" (Impact: medium,
   Difficulty: low, Timeframe: 1-3 months)
   Status: IN PROGRESS — pilot running with 3 clients

3. [radical] "Explore AI-powered product line" (Impact: high, Difficulty: high,
   Timeframe: 12-18 months)
   Status: NOT STARTED — pending board approval

Previous Next Steps:
1. "Assign CRM implementation lead" → Owner: CTO, COMPLETED
2. "Design feedback survey template" → Owner: Product lead, COMPLETED
3. "Draft AI product budget proposal" → Owner: CEO, PARTIAL

Previous Key Weaknesses: ["No formal innovation process",
  "Fragmented customer data"]

BUDGET HISTORY:
- Assessment #1: ~€55,000/year (1% of €5.5M–€11M revenue)
---
CHANGES SINCE LAST ASSESSMENT:
Acquired 2 new enterprise clients. Doubled development team.
Launched customer feedback pilot with mixed results.
Still exploring AI tooling but no concrete plan.
Budget for innovation slightly increased.

PROGRESS ON PREVIOUS RECOMMENDATIONS:
- Implement CRM system: DONE
- Launch customer feedback program: IN PROGRESS
- Explore AI-powered product line: NOT STARTED

CURRENT ASSESSMENT (Assessment #2):
Company: Acme Corp | Sector: Technology & IT | Size: Medium
Company description: B2B SaaS company with 45 employees...
[all standard questionnaire fields follow]
```

**Output** — extended JSON with delta, carry-forward, progress:

```json
{
  "maturity_score": 6.0,
  "score_delta": 0.5,
  "score_change": "improved",
  "opportunities": [
    {
      "id": "opp_2_1",
      "type": "incremental",
      "title": "Scale CRM automation with API integration",
      "rationale": "Builds on the completed CRM implementation...",
      "execution_plan": { ... },
      "impact": "medium",
      "difficulty": "low",
      "timeframe": "2-4 months",
      "carry_forward_from": "opp_1",
      "carry_forward_status": "evolved_to"
    },
    {
      "id": "opp_2_2",
      "type": "incremental",
      "title": "Expand feedback program to enterprise tier",
      "rationale": "...",
      "execution_plan": { ... },
      "impact": "medium",
      "difficulty": "medium",
      "timeframe": "3-5 months",
      "carry_forward_from": "opp_2",
      "carry_forward_status": "continues"
    },
    {
      "id": "opp_2_3",
      "type": "radical",
      "title": "Build AI-powered analytics engine",
      "rationale": "Leveraging the larger dev team and new budget...",
      "execution_plan": { ... },
      "impact": "high",
      "difficulty": "high",
      "timeframe": "12-18 months",
      "carry_forward_from": null,
      "carry_forward_status": "new"
    }
  ],
  "next_steps": [
    {"action": "...", "owner": "...", "timeframe": "..."}
  ],
  "key_weaknesses": [
    "Formal process still not adopted company-wide",
    "Customer data integration remains fragmented across tools"
  ],
  "progress": {
    "improvements": [
      "CRM implementation completed, response time improved 40%",
      "Development team doubled, enabling faster execution",
      "Customer feedback pilot yielding initial insights"
    ],
    "persistent_gaps": [
      "Innovation process still informal — no dedicated framework adopted",
      "Customer data remains fragmented across CRM, support and analytics tools"
    ],
    "achieved_milestones": [
      "CRM system operational (Week 8 of previous roadmap)",
      "Feedback survey deployed to 3 pilot clients (Week 4 of previous roadmap)"
    ]
  },
  "comparison_to_previous": {
    "previous_score": 5.5,
    "previous_date": "2026-03-15",
    "assessment_number": 1,
    "key_changes": "Score improved from 5.5 to 6.0 driven by completed CRM implementation, team growth, and initial customer feedback process. Held back by persistent lack of formal innovation framework and data fragmentation."
  }
}
```

### 1.3 Fields Reference

| Field | First Assessment | Reassessment |
|---|---|---|
| `maturity_score` | required | required |
| `opportunities[].id` | required | required |
| `opportunities[].carry_forward_from` | absent | required (null for new opps) |
| `opportunities[].carry_forward_status` | absent | required (continues/evolved_to/retired/new) |
| `score_delta` | absent | required |
| `score_change` | absent | required (improved/stable/declined) |
| `progress` | absent | required |
| `comparison_to_previous` | absent | required |

---

## 2. Stream A — Application Changes

All changes to the CaForB Django/Next.js application to support continuous assessment.

### A.1 — Persistent Company Identity

**File: `core/models.py`**

Add fields to `QuestionnaireResponse`:
- `assessment_number` — `IntegerField(default=1)`. Auto-incremented per company in the mutation.
- `period_label` — `CharField(max_length=100, blank=True, default="")`. Optional user-provided label ("Q1 2026").
- `changes_since_last` — `TextField(blank=True, default="")`. Free-text description of what changed.
- `recommendation_status` — `JSONField(default=dict)`. Maps previous `opportunities[].id` and `next_steps[].action` to status {"done", "partial", "not_done", "superseded"}.

Add fields to `InnovationInsight`:
- `previous_insight` — `ForeignKey("self", null=True, blank=True, on_delete=SET_NULL, related_name="subsequent_insights")`. Chains assessments.
- `model_name` — `CharField(max_length=100, blank=True, default="")`. Records which model generated this insight (for A/B comparison in evaluation).

Add field to `LLMTrace`:
- `model_name` — `CharField(max_length=100, blank=True, default="")`.

**File: `core/schema.py`** — GraphQL changes:
- `submitQuestionnaire` gains `companyId: Int` (optional) and `periodLabel: String` (optional).
  - If `companyId` provided and owned by user → reuse Company, increment `assessment_number`.
  - Else → create new Company (assessment_number=1).
- New query `myCompanies` → `[CompanySummaryType]` (id, name, sector, size, latestScore, assessmentCount, createdAt).
- New query `company(id: Int!)` → `CompanyDetailType` (all of above + `assessments: [AssessmentTimelineType]`).
- New mutation `submitReassessment` — accepts `companyId`, `previousInsightId`, `recommendationStatus`, `changesSinceLast`, plus all standard fields. Builds memory block, calls LLM with history.
- New types: `CompanySummaryType`, `CompanyDetailType`, `AssessmentTimelineType`, `ProgressReportType`.

**Migration:**
`core/migrations/0004_continuous_assessment.py` — auto-generated via `makemigrations` + data migration setting `assessment_number=1` for all existing QuestionnaireResponses.

### A.2 — Memory Service

**New file: `core/services/memory.py`**

Two export functions:

```python
def build_assessment_history(company, current_response=None) -> str
```
Compresses all prior QuestionnaireResponses + InnovationInsights for a company into a compact text block (the "PRIOR ASSESSMENT SUMMARY" shown in §1.2). Includes:
- Previous maturity scores (chronological)
- Opportunities with their carry-forward status (from previous assessment's recommendation_status)
- Next steps with completion status
- Previous key weaknesses
- Budget history
- Cap limit: max 5 prior assessments (oldest dropped if > 5)

```python
def build_score_trend(company) -> dict
```
Returns `{"scores": [...], "trend": "improving|declining|stable", "first_score": X, "latest_score": Y, "delta": Z}`. Used by the agent and the frontend.

### A.3 — Extended Prompt Builder

**File: `core/services/llm_services.py`**

`build_innovation_prompt` signature changes from:
```python
def build_innovation_prompt(company: dict, answers: dict) -> str
```
to:
```python
def build_innovation_prompt(company: dict, answers: dict, history: str = None) -> str
```

When `history` is present, the prompt template prepends it before the company/survey block and adds a **REASSESSMENT DIRECTIVES** section:

```
You are conducting a REASSESSMENT for a company you have previously evaluated.
Above is a summary of the prior assessment(s). Your task:

1. Compare the current state against prior scores and opportunities.
2. Determine which prior opportunities continue, have evolved, or should be retired.
3. Identify new opportunities based on changes since last assessment.
4. Assess overall progress (improvements, persistent gaps, achieved milestones).
5. Produce a "comparison_to_previous" block explaining the key changes.

[then the existing constraint rules: budget, regulatory, risk, competition, strategic priority]
[then the extended JSON output format with carry_forward, score_delta, progress, comparison]
```

When `history` is absent, use the original single-shot prompt (unchanged for backward compatibility).

### A.4 — Agent Loop

**File: `core/services/llm_services.py`** (refactor `generate_innovation_insight`)

Replace the single `ollama.chat` call with a Python-orchestrated ReAct-lite loop:

```
generate_innovation_insight(company, answers, history=None, model="gemma4") -> (str, int)
```

**Tool functions** (callable by the orchestrator, not by the LLM):
- `tool_fetch_history(company) → str` — calls `build_assessment_history`
- `tool_fetch_trend(company) → dict` — calls `build_score_trend`
- `tool_compute_budget(answers) → str` — calls `_estimate_budget`

**Loop steps** (each recorded as an `LLMTrace` row if `insight` is provided):
1. `fetch_history` — retrieve prior assessment memory (if company has history)
2. `fetch_trend` — compute score trend
3. `build_context` — assemble the full prompt (history + answers)
4. `synthesize` — single `ollama.chat` call with the assembled context

**The model is always a single-step synthesizer** — matching supervised fine-tuning.
The agent loop is the orchestrator that gathers context before the final call.

**Signature stability:** `generate_innovation_insight` keeps its current signature
so `schema.py` callers are unchanged.

**Trace model:** each step writes an `LLMTrace` row (requires passing the `insight`
instance to the function, or returning trace data to be persisted afterward).

### A.5 — Frontend Changes

**Company picker** (`frontend/app/assessment/`):
- Step 0 (before the 5-step survey): "Select a company" dropdown or "Create new"
- If existing company selected → show last assessment date and maturity score
- GraphQL query: `myCompanies`

**Re-assessment flow** (same page, conditional):
- If re-assessing: between company pick and Step 1, insert "Since Your Last Assessment"
  - Checklist of previous opportunities/next-steps from latest assessment
  - User marks each as Done / In Progress / Not Started
  - Free-text "What changed since your last assessment?"
  - GraphQL query: `company(id)` to get assessment timeline

**New route `frontend/app/company/[id]/page.tsx`**:
- Company detail page with:
  - Score evolution line chart (maturity_score over assessment_number)
  - Timeline of assessments, each expandable
  - Opportunity tracker — which ones carried forward, which retired, which new
  - "Run Re-assessment" button

**Dashboard** (`frontend/app/dashboard/page.tsx`):
- Group assessments by company (fetch `myCompanies` instead of `myInsights`)
- Show per-company: name, sector, latest score + trend arrow (↑ improving / ↓ declining / → stable), assessment count
- Click → navigate to `/company/[id]`

**Results page** (`frontend/app/results/[id]/page.tsx`):
- If previous_insight exists → show "vs. Previous Assessment" delta section:
  - Score change (±0.5) with color
  - New vs. continued vs. retired opportunities
  - Progress block (improvements, persistent gaps)

**Analysis overlay fix:**
- Current fake 4.5s progress → replace with real step status from `LLMTrace` rows
  (poll `getInsight` and read traces, or return step statuses from the mutation).
  Phase 1: increase timeout in Apollo client; Phase 2: move to polling.

### A.6 — Evaluation Infrastructure

**File: `core/tests.py`**:
- `test_build_assessment_history_no_prior` — empty company produces empty block
- `test_build_assessment_history_with_prior` — company with 2 assessments produces correct summary
- `test_build_prompt_first_assessment` — no history → original prompt format
- `test_build_prompt_reassessment` — with history → extended prompt with directives
- `test_build_score_trend` — improving / declining / stable scenarios
- `test_agent_loop_tools` — mock Ollama, verify trace rows created
- `test_submit_questionnaire_new_company` — no companyId → creates new Company
- `test_submit_questionnaire_existing_company` — companyId provided → reuses, assessment_number=2

---

## 3. Stream B — Dataset Pipeline Changes

All changes to the `datasets_treino_finetune/` pipeline to generate training data
for the extended contract.

### B.1 — Generate Re-assessment Inputs

**File: `datasets_treino_finetune/scripts/generate_surveys.py`** (extend)

New function `generate_reassessment_pairs()` that reads `raw_inputs.json` and for
each base survey produces 1 reassessment variant (skip ~20% to avoid 1:1 pairing):

- **Same company identity** — name, sector, size kept
- **Modified answers** — with realistic evolution:
  - `innovationProcess`: higher maturity (e.g., informal → partial)
  - `digitalMaturity`: +1 in 60% of cases
  - `budgetPercentage`: ±5% (trending up more often)
  - `timeHorizon`: short→medium, medium→long in 40% of cases
  - `mainBarrier`: 1-2 barriers removed, 1 new added
  - `teamSize`: increased in 50% of cases
  - `competitivePressure`: may shift
- **New fields:**
  - `changes_since_last` — free-text generated from delta logic (e.g., "Hired 2 senior engineers, launched customer beta, competitor X entered our market")
  - `recommendation_status` — JSON mapping prior opp IDs to status values
  - `previous_assessment` — reference to the original survey ID

Output: `raw_inputs_reassessment.json` (~400 entries).

### B.2 — Generate Synthetic Outputs for Re-assessment

**File: `scripts/generate_one.py`** (extend)

- New system prompt variant: `SYSTEM_PROMPT_REASSESSMENT` that instructs the model
  to produce the extended contract (with carry_forward, score_delta, progress, comparison).
- `build_reassessment_prompt()` — formats the prior summary block + current survey into the model input.
- **Locked-field validation** extended to check:
  - `carry_forward_status` is a valid enum value
  - `score_delta` matches `maturity_score - comparison.previous_score` (±0.5 tolerance)
  - Each `carry_forward_from` reference exists in the previous assessment's opportunities
- **Retry logic** reused as-is (up to 5 retries with feedback on violations).

**File: `scripts/run_batch.py`** — run against `raw_inputs_reassessment.json`,
output to `raw/05??.json` (new index range).

### B.3 — Extended Validation & Auto-Fix

**File: `scripts/validate_schema.py`** (extend — new checks 8-12):

| # | Check | Level |
|---|---|---|
| 8 | `score_delta` present in reassessment; matches `maturity_score - comparison.previous_score` ± 0.5 | ERROR |
| 9 | `carry_forward_status` values valid (continues/evolved_to/retired/new) | ERROR |
| 10 | Non-new opportunities have a valid `carry_forward_from` reference | WARNING |
| 11 | `comparison_to_previous` contains `previous_score`, `previous_date`, `assessment_number` | ERROR |
| 12 | `progress` contains `improvements`, `persistent_gaps`, `achieved_milestones` (all arrays) | WARNING |

Existing checks 1-7 still run on all files (first-assessment and reassessment).

**File: `scripts/auto_fix.py`** (extend):

| Rule | Action |
|---|---|
| Score swing > 2.0 | Clamp delta to ±2.0, adjust maturity_score |
| carry_forward_status mismatch | Set to "continues" if conservative and type matches; "evolved_to" if same type but different title; "new" if unknown |
| Missing comparison fields | Populate from metadata if available |

### B.4 — Mix, Convert, Train

**File: `scripts/convert_to_jsonl.py`** (extend):
- Input: `raw/*.json` (all 504 + ~400 new = ~900 files)
- Mix first-assessment and reassessment in the 80/20 split
- Updated system prompt that acknowledges both task types
- Coverage report extended to track `assessment_type` distribution

**File: `scripts/train_caforb.py`** (1-line edit):
- `max_seq_length` from 2048 → **4096** (reassessment inputs are ~2× longer)
- Feature flag to test at 3072 first if VRAM is tight

---

## 4. Step C — Train the Model

1. Verify the extended dataset passes `validate_schema.py` (0 errors).
2. Run `python scripts/train_caforb.py`:
   - Model: `google/gemma-4-E2B-it`
   - LoRA: r=16, alpha=16, dropout=0.05
   - 3 epochs, lr=2e-4, fp16
   - VRAM budget: 8 GB (RTX 4070)
3. Output: `caforb-lora/` adapter weights.
4. Merge LoRA → full weights → convert to GGUF (quantized).
5. `ollama create caforb-v2 -f Modelfile`.
6. Verify: `ollama run caforb-v2` with a sample reassessment prompt.

---

## 5. Step D — Verify & Evaluate

### D.1 — Test the application end-to-end

1. Run Django server with caforb-v2 model configured.
2. Create a company, run first assessment (check: first-assessment output format).
3. Re-assess the same company with `changesSinceLast` and `recommendationStatus`.
4. Verify: reassessment output has carry_forward, score_delta, progress, comparison.
5. Check LLMTrace: agent loop wrote N trace rows with distinct step_names.
6. Frontend: `/company/[id]` shows score timeline and all assessments.

### D.2 — A/B comparison for dissertation evaluation

- Run the same company through both models (gemma4 + caforb-v2).
- Compare: coherence of carry_forward, realism of progress assessment, budget alignment.
- Record model_name in LLMTrace for traceability.

### D.3 — Update the dissertation manuscript

- Chapter 4 Architecture: update LLM from "Anthropic Claude" → Ollama gemma4/fine-tuned caforb-v2; add agent loop + memory service diagrams.
- Chapter 5 Implementation: document the extended contract, agent loop, and dataset pipeline.
- Chapter 6/7: present A/B evaluation results.

---

## 6. Implementation Order

```
  ┌─────────────────────────────────────────────────┐
  │           DEFINE THE EXTENDED CONTRACT           │  (this document, §1)
  └──────────────────────┬──────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
  ┌──────────────────┐          ┌───────────────────┐
  │  Stream A — App   │          │  Stream B — Dataset │
  │──────────────────│          │───────────────────│
  │ A1. models+       │          │ B1. gen reassessment│
  │     migration     │          │     surveys         │
  │ A2. memory.py     │          │ B2. gen synthetic   │
  │ A3. prompt builder│          │ B3. validate + fix  │
  │ A4. agent loop    │          │ B4. convert + train │
  │ A5. schema.py     │          │                     │
  │ A6. frontend      │          │                     │
  └────────┬─────────┘          └─────────┬───────────┘
           │                              │
           └──────────────┬───────────────┘
                          ▼
                 ┌──────────────────┐
                 │  C. Train model   │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │  D. Verify & Eval │
                 └──────────────────┘
```

Streams A and B are **independent** and can run in parallel. Both converge at training.

---

## 7. What Stays the Same

| Component | Status |
|---|---|
| All 504 existing raw examples in `datasets_treino_finetune/raw/` | **Unchanged** — valid for first-assessment training |
| `review_cli.py` | Reused as-is on extended data if manual review needed |
| `augment_with_fewshot.py` | Reused logic if few-shot augmentation desired for reassessment |
| `setup_ml.py`, `train_caforb.py` | Only `max_seq_length` changes |
| Frontend design system (Obsidian Violet theme, Tailwind v4, shadcn) | Untouched |
| Auth (login/register/session middleware) | Untouched |
| GraphQL endpoint URL, CORS, CSRF config | Untouched |
| `core/admin.py` | Updated to show new fields but no logic changes |
| `core/apps.py`, `backend/settings.py` | Untouched |

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| max_seq_length=4096 exceeds 8 GB VRAM on RTX 4070 | Training fails | Test at 3072 first; compress prior summary (truncate old assessments); lower batch/GA |
| `gemma4:e2b-it-qat` generates low-quality reassessment outputs | Poor training data | Use the same review_cli.py for spot-checking; increase retry limit in generate_one.py |
| Fine-tuned model overfits to carry_forward patterns | Degrades on novel first-assessment inputs | Train on mixed data (first + reassessment); validate both separately |
| Agent loop adds significant latency | Frontend timeout, poor UX | Keep analysis overlay with real step status; increase Apollo timeout; optional Celery migration |
| Existing QuestionnaireResponses have no `assessment_number` = 1 | Migration fails | Data migration handles this (default=1 for all existing rows) |
| Frontend changes conflict with existing 5-step wizard | Complex rework | Add Step 0 as a conditional overlay before Step 1; keep existing wizard components untouched |

---

*End of document.*
