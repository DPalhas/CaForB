import ollama

def build_innovation_prompt(company: dict, answers: dict) -> str:
    return f"""
You are a strategic innovation advisor. Analyse the following company profile
and questionnaire responses, then provide:
1. An innovation maturity score (0-10)
2. Top 3 innovation opportunities (incremental or radical)
3. Recommended next steps aligned with their business strategy

Company: {company['name']} | Sector: {company['sector']} | Size: {company['size']}

Questionnaire Responses:
{answers}

Provide a structured, actionable response.
"""

def generate_innovation_insight(company: dict, answers: dict) -> str:
    prompt = build_innovation_prompt(company, answers)
    response = ollama.chat(
        model="gemma4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']