"""Skeleton FastAPI surface for Little RAG communication.

Endpoints are placeholders to be implemented alongside the runner.
"""

from fastapi import FastAPI

app = FastAPI(title="Parent Little RAG API")


@app.post("/little/heartbeat")
async def post_heartbeat() -> dict:
    """Receive health pings from Little RAG."""
    raise NotImplementedError


@app.post("/little/summary")
async def post_summary() -> dict:
    """Accept summary rows from Little RAG."""
    raise NotImplementedError


@app.get("/little/summary")
async def get_summary():
    """Return the most recent summary."""
    raise NotImplementedError


@app.post("/little/match")
async def post_match() -> dict:
    """Persist confirmed event/group mappings."""
    raise NotImplementedError


@app.get("/groups/list")
async def get_groups():
    """List known WhatsApp groups for matching."""
    raise NotImplementedError
