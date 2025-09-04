"""FastAPI endpoints for Little RAG communication."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Parent Little RAG API")

class Heartbeat(BaseModel):
    calendar_ok: int
    last_poll_ts: str

class SummaryRow(BaseModel):
    event_date: str
    brand: str
    group_title: str
    group_id: str
    last_active_ts: Optional[str] = None
    match_conf: float
    status: str
    notes: List[str] = []

_summary_cache: List[SummaryRow] = []

@app.post("/little/heartbeat")
async def post_heartbeat(hb: Heartbeat):
    # In a full system, this would persist to the database
    return {"ok": True}

@app.post("/little/summary")
async def post_summary(rows: List[SummaryRow]):
    global _summary_cache
    _summary_cache = rows
    return {"received": len(rows)}

@app.get("/little/summary", response_model=List[SummaryRow])
async def get_summary():
    return _summary_cache

@app.post("/little/match")
async def post_match(row: SummaryRow):
    if row.status != "matched":
        raise HTTPException(400, "row.status must be 'matched'")
    # Persist mapping here in a full implementation
    return {"mapped": row.group_id, "event_date": row.event_date}

@app.get("/groups/list")
async def get_groups():
    # Placeholder: in production this would query WhatsApp groups
    return [
        {"group_id": "123", "name": "Studio338 Launch", "last_active_ts": "2024-01-01T00:00:00"},
        {"group_id": "456", "name": "AnotherBrand 2024", "last_active_ts": "2024-01-05T00:00:00"},
    ]
