from db import supabase

notes = [
    # TASKS
    {
        "content": "Finish Chief Of Staff MVP",
        "note_type": "TASK",
        "priority": 1,
    },
    {
        "content": "Workout tomorrow morning",
        "note_type": "TASK",
        "priority": 1,
    },
    {
        "content": "Sleep before 11 PM",
        "note_type": "TASK",
        "priority": 1,
    },
    {
        "content": "Call Mom",
        "note_type": "TASK",
        "priority": 2,
    },
    {
        "content": "Learn RAG fundamentals",
        "note_type": "TASK",
        "priority": 3,
    },

    # OBSERVATIONS
    {
        "content": "I often start projects enthusiastically and lose momentum after 20 percent",
        "note_type": "OBSERVATION",
        "priority": 1,
    },
    {
        "content": "I spend time watching tutorials when I should be building",
        "note_type": "OBSERVATION",
        "priority": 1,
    },
    {
        "content": "I frequently delay sleep even though I know it affects my workouts",
        "note_type": "OBSERVATION",
        "priority": 1,
    },
    {
        "content": "I tend to scroll shorts immediately after waking up",
        "note_type": "OBSERVATION",
        "priority": 2,
    },
    {
        "content": "Building software gives me more satisfaction than consuming content",
        "note_type": "OBSERVATION",
        "priority": 2,
    },

    # DECISIONS
    {
        "content": "Build before learning",
        "note_type": "DECISION",
        "priority": 1,
    },
    {
        "content": "Do not start a new project before shipping the current one",
        "note_type": "DECISION",
        "priority": 1,
    },
    {
        "content": "Sleep is a non negotiable habit",
        "note_type": "DECISION",
        "priority": 1,
    },
    {
        "content": "Workout consistency is more important than workout intensity",
        "note_type": "DECISION",
        "priority": 2,
    },
    {
        "content": "Avoid chasing novelty for the sake of novelty",
        "note_type": "DECISION",
        "priority": 2,
    },
]

result = supabase.table("notes").insert(notes).execute()

print(f"Inserted {len(result.data)} notes")
