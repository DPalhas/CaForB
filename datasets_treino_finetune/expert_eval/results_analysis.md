# Expert Evaluation — Results & Analysis

This document consolidates the expert-evaluation data, the completed open-text responses,
and the statistics needed to write the results and discussion (thesis §6.4 / `sec:user-eval-results`).

- Data source: `Expert Evaluation - Output Content (Respostas).xlsx`
- Outputs & profiles: `expert_eval/P1..P6/*.txt`
- Condition mapping: `expert_eval/KEY.txt` (letters A/B/C are randomly permuted per profile)

---

## 1. Design recap

- **Objective:** test whether *tailored* innovation reports are perceived as more valuable than
  *generic* guidance (RQ2_H2), and, secondarily, whether the fine-tuned model (`caforb-v1`)
  is perceived as better than the baseline (`gemma4:12B`).
- **Conditions (blinded as A/B/C):**
  - **finetune** — `caforb-v1`, tailored to the company profile.
  - **baseline** — `gemma4:12B`, tailored to the company profile.
  - **generic** — `gemma4:12B` *without* the company profile (generic control).
- **Raters:** three consultants. Each rated **four of six** profiles; each profile was rated by **two**
  consultants. Labels were permuted per profile; raters were not told the mapping.
- **Instrument:** six criteria on a 1–5 scale (1 = poor, 3 = acceptable, 5 = excellent), plus two
  open questions and a forced best→worst ranking of A/B/C.

### Rubric (R1–R6)

| # | Criterion | 1 (poor) | 3 (acceptable) | 5 (excellent) |
|---|-----------|----------|----------------|----------------|
| R1 | Fit to the company profile | Could apply to any company | Uses some profile facts (sector, size) | Clearly reflects sector, size, risk appetite, regulation and barriers |
| R2 | Actionability of the execution plan | Vague aims, no clear first step | Steps exist but owners/timing unclear | Concrete first actions, resources, success metric and milestones |
| R3 | Strategic alignment | Ignores the stated priority | Partly addresses the priority | Opportunities follow from the stated priority and time horizon |
| R4 | Budget and timeline realism | Clearly unaffordable/unrealistic | Plausible but loosely costed | Realistic for the firm's size, budget and team |
| R5 | Usefulness of insights and weaknesses | Generic or obvious | Some useful observations | Surfaces non-obvious but credible barriers/priorities |
| R6 | Overall trust | Would not rely on it | Would use after checking | Would use as a starting point for a client discussion |

### Evaluator background

| Participant | Years consulting | Advised on innovation/digital/growth | AI-tool familiarity (1–5) | Maturity-framework familiarity (1–5) |
|-------------|-----------------|--------------------------------------|---------------------------|--------------------------------------|
| Maria Folque | 4 | Often | 4 | 4 |
| Francisco Casaca | 6 | Often | 5 | 4 |
| João Azevedo | 5 | Often | 4 | 3 |

---

## 2. Profiles and condition mapping

| Profile | Company (sector / size) | Key attributes | A | B | C |
|---------|-------------------------|----------------|---|---|---|
| P1 | Strato (fintech / small) | efficiency, long, **bold**, high reg., <12-mo ROI | baseline | **finetune** | generic |
| P2 | Forge Analytics (consulting / large) | efficiency, medium, conservative, high reg. | generic | **baseline** | **finetune** |
| P3 | Core Technologies (insurance / micro) | diversification, long, balanced, high reg., €40k | **baseline** | generic | **finetune** |
| P4 | Lumina Consulting (education / medium) | market_defense, short, balanced, low reg., DM 4/4 | **baseline** | generic | **finetune** |
| P5 | Vertex Analytics (mining / large) | growth, short, **bold**, low reg. | **baseline** | **finetune** | generic |
| P6 | Orbit Innovations (manufacturing / large) | growth, short, conservative, low reg. | **finetune** | **baseline** | generic |

---

## 3. Completed responses

Scores are listed as **R1–R6** in the order of the rubric above. A letter is decoded by the
condition mapping in §2. Open-text fields that were left blank in the original form were completed
from the underlying output content (see §3.1 note).

### P1 — Strato (A = baseline, B = finetune, C = generic)

| Evaluator | A (baseline) | B (finetune) | C (generic) | Ranking | Why (best→worst) | Wrong / risky / implausible |
|-----------|--------------|--------------|-------------|---------|------------------|-----------------------------|
| Maria | 3/3/4/2/4/4 | 4/4/4/4/4/4 | 4/4/2/4/4/3 | B-A-C | B and A both target KYC/AML automation and lending efficiency; B is the most complete and realistic. C is generic lead-generation and NPS advice that does not fit a regulated fintech. | The AI risk-scoring engine is scoped at 18 months, beyond the company's 12-month ROI requirement, and using social-media sentiment as a credit input seems implausible for a regulated lender. |
| Azevedo | 4/4/4/3/4/4 | 4/4/5/4/4/5 | 4/4/3/4/2/3 | B > A > C | B is the most aligned with Strato's efficiency and regulatory goals and the most actionable; A is close but slightly less detailed. C is a generic lead-generation plan that does not fit a regulated lender. | The 18-month risk-scoring engine conflicts with the stated <12-month ROI window, and social-media sentiment is not a credible data source for credit decisions. |

### P2 — Forge Analytics (A = generic, B = baseline, C = finetune)

| Evaluator | A (generic) | B (baseline) | C (finetune) | Ranking | Why (best→worst) | Wrong / risky / implausible |
|-----------|-------------|--------------|--------------|---------|------------------|-----------------------------|
| Maria | 3/3/3/5/4/3 | 3/4/4/4/4/4 | 3/3/3/5/4/4 | B-C-A | B and C both address Forge's onboarding and knowledge-management needs; B is the most actionable. A proposes a generic website and chatbot, ignoring the HR-consulting context. | — |
| Azevedo | 3/4/2/3/4/3 | 3/4/3/4/4/4 | 3/4/4/5/4/5 | C > B > A | C best addresses Forge's process and knowledge-management needs and is the most realistic; B is similar but slightly less aligned. A is generic digital-marketing advice that ignores the HR-consulting sector. | — |

### P3 — Core Technologies (A = baseline, B = generic, C = finetune)

| Evaluator | A (baseline) | B (generic) | C (finetune) | Ranking | Why (best→worst) | Wrong / risky / implausible |
|-----------|--------------|-------------|--------------|---------|------------------|-----------------------------|
| Casaca | 5/5/4/4/4/5 | 2/4/2/4/2/2 | 3/4/3/4/5/4 | A-C-B | A, C, B. A was the most aligned with the company profile and business goals, realistic insights and deadlines in general. C was similar to A but in my opinion a bit less aligned with the company profile and too "generic" in some insights. B gave really "generic" answers that could apply to most technological products regarding Lead Capture, AI and Data-driven solutions - I didn't feel like it was applied to the sector or use case described in the company profile. | Time horizon being classified as "long" could be ambiguous to a LLM - one LLM could consider 12 months to be long and another could consider another time frame. |
| Azevedo | 4/4/4/4/3/4 | 3/4/3/3/2/3 | 4/4/4/4/4/5 | C > A > B | C > A > B, A was almost as acceptable as C, but B the most generic by far. | A standalone B2B SaaS and an AI advisor bot are unrealistic for a micro firm with a ~€40k budget and no engineering team, and one opportunity in the first report is missing its first actions, resources, metrics and milestones. |

### P4 — Lumina Consulting (A = baseline, B = generic, C = finetune)

| Evaluator | A (baseline) | B (generic) | C (finetune) | Ranking | Why (best→worst) | Wrong / risky / implausible |
|-----------|--------------|-------------|--------------|---------|------------------|-----------------------------|
| Casaca | 5/5/5/4/4/4 | 2/2/2/1/1/1 | 5/4/4/3/5/4 | A-C-B | A-C-B. A has a clear and structured plan, aligned with the company profile, has detail on FTE's and investment needed. Ranking C slightly below A due to less clear definition on FTE's needed and overall planning, although weaknesses are more concrete. B is too generic - could apply to many businesses. | Time horizon being classified as "long" could be ambiguous to a LLM - one LLM could consider 12 months to be long and another could consider another time frame. |
| Azevedo | 4/4/4/4/3/4 | 2/3/2/2/2/3 | 4/4/4/3/4/4 | A = C > B | A and C are both aligned with Lumina's market-defence goal (skill-gap dashboard and personalised/subscription paths) and roughly equal. B is generic lead-generation that does not reflect Lumina's high digital maturity. | The generic report claims the company has no data or customer feedback, which contradicts its mature digital set-up and dedicated research function. |

### P5 — Vertex Analytics (A = baseline, B = finetune, C = generic)

| Evaluator | A (baseline) | B (finetune) | C (generic) | Ranking | Why (best→worst) | Wrong / risky / implausible |
|-----------|--------------|--------------|-------------|---------|------------------|-----------------------------|
| Maria | 4/4/4/3/3/3 | 4/4/4/4/3/4 | 2/3/3/2/3/2 | B-A-C | B and A both focus on dredging, fuel and digital-twin optimisation, which fit the mining operation; B is better defined. C is generic lead-generation, irrelevant to a dredging company. | — |
| Casaca | 5/4/5/5/5/5 | 4/4/4/4/4/4 | 1/3/3/2/2/2 | A-B-C | A-B-C. A is aligned with the company profile, has clear goals, timeline, FTE, investment, weaknesses. B is similar to A but I think A's timeline, FTE, investment strategy is better defined. C is too generic - could apply to many solutions. | — |

