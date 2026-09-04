"""FastAPI app: three endpoints for the AI Content Assistant."""
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()  # must run before ai.py reads GEMINI_API_KEY/GEMINI_MODEL at import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import ai
import database
from schemas import EntryCreate, EntryOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="AI Content Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/entries", response_model=EntryOut, status_code=201)
def create_entry(payload: EntryCreate):
    try:
        ai_result = ai.call_gemini(payload.text)
    except ai.AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return database.create_entry(
        text=payload.text,
        summary=ai_result["summary"],
        tags=ai_result["tags"],
    )


@app.get("/entries", response_model=list[EntryOut])
def get_entries():
    return database.list_entries()


@app.get("/entries/{entry_id}", response_model=EntryOut)
def get_entry(entry_id: int):
    entry = database.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found.")
    return entry
