import ollama
import time
import json
import re


def build_innovation_prompt(company: dict, answers: dict) -> str:
    return f"""You are a strategic innovation advisor. Analyse the following company 
profile and questionnaire responses, then respond ONLY with valid JSON in this exact format:
{{
  "maturity_score": <float 0-10>,
  "opportunities": [
    {{
      "type": "incremental or radical",
      "title": "<string>",
      "rationale": "<string>",
      "impact": "low, medium or high",
      "difficulty": "low, medium or high",
      "timeframe": "<string>"
    }}
  ],
  "next_steps": ["<string>"],
  "key_weaknesses": ["<string>"]
}}

Company: {company['name']} | Sector: {company['sector']} | Size: {company['size']}
Questionnaire answers: {answers}

IMPORTANT: Respond with a single valid JSON object only. No markdown, no explanation, no extra text. 
Ensure all arrays are closed with ] and the object is closed with }}."""


def _extract_json(text: str) -> dict:
    """Try multiple strategies to extract valid JSON from LLM output."""
    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: extract first {...} block
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass

    # Strategy 3: fix common Gemma4 mistake — trailing } instead of ]}
    try:
        fixed = re.sub(r'\}\s*$', ']}', text.rstrip())
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 4: fix unclosed arrays before final }
    try:
        fixed = text.rstrip()
        if not fixed.endswith(']}'):
            fixed = re.sub(r'(\s*\]?\s*)\}$', '\n  ]\n}', fixed)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    return {}


def generate_innovation_insight(company: dict, answers: dict):
    prompt = build_innovation_prompt(company, answers)
    start = time.time()
    response = ollama.chat(
        model="gemma4",
        messages=[{"role": "user", "content": prompt}]
    )
    duration_ms = int((time.time() - start) * 1000)
    raw_text = response['message']['content']
    return raw_text, duration_ms
