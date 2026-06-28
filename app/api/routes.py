from fastapi import APIRouter, HTTPException, Request

from app.services.whatsapp import (
    mark_message_as_read,
    parse_whatsapp_message,
)
from db import NoteCreate, NoteResponse, ReflectionCreate, ReflectionResponse, supabase

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/note", response_model=NoteResponse)
def create_note(note: NoteCreate):
    try:
        result = supabase.table("notes").insert(note.model_dump()).execute()

        if not getattr(result, "data", None):
            raise HTTPException(status_code=500, detail="Failed to insert note")

        return NoteResponse.model_validate(result.data[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/notes")
def get_notes():
    result = (
        supabase
        .table("notes")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    notes = [NoteResponse.model_validate(row).model_dump() for row in result.data]
    return {"notes": notes}


@router.get("/briefing")
def briefing():
    result = supabase.table("notes").select("*").eq("archived", False).execute()
    return {"briefing": get_daily_briefing(result.data)}


@router.patch("/notes/{note_id}/complete", response_model=NoteResponse)
def complete_note(note_id: int):
    try:
        result = supabase.table("notes").update({"completed": True}).eq("id", note_id).execute()

        if not getattr(result, "data", None):
            raise HTTPException(status_code=404, detail="Note not found")

        return NoteResponse.model_validate(result.data[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.patch("/notes/{note_id}/archive", response_model=NoteResponse)
def archive_note(note_id: int):
    try:
        result = supabase.table("notes").update({"archived": True}).eq("id", note_id).execute()

        if not getattr(result, "data", None):
            raise HTTPException(status_code=404, detail="Note not found")

        return NoteResponse.model_validate(result.data[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/reflection", response_model=ReflectionResponse)
def create_reflection(reflection: ReflectionCreate):
    try:
        result = supabase.table("reflections").insert(reflection.model_dump()).execute()

        if not getattr(result, "data", None):
            raise HTTPException(status_code=500, detail="Failed to insert reflection")

        return ReflectionResponse.model_validate(result.data[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/reflections")
def get_reflections():
    result = (
        supabase
        .table("reflections")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    reflections = [ReflectionResponse.model_validate(row).model_dump() for row in result.data]
    return {"reflections": reflections}


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp webhook messages."""
    payload = await request.json()
    _log_webhook_payload(payload)

    # Parse the incoming message
    message = parse_whatsapp_message(payload)
    if not message:
        return {"status": "ok"}

    user_phone = message.get("from")
    message_text = message.get("text", "").strip().lower()
    message_id = message.get("message_id")

    # Mark message as read
    if message_id:
        mark_message_as_read(message_id)

    # Route command to appropriate handler
    _route_command(user_phone, message_text)

    return {"status": "ok"}


def _log_webhook_payload(payload: dict) -> None:
    """Log incoming webhook payload for debugging."""
    print("=" * 80)
    print("WHATSAPP MESSAGE RECEIVED")
    print(payload)
    print("=" * 80)


def _route_command(user_phone: str, message_text: str) -> None:
    """Route user command to appropriate handler."""
    from app.services.command_handlers import (
        handle_archive,
        handle_briefing,
        handle_constraint,
        handle_decision,
        handle_delete,
        handle_done,
        handle_help,
        handle_observation,
        handle_open,
        handle_task,
        handle_unknown,
    )

    if message_text in ("briefing", "brief"):
        handle_briefing(user_phone)
    elif message_text == "open":
        handle_open(user_phone)
    elif message_text.startswith("task:"):
        handle_task(user_phone, message_text)
    elif message_text.startswith("obs:"):
        handle_observation(user_phone, message_text)
    elif message_text.startswith("dec:"):
        handle_decision(user_phone, message_text)
    elif message_text.startswith("con:"):
        handle_constraint(user_phone, message_text)
    elif message_text.startswith("done:"):
        handle_done(user_phone, message_text)
    elif message_text.startswith("archive:"):
        handle_archive(user_phone, message_text)
    elif message_text.startswith("delete:"):
        handle_delete(user_phone, message_text)
    elif message_text == "help":
        handle_help(user_phone)
    else:
        handle_unknown(user_phone)


@router.get("/webhook/whatsapp")
async def whatsapp_verify(request: Request):
    """Webhook verification endpoint for WhatsApp."""
    verify_token = request.query_params.get("hub.verify_token", "")
    challenge = request.query_params.get("hub.challenge", "")
    
    # You should set WHATSAPP_VERIFY_TOKEN in your environment variables
    from os import getenv
    expected_token = getenv("WHATSAPP_VERIFY_TOKEN", "your_verify_token")
    
    if verify_token == expected_token:
        return int(challenge) if challenge.isdigit() else challenge
    
    raise HTTPException(status_code=403, detail="Invalid verification token")
