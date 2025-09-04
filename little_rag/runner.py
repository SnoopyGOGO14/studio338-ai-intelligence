"""Little RAG runner: polls calendars and groups to propose event/group mappings."""
import asyncio
from datetime import datetime
from typing import List
import httpx
import yaml
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Little RAG")

class SummaryRow(BaseModel):
    event_date: str
    brand: str
    group_title: str
    group_id: str
    last_active_ts: str | None = None
    match_conf: float
    status: str
    notes: List[str] = []

async def load_config(path: str = "config/little_rag.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

async def load_calendars(cfg: dict) -> List[dict]:
    # Placeholder for fetching and parsing calendars
    return []

async def load_brands(cfg: dict) -> dict:
    with open(cfg["brand_list"]) as f:
        data = yaml.safe_load(f)
    return data.get("brands", [])

async def get_groups(parent_api: str) -> List[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{parent_api}/groups/list")
        resp.raise_for_status()
        return resp.json()

async def match(rows: List[dict], brands: List[dict], groups: List[dict]) -> List[SummaryRow]:
    # Deterministic placeholder matching logic
    results: List[SummaryRow] = []
    for row in rows:
        results.append(SummaryRow(
            event_date=row.get("date", ""),
            brand=row.get("brand", ""),
            group_title="",
            group_id="",
            match_conf=0.0,
            status="unmatched",
        ))
    return results

async def loop():
    cfg = await load_config()
    parent_api = cfg["parent_api"]
    while True:
        rows = await load_calendars(cfg)
        brands = await load_brands(cfg)
        groups = await get_groups(parent_api)
        table = await match(rows, brands, groups)
        async with httpx.AsyncClient() as client:
            await client.post(f"{parent_api}/little/heartbeat", json={
                "calendar_ok": 1,
                "last_poll_ts": datetime.utcnow().isoformat(),
            })
            await client.post(f"{parent_api}/little/summary", json=[r.dict() for r in table])
            for r in table:
                if r.status == "matched" and r.match_conf >= 0.8:
                    await client.post(f"{parent_api}/little/match", json=r.dict())
        await asyncio.sleep(cfg.get("poll_minutes", 10) * 60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(loop())
