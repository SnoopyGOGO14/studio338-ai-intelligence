"""
Database module for WOTSON Agent.
Handles all interactions with the SQLite database.
"""

import sqlite3
import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

from utils.config import CONFIG

DB_PATH = Path(CONFIG["paths"]["data_root"]) / "wotson.db"

def get_conn():
    """Establishes and returns a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Creates the necessary database tables if they don't already exist."""
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS Events (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS WhatsAppGroups (
            id TEXT PRIMARY KEY,
            name TEXT,
            event_id TEXT,
            FOREIGN KEY (event_id) REFERENCES Events(id)
        );
        """)
        
        conn.execute("""
        CREATE TABLE IF NOT EXISTS WhatsAppMessages (
            id TEXT PRIMARY KEY,
            group_id TEXT NOT NULL,
            sender_id TEXT,
            content TEXT,
            timestamp DATETIME,
            category TEXT, -- e.g., 'question', 'answered'
            FOREIGN KEY (group_id) REFERENCES WhatsAppGroups(id)
        );
        """)
        conn.commit()
        print("Database initialized successfully with new schema.")

def get_unanswered_questions() -> list:
    """
    Fetches all messages that look like questions and haven't been answered.
    """
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM WhatsAppMessages
            WHERE content LIKE '%?'
              AND category IS NULL
              AND timestamp >= datetime('now', '-24 hours')
        """)
        return [dict(row) for row in rows.fetchall()]

def get_upcoming_events(within_days=3) -> list:
    """Fetches events that are coming up within a given number of days."""
    with get_conn() as conn:
        now = datetime.now()
        upcoming = (now + timedelta(days=within_days)).strftime('%Y-%m-%d')
        rows = conn.execute("""
            SELECT E.*, G.id as group_id
            FROM Events E
            JOIN WhatsAppGroups G ON G.event_id = E.id
            WHERE E.date BETWEEN ? AND ?
        """, (now.strftime('%Y-%m-%d'), upcoming))
        return [dict(row) for row in rows.fetchall()]

def get_group_silence_state(hours=8) -> list:
    """Finds groups that have been silent for a given number of hours."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT G.id as group_id, E.name as event_name, MAX(M.timestamp) as last_msg
            FROM WhatsAppGroups G
            JOIN WhatsAppMessages M ON G.id = M.group_id
            JOIN Events E ON G.event_id = E.id
            GROUP BY G.id
            HAVING (strftime('%s', 'now') - strftime('%s', M.timestamp)) > (? * 3600)
        """, (hours,))
        return [dict(row) for row in rows.fetchall()] 