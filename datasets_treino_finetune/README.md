# CaForB Fine-tuning Dataset

## Overview

This directory contains the training data pipeline for fine-tuning a Gemma model (or equivalent) to replace the current prompt-engineered `ollama.chat(model="gemma4")` call with a domain-specialized model that directly maps structured corporate survey inputs to structured innovation advisory outputs.

## Directory Structure

```
datasets_treino_finetune/
├── templates/                          # Phase 1: Free-text template libraries
│   ├── company_description/
│   │   ├── by_sector/                  # 26 sector-specific descriptions (3-5 variants each)
│   │   └── by_size/                    # Size-specific descriptions (3 variants each)
│   ├── strategic_goals/               # By priority type: growth, efficiency, market_defense, diversification
│   ├── past_initiatives/              # By maturity: none, low, medium, high
│   ├── team_size/                     # By company size: micro, small, medium, large
│   └── additional_context/            # fundraising, restructuring, regulatory_change
│
├── scripts/                            # Generation & tooling
│   ├── generate_surveys.py            # Combinatorial survey input generator
│   ├── coverage_check.py              # Ensures balanced distribution across constraint combos
│   ├── generate_synthetic.py          # Calls external LLM API for output generation
│   ├── review_cli.py                  # Expert review CLI
│   ├── augment_with_fewshot.py        # Few-shot augmentation from reviewed seed
│   ├── coverage_report.py             # Pre-training distribution validation
│   ├── convert_to_jsonl.py            # Individual JSONs -> train.jsonl / validation.jsonl
│   └── validate_schema.py             # Schema & business rule validation
│
├── raw/                                # Phase 2 output (~500 examples from external LLM)
├── reviewed/                           # Phase 3 output (80-100 expert-reviewed examples)
├── rejected/                           # Discarded examples
├── augmented/                          # Phase 4 output (~400 few-shot generated examples)
│
├── final/                              # Training-ready dataset
│   ├── examples/                       # Canonical JSONs (one per example)
│   ├── train.jsonl                     # 400 examples for training
│   ├── validation.jsonl               # 100 examples for validation
│   └── coverage_report.json           # Final distribution breakdown
│
└── README.md                           # This file
```

## Example JSON Schema

Each example in `final/examples/` follows this structure:

```json
{
  "id": "001",
  "version": 1,
  "split": "train",
  "metadata": {
    "sector": "Fintech",
    "size": "Medium",
    "regulatory_environment": "high",
    "risk_appetite": "conservative",
    "strategic_priority": "efficiency",
    "competitive_pressure": "medium",
    "estimated_budget_eur": 440000,
    "reviewed": true,
    "source": "gpt4o_synthetic",
    "generated_at": "2026-08-01T12:00:00Z"
  },
  "instruction": "You are a strategic corporate innovation advisor. Analyse the company profile and survey responses, then output ONLY a valid JSON object with the exact schema provided.",
  "input": {
    "company": { "name": "...", "sector": "...", "size": "..." },
    "answers": { /* 17 survey fields */ }
  },
  "output": {
    "maturity_score": 5.8,
    "opportunities": [ /* ranked opportunities with execution plans */ ],
    "next_steps": [ /* prioritized executive actions */ ],
    "key_weaknesses": [ /* identified barriers */ ]
  }
}
```

## Four-Phase Data Collection Pipeline

### Phase 1: Programmatic Survey Input Generation
- Combinatorial grid across 5 key constraint dimensions (risk × priority × regulatory × sector × size)
- Free-text fields populated from template libraries with controlled variation
- Target: 500 diverse survey inputs

### Phase 2: Synthetic Output Generation
- Feed each input through GPT-4o or Claude 3.5 Sonnet
- Output stored in `raw/` directory
- Estimated cost: ~€5-10 total

### Phase 3: Expert Review
- Review 80-100 examples using `review_cli.py`
- Verify maturity scores, opportunity quality, and constraint compliance
- Corrected examples saved to `reviewed/`

### Phase 4: Augmented Generation
- Use reviewed examples as few-shot prompts
- Generate remaining ~400 examples with higher quality
- Saved to `augmented/`, then all validated examples copied to `final/`

## Coverage Requirements

Every combination of the following must have at least 3 examples:

| Dimension        | Values                                              | Count |
|------------------|-----------------------------------------------------|-------|
| riskAppetite     | conservative, balanced, bold                        | 3     |
| strategicPriority| growth, efficiency, market_defense, diversification | 4     |
| regulatoryEnv    | low, medium, high                                   | 3     |
|                  | **Minimum combos:**                                 | **36** |

## Validation Rules (validate_schema.py)

1. `maturity_score` must be float in range 0-10
2. Opportunity type must respect risk appetite: conservative → all incremental
3. Budget sanity: execution plan resources must not exceed estimated budget
4. Regulatory: high regulation → at least one firstAction mentions compliance/legal
5. Priority alignment: at least one opportunity targets the stated priority
6. No duplicate weaknesses within/across examples from same sector
