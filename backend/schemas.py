"""Pydantic request/response models."""
from pydantic import BaseModel, Field

MAX_TEXT_LENGTH = 8000


class EntryCreate(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


class EntryOut(BaseModel):
    id: int
    text: str
    summary: str
    tags: list[str]
    created_at: str
