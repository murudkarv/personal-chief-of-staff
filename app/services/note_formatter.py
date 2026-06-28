"""
Note formatting service - handles formatting notes for WhatsApp display
"""
from datetime import datetime
from typing import List


def format_date(created_at: str) -> str:
    """Format ISO datetime string to readable date format."""
    if not created_at or created_at == "N/A":
        return "N/A"
    
    try:
        date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return date_obj.strftime("%b %d, %Y")
    except Exception:
        try:
            return created_at[:10]
        except Exception:
            return "N/A"


def format_open_tasks(tasks: List[dict]) -> str:
    """Format open tasks for WhatsApp display."""
    if not tasks:
        return "✅ No open tasks!"
    
    items_text = "📋 *Open Tasks:*\n\n"
    for task in tasks:
        created_at = task.get("created_at", "N/A")
        formatted_date = format_date(created_at)
        items_text += f"ID: {task['id']} - {task['content']} ({formatted_date})\n"
    
    return items_text


def format_help_text() -> str:
    """Return formatted help text with all available commands."""
    return """Commands:

*briefing* - Get daily briefing
*open* - Show all open tasks
*task:* text - Add a task
*obs:* text - Add observation
*dec:* text - Add decision
*con:* text - Add constraint
*done:* id(s) - Mark task(s) as complete (e.g. done: 1 or done: 1,2,3)
*archive:* id(s) - Archive note(s) (e.g. archive: 1 or archive: 1,2,3)
*delete:* id(s) - Delete note(s) (e.g. delete: 1 or delete: 1,2,3)"""


def format_completion_status(
    completed_count: int,
    not_found_ids: List[int],
    non_task_ids: List[int] = None,
) -> str:
    """Format completion status message with warnings."""
    message = f"✅ {completed_count} task(s) marked as complete"
    
    if not_found_ids:
        message += f"\n⚠️ Not found: {', '.join(map(str, not_found_ids))}"
    
    if non_task_ids:
        message += f"\n⚠️ Not tasks: {', '.join(map(str, non_task_ids))}"
    
    return message


def format_archive_status(archived_count: int, not_found_ids: List[int]) -> str:
    """Format archive status message."""
    message = f"✅ {archived_count} note(s) archived"
    
    if not_found_ids:
        message += f"\n⚠️ Not found: {', '.join(map(str, not_found_ids))}"
    
    return message


def format_delete_status(deleted_count: int, not_found_ids: List[int]) -> str:
    """Format delete status message."""
    message = f"🗑️ {deleted_count} note(s) deleted"
    
    if not_found_ids:
        message += f"\n⚠️ Not found: {', '.join(map(str, not_found_ids))}"
    
    return message
