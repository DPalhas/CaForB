from typing import Tuple, Any

import ollama
import time


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

Respond with JSON only. No explanation, no markdown."""


def generate_innovation_insight(company: dict, answers: dict) -> tuple[Any, int]:
    prompt = build_innovation_prompt(company, answers)
    start = time.time()
    response = ollama.chat(
        model="gemma4",
        messages=[{"role": "user", "content": prompt}]
    )
    duration_ms = int((time.time() - start) * 1000)
    return response['message']['content'], duration_ms
