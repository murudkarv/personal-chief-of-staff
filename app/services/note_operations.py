"""
Note operations service - handles CRUD operations for notes
"""
from typing import List, Tuple

from db import supabase


def get_open_tasks() -> List[dict]:
    """Fetch all open (not completed, not archived) tasks."""
    result = (
        supabase.table("notes")
        .select("*")
        .eq("archived", False)
        .eq("completed", False)
        .eq("note_type", "TASK")
        .order("created_at", desc=False)
        .execute()
    )
    return result.data if hasattr(result, "data") else []


def get_note_by_id(note_id: int) -> dict | None:
    """Fetch a single note by ID."""
    result = supabase.table("notes").select("*").eq("id", note_id).execute()
    return result.data[0] if result.data else None


def mark_notes_complete(note_ids: List[int]) -> Tuple[int, List[int], List[int]]:
    """
    Mark multiple notes as complete.
    Returns: (completed_count, not_found_ids, non_task_ids)
    """
    completed_count = 0
    not_found_ids = []
    non_task_ids = []

    for note_id in note_ids:
        note = get_note_by_id(note_id)
        if not note:
            not_found_ids.append(note_id)
        elif note.get("note_type") != "TASK":
            non_task_ids.append(note_id)
        else:
            supabase.table("notes").update({"completed": True}).eq("id", note_id).execute()
            completed_count += 1

    return completed_count, not_found_ids, non_task_ids


def archive_notes(note_ids: List[int]) -> Tuple[int, List[int]]:
    """
    Archive multiple notes.
    Returns: (archived_count, not_found_ids)
    """
    archived_count = 0
    not_found_ids = []

    for note_id in note_ids:
        result = supabase.table("notes").update({"archived": True}).eq("id", note_id).execute()
        if result.data:
            archived_count += 1
        else:
            not_found_ids.append(note_id)

    return archived_count, not_found_ids


def delete_notes(note_ids: List[int]) -> Tuple[int, List[int]]:
    """
    Delete multiple notes.
    Returns: (deleted_count, not_found_ids)
    """
    deleted_count = 0
    not_found_ids = []

    for note_id in note_ids:
        # Check if note exists before deleting
        if not get_note_by_id(note_id):
            not_found_ids.append(note_id)
        else:
            supabase.table("notes").delete().eq("id", note_id).execute()
            deleted_count += 1

    return deleted_count, not_found_ids


def insert_note(content: str, note_type: str) -> bool:
    """Insert a new note."""
    try:
        supabase.table("notes").insert({
            "content": content,
            "note_type": note_type,
            "completed": False,
        }).execute()
        return True
    except Exception:
        return False