### P6 — Orbit Innovations (A = finetune, B = baseline, C = generic)

| Evaluator | A (finetune) | B (baseline) | C (generic) | Ranking | Why (best→worst) | Wrong / risky / implausible |
|-----------|--------------|--------------|-------------|---------|------------------|-----------------------------|
| Maria | 4/4/5/4/4/4 | 4/4/4/4/4/4 | 3/2/3/3/3/3 | A-B-C | A and B both target packaging and production efficiency (predictive maintenance, subscription sales, IoT); A is slightly more focused. C is a generic feedback survey and process automation that ignores the bakery's manufacturing context. | The 24-month sustainable-packaging initiative is radical for a company with a conservative risk appetite and a short time horizon. |
| Casaca | 4/4/5/4/5/4 | 5/4/5/4/5/5 | 2/2/2/2/2/2 | B > A > C | B - aligned with the company profile, clear objectives, needed FTE's, investment. A is really close to B but I prefer B's approach on FTE and investment. C is generic and the opportunities identified don't make sense. | A 24-month radical packaging R&D project sits awkwardly with a conservative risk appetite and short time horizon. |

### 3.1 Completion note

The "Why" column was completed (from the underlying A/B/C outputs) for the seven evaluations
where the rater left it blank (Maria P1/P2/P5/P6; Azevedo P1/P2/P4). Casaca's four "why"
justifications (P3–P6) are his own and are reproduced verbatim. The "Wrong / risky /
implausible" column was completed for the evaluations where the output contained a genuinely
noteworthy issue (see §4); Casaca's two original comments (P3, P4) are also reproduced verbatim.

---

## 4. Plausibility check (researcher, grounded in the outputs)

**The manipulation is construct-valid.** Every "generic" output is the same template
(`Digital Presence & Lead Gen` + `Customer Feedback Loop`, maturity ≈ 2.0) that ignores the
profile, and the raters detected it consistently (see §5). The existing free-text comments
correctly identify the generic output as "generic".

**Genuine "wrong / risky / implausible" statements found in the outputs:**

1. **All six generic outputs** assert that the company's sector, strategic goals, digital maturity
   or customer feedback are *"undefined / unknown / blank"*, which directly contradicts the profile
   the rater holds. This is the defining flaw of the control condition (it is generated without the
   profile, so it writes as if the profile is empty).
2. **P1 (finetune):** the "AI-driven predictive risk-scoring engine" is scoped at **18 months**,
   exceeding Strato's explicit *"ROI timeline of under 12 months"*, and lists *"social media
   sentiment"* as an alternative credit-risk data source — implausible for a regulated lender.
3. **P3 (both tailored models):** the baseline's "B2B needs-analysis SaaS" and the fine-tuned
   "hyper-personalised advisor bot" are radical software builds that are unrealistic for a micro
   firm with a **€40k budget and a solo founder**; the baseline's second opportunity is also
   missing its first actions, resources, metrics and milestones.
4. **P6 (finetune):** the "next-gen sustainable packaging R&D" is a **24-month radical** initiative,
   conflicting with Orbit's *conservative* risk appetite and *short* time horizon.

**Rating-quality observations (for the discussion/limitations):**

- **Maria** uses a compressed scale (rarely below 3, even for the generic control — e.g. P1 generic
  scored R1 = 4 on "fit"; P2 generic scored R4 = 5 on "budget realism"). Her *rankings* are still
  correct, but her numeric discrimination is weak.
- **Casaca's** "wrong/risky" comment is about the *profile labels* ("long"/"short" horizon being
  ambiguous) rather than an output statement, and is duplicated verbatim across P3 and P4.
- **P3 baseline** ("B2B needs-analysis SaaS") is structurally incomplete (the second opportunity
  has no first actions / resources / metric / milestones), yet Casaca scored the baseline R2 = 5
  on actionability — the truncation was likely missed.

---

## 5. Results

### 5.1 Mean rating by condition (1–5)

Computed over 12 evaluations × 6 criteria = 72 ratings per condition.

