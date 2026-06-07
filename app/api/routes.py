from fastapi import APIRouter, HTTPException

from app.services.briefing import get_daily_briefing
from db import NoteCreate, NoteResponse, supabase

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
