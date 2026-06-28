import os
from datetime import datetime
from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


class NoteType(str, Enum):
    TASK = "TASK"
    OBSERVATION = "OBSERVATION"
    DECISION = "DECISION"
    CONSTRAINT = "CONSTRAINT"


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)
    completed: bool = False
    note_type: NoteType = Field(default=NoteType.TASK)
    priority: int = Field(default=3, ge=1, le=5)
    archived: bool = False


class NoteResponse(NoteCreate):
    id: int
    created_at: datetime


class ReflectionCreate(BaseModel):
    energy: int = Field(..., ge=1, le=5)
    wins: Optional[str] = None
    failures: Optional[str] = None
    insight: Optional[str] = None


class ReflectionResponse(ReflectionCreate):
    id: int
    created_at: datetime
