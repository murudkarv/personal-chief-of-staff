from datetime import date

import requests

from db import supabase

OLLAMA_URL = "http://localhost:11434/api/generate"
BRIEFING_CACHE = {}


def build_briefing_prompt(notes, reflections=None):
    if reflections is None:
        reflections = []

    tasks = [n["content"] for n in notes if n["note_type"] == "TASK" and not n["completed"]]
    observations = [n["content"] for n in notes if n["note_type"] == "OBSERVATION"]
    decisions = [n["content"] for n in notes if n["note_type"] == "DECISION"]
    constraints = [n["content"] for n in notes if n["note_type"] == "CONSTRAINT"]

    tasks_str = "\n".join(f"- {t}" for t in tasks)
    decisions_str = "\n".join(f"- {d}" for d in decisions)
    observations_str = "\n".join(f"- {o}" for o in observations)
    constraints_str = "\n".join(f"- {c}" for c in constraints)

    reflections_str = ""
    if reflections:
        reflection_items = []
        for r in reflections:
            item = f"- Energy: {r['energy']}"
            if r.get("wins"):
                item += f"\n  Win: {r['wins']}"
            if r.get("failures"):
                item += f"\n  Struggle: {r['failures']}"
            if r.get("insight"):
                item += f"\n  Insight: {r['insight']}"
            reflection_items.append(item)
        reflections_str = "\n\n".join(reflection_items)

    reflections_section = f"""
Recent Reflections:
{reflections_str}
""" if reflections_str else ""

    return f"""You are my Chief of Staff.

You will receive:

- Tasks (what I want to do)
- Decisions (principles I claim to follow)
- Observations (evidence of my behavior)
- Constraints (factors that limit execution)
- Recent Reflections (how I actually performed)

Rules:

- Constraints are more important than tasks.
- Recommendations must be realistic given the constraints.
- Do not invent facts.
- Use observations as evidence.
- Point out contradictions between decisions and behavior.
- Keep the briefing under 150 words.

Generate:

## Top 3 Focus Areas
Three things that deserve attention today.

## Primary Constraint
The single biggest factor limiting execution right now.

## Biggest Risk
What is most likely to derail today.

## Reminder
One decision that is especially relevant today.

## Question
One question that would help clarify the situation.

Tasks:
{tasks_str}

Decisions:
{decisions_str}

Observations:
{observations_str}

Constraints:
{constraints_str}{reflections_section}"""


def generate_briefing_text(notes, reflections=None):
    prompt = build_briefing_prompt(notes, reflections)
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
        # Fetch latest 5 reflections
        reflections_result = (
            supabase
            .table("reflections")
            .select("*")
            .order("created_at", desc=True)
            .limit(5)
            .execute()
        )
        reflections = reflections_result.data if hasattr(reflections_result, "data") else []
        BRIEFING_CACHE[today] = generate_briefing_text(notes, reflections)
    return BRIEFING_CACHE[today]
