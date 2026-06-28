"""
WhatsApp command handlers - handles parsing and executing user commands
"""
from typing import List

from app.services.briefing import get_daily_briefing
from app.services.note_formatter import (
    format_archive_status,
    format_completion_status,
    format_delete_status,
    format_help_text,
    format_open_tasks,
)
from app.services.note_operations import (
    archive_notes,
    delete_notes,
    get_open_tasks,
    insert_note,
    mark_notes_complete,
)
from app.services.whatsapp import send_whatsapp_message
from db import supabase


def parse_ids_from_command(command_text: str) -> List[int]:
    """
    Parse comma-separated IDs from command text.
    Example: "done: 1,2,3" -> [1, 2, 3]
    """
    try:
        ids_str = command_text.replace(":", "", 1).strip()
        return [int(id.strip()) for id in ids_str.split(",")]
    except ValueError:
        return []


def handle_briefing(user_phone: str) -> None:
    """Handle briefing command."""
    result = supabase.table("notes").select("*").eq("archived", False).execute()
    briefing = get_daily_briefing(result.data)
    send_whatsapp_message(user_phone, briefing)


def handle_open(user_phone: str) -> None:
    """Handle open tasks command."""
    tasks = get_open_tasks()
    formatted = format_open_tasks(tasks)
    send_whatsapp_message(user_phone, formatted)


def handle_task(user_phone: str, message_text: str) -> None:
    """Handle task creation command."""
    task_content = message_text.replace("task:", "", 1).strip()
    if not task_content:
        send_whatsapp_message(user_phone, "❌ Task cannot be empty")
        return
    
    success = insert_note(task_content, "TASK")
    if success:
        send_whatsapp_message(user_phone, f"✅ Task added: {task_content}")
    else:
        send_whatsapp_message(user_phone, f"❌ Error adding task")


def handle_observation(user_phone: str, message_text: str) -> None:
    """Handle observation creation command."""
    obs_content = message_text.replace("obs:", "", 1).strip()
    if not obs_content:
        send_whatsapp_message(user_phone, "❌ Observation cannot be empty")
        return
    
    success = insert_note(obs_content, "OBSERVATION")
    if success:
        send_whatsapp_message(user_phone, f"✅ Observation noted: {obs_content}")
    else:
        send_whatsapp_message(user_phone, f"❌ Error adding observation")


def handle_decision(user_phone: str, message_text: str) -> None:
    """Handle decision creation command."""
    dec_content = message_text.replace("dec:", "", 1).strip()
    if not dec_content:
        send_whatsapp_message(user_phone, "❌ Decision cannot be empty")
        return
    
    success = insert_note(dec_content, "DECISION")
    if success:
        send_whatsapp_message(user_phone, f"✅ Decision recorded: {dec_content}")
    else:
        send_whatsapp_message(user_phone, f"❌ Error adding decision")


def handle_constraint(user_phone: str, message_text: str) -> None:
    """Handle constraint creation command."""
    con_content = message_text.replace("con:", "", 1).strip()
    if not con_content:
        send_whatsapp_message(user_phone, "❌ Constraint cannot be empty")
        return
    
    success = insert_note(con_content, "CONSTRAINT")
    if success:
        send_whatsapp_message(user_phone, f"✅ Constraint added: {con_content}")
    else:
        send_whatsapp_message(user_phone, f"❌ Error adding constraint")


def handle_done(user_phone: str, message_text: str) -> None:
    """Handle mark complete command."""
    task_ids = parse_ids_from_command(message_text)
    
    if not task_ids:
        send_whatsapp_message(user_phone, "❌ Invalid task IDs. Use: done: <id> or done: <id>,<id>,<id>")
        return
    
    completed_count, not_found_ids, non_task_ids = mark_notes_complete(task_ids)
    message = format_completion_status(completed_count, not_found_ids, non_task_ids)
    send_whatsapp_message(user_phone, message)


def handle_archive(user_phone: str, message_text: str) -> None:
    """Handle archive command."""
    note_ids = parse_ids_from_command(message_text)
    
    if not note_ids:
        send_whatsapp_message(user_phone, "❌ Invalid note IDs. Use: archive: <id> or archive: <id>,<id>,<id>")
        return
    
    archived_count, not_found_ids = archive_notes(note_ids)
    message = format_archive_status(archived_count, not_found_ids)
    send_whatsapp_message(user_phone, message)


def handle_delete(user_phone: str, message_text: str) -> None:
    """Handle delete command."""
    note_ids = parse_ids_from_command(message_text)
    
    if not note_ids:
        send_whatsapp_message(user_phone, "❌ Invalid note IDs. Use: delete: <id> or delete: <id>,<id>,<id>")
        return
    
    deleted_count, not_found_ids = delete_notes(note_ids)
    message = format_delete_status(deleted_count, not_found_ids)
    send_whatsapp_message(user_phone, message)


def handle_help(user_phone: str) -> None:
    """Handle help command."""
    help_text = format_help_text()
    send_whatsapp_message(user_phone, help_text)


def handle_unknown(user_phone: str) -> None:
    """Handle unknown command."""
    send_whatsapp_message(user_phone, "Unknown command. Type *help* for available commands.")
