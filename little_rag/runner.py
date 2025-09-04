"""Skeleton for Little RAG runner.

This module will later poll calendars and WhatsApp groups to propose
brand/event mappings. Only structure is provided for further development.
"""

from fastapi import FastAPI

app = FastAPI(title="Little RAG")


def load_config(path: str = "config/little_rag.yaml") -> dict:
    """Load configuration for the runner."""
    raise NotImplementedError


async def poll_once() -> None:
    """Fetch calendars and groups, then compute summary rows."""
    raise NotImplementedError


@app.on_event("startup")
async def startup_event() -> None:
    """Kick off background polling tasks."""
    pass