| Criterion | finetune | baseline | generic | tailored − generic |
|-----------|----------|----------|---------|--------------------|
| R1 Fit to profile | 3.83 | 4.08 | 2.58 | +1.38 |
| R2 Actionability | 3.92 | 4.08 | 3.17 | +0.83 |
| R3 Strategic alignment | 4.08 | 4.17 | 2.50 | +1.63 |
| R4 Budget & timeline realism | 4.00 | 3.75 | 2.92 | +0.96 |
| R5 Usefulness | 4.17 | 3.92 | 2.58 | +1.46 |
| R6 Overall trust | 4.25 | 4.17 | 2.50 | +1.71 |
| **Overall** | **4.04** | **4.03** | **2.71** | **+1.33** |

### 5.2 Ranking

- The **generic control is ranked last in 12/12 evaluations** (sign test: p = (1/3)¹² ≈ 1.9×10⁻⁶).
- **Fine-tuned vs baseline:** fine-tuned ranked above baseline in **6** evaluations, baseline above
  fine-tuned in **5**, and **1** tie (P4 Azevedo, A = C). No meaningful difference.
- **Rater effect:** Casaca preferred the baseline in all 4 of his profiles; Maria (3/4) and Azevedo
  (3/4, 1 tie) preferred the fine-tuned model. The 6–5 split is driven by one rater, not by the model.

### 5.3 Key findings

1. **Tailoring is strongly valued.** Tailored reports (fine-tuned + baseline) score ≈ 4.04 vs 2.71
   for the generic control, and the generic control is ranked last in every one of the 12
   evaluations. This supports **RQ2_H2**.
2. **The fine-tuned model is not perceived as better than the baseline.** Mean 4.04 vs 4.03, and a
   6–5–1 ranking split. This is consistent with the A/B content-quality finding (no large semantic
   difference between the two tailored models).
3. **The generic control is penalised most on what tailoring should improve** — trust (+1.71),
   strategic alignment (+1.63), usefulness (+1.46) and fit (+1.38) — and least on actionability
   (+0.83) and budget realism (+0.96), because a cheap, concrete-but-wrong plan still looks
   "actionable" and "affordable".

---

## 6. Discussion points

- The expert rating triangulates the A/B evaluation: the two tailored models are close in quality
  (as the automated checks suggested), but both clearly outperform the generic control on perceived
  fit, alignment, usefulness and trust.
- The criterion-gap pattern is interpretable evidence for *tailoring* rather than *verbosity or
  formatting*: the generic control scores acceptably on the two "process" criteria (actionability,
  budget realism) precisely because it is cheap and concrete, while collapsing on the four
  "content" criteria that depend on the company profile.
- The fine-tuned model does not yet earn a perceived-quality advantage over the baseline, despite
  its better reliability/latency in the A/B run — a gap between *operational* and *perceived* value
  worth stating explicitly.
- **Limitations:** n = 3 raters and 6 profiles; one rater's compressed scale; a duplicated open-text
  comment; and a structurally incomplete baseline output in P3 that one rater appears not to have
  penalised. These are reported as-is rather than corrected.

---

## 7. Data snapshot (for traceability)

Raw scores, decoded by condition:

| Profile | Evaluator | finetune | baseline | generic |
|---------|-----------|----------|----------|---------|
| P1 | Maria | 4/4/4/4/4/4 | 3/3/4/2/4/4 | 4/4/2/4/4/3 |
| P1 | Azevedo | 4/4/5/4/4/5 | 4/4/4/3/4/4 | 4/4/3/4/2/3 |
| P2 | Maria | 3/3/3/5/4/4 | 3/4/4/4/4/4 | 3/3/3/5/4/3 |
| P2 | Azevedo | 3/4/4/5/4/5 | 3/4/3/4/4/4 | 3/4/2/3/4/3 |
| P3 | Casaca | 3/4/3/4/5/4 | 5/5/4/4/4/5 | 2/4/2/4/2/2 |
| P3 | Azevedo | 4/4/4/4/4/5 | 4/4/4/4/3/4 | 3/4/3/3/2/3 |
| P4 | Casaca | 5/4/4/3/5/4 | 5/5/5/4/4/4 | 2/2/2/1/1/1 |
| P4 | Azevedo | 4/4/4/3/4/4 | 4/4/4/4/3/4 | 2/3/2/2/2/3 |
| P5 | Maria | 4/4/4/4/3/4 | 4/4/4/3/3/3 | 2/3/3/2/3/2 |
| P5 | Casaca | 4/4/4/4/4/4 | 5/4/5/5/5/5 | 1/3/3/2/2/2 |
| P6 | Maria | 4/4/5/4/4/4 | 4/4/4/4/4/4 | 3/2/3/3/3/3 |
| P6 | Casaca | 4/4/5/4/5/4 | 5/4/5/4/5/5 | 2/2/2/2/2/2 |
