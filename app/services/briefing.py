from datetime import date

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
BRIEFING_CACHE = {}


def build_briefing_prompt(notes):
    tasks = [n["content"] for n in notes if n["note_type"] == "TASK" and not n["completed"]]
    observations = [n["content"] for n in notes if n["note_type"] == "OBSERVATION"]
    decisions = [n["content"] for n in notes if n["note_type"] == "DECISION"]

    return f"""
    You are Vaibhav's Chief of Staff.

    Decisions:
    {chr(10).join(f'- {d}' for d in decisions)}

    Tasks:
    {chr(10).join(f'- {t}' for t in tasks)}

    Observations:
    {chr(10).join(f'- {o}' for o in observations)}

    Reply in 5 short bullets:
    1. Morning briefing
    2. Top 3 priorities
    3. Risks/distractions
    4. Uncomfortable truth
    5. One action for today
    """


def generate_briefing_text(notes):
    prompt = build_briefing_prompt(notes)
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3:8b",
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 160,
            },
        },
        timeout=120,
    )
    return response.json().get("response", "").strip()


def get_daily_briefing(notes):
    today = date.today().isoformat()
    if today not in BRIEFING_CACHE:
        BRIEFING_CACHE[today] = generate_briefing_text(notes)
    return BRIEFING_CACHE[today]
