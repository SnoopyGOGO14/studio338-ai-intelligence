"""
Database module for WOTSON Agent.
Handles all interactions with the SQLite database.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from utils.config import CONFIG

DB_PATH = Path(CONFIG["paths"]["data_root"]) / "wotson.db"

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """
    Creates the necessary database tables if they don't already exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table for all incoming messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        group_id TEXT NOT NULL,
        sender_id TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        is_question BOOLEAN DEFAULT FALSE,
        is_answered BOOLEAN DEFAULT FALSE
    );
    """)
    
    # Table for events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        event_name TEXT NOT NULL,
        start_time DATETIME NOT NULL,
        relevant_groups TEXT -- JSON list of group_ids
    );
    """)
    
    # Table to track group activity
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        group_id TEXT PRIMARY KEY,
        group_name TEXT,
        last_activity_ts DATETIME NOT NULL
    );
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def log_message(message: Dict[str, Any]):
    """Logs a new message to the database and updates group activity."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT OR REPLACE INTO messages (message_id, group_id, sender_id, content, timestamp)
    VALUES (?, ?, ?, ?, ?);
    """, (message['message_id'], message['group_id'], message['sender'], message['content'], message['timestamp']))
    
    cursor.execute("""
    INSERT OR REPLACE INTO groups (group_id, group_name, last_activity_ts)
    VALUES (?, ?, ?);
    """, (message['group_id'], message.get('group_name', ''), message['timestamp']))
    
    conn.commit()
    conn.close()

def get_unanswered_questions() -> List[Dict[str, Any]]:
    """Fetches all messages flagged as unanswered questions from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE is_question = TRUE AND is_answered = FALSE;")
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return questions

def get_upcoming_events(reminder_days: int) -> List[Dict[str, Any]]:
    """Fetches events scheduled to start within the reminder window."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT * FROM events 
    WHERE start_time BETWEEN DATETIME('now') AND DATETIME('now', '+{days} days');
    """.format(days=reminder_days)
    cursor.execute(query)
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return events

def get_all_groups_activity() -> List[Dict[str, Any]]:
    """Fetches the last activity timestamp for all monitored groups."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, last_activity_ts FROM groups;")
    groups = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return groups

def mark_question_as_answered(message_id: str):
    """Marks a specific question as answered in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET is_answered = TRUE WHERE message_id = ?;", (message_id,))
    conn.commit()
    conn.close() 