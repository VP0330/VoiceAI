"""Database schema initialization and management."""
import sqlite3
from pathlib import Path
from typing import Optional


DB_PATH = Path("voice_insights.db")


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection (creates DB if not exists)."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database schema if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_metadata TEXT
        )
    """)

    # Create transcript_turns table for live streaming replay
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcript_turns (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            speaker TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    """)

    # Create llm_calls table for observability
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS llm_calls (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            latency_ms INTEGER,
            retry_count INTEGER,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_tokens INTEGER,
            success BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    """)

    # Create insights table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            theme TEXT NOT NULL,
            quote TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            actionable BOOLEAN,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    """)

    conn.commit()
    conn.close()


def save_session(session_id: str, metadata: Optional[str] = None) -> None:
    """Save a new session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (id, session_metadata)
        VALUES (?, ?)
    """, (session_id, metadata))
    conn.commit()
    conn.close()


def save_llm_call(
    session_id: str,
    llm_call_id: str,
    prompt: str,
    response: str,
    latency_ms: int,
    retry_count: int,
    input_tokens: int,
    output_tokens: int,
    success: bool
) -> None:
    """Save an LLM call record for observability."""
    conn = get_db_connection()
    cursor = conn.cursor()
    total_tokens = input_tokens + output_tokens
    cursor.execute("""
        INSERT INTO llm_calls 
        (id, session_id, prompt, response, latency_ms, retry_count, input_tokens, output_tokens, total_tokens, success)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (llm_call_id, session_id, prompt, response, latency_ms, retry_count, input_tokens, output_tokens, total_tokens, success))
    conn.commit()
    conn.close()


def save_insights(session_id: str, insights_data: list[dict]) -> None:
    """Save extracted insights for a session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    for insight in insights_data:
        cursor.execute("""
            INSERT INTO insights 
            (id, session_id, theme, quote, sentiment, actionable, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            insight["id"],
            session_id,
            insight["theme"],
            insight["quote"],
            insight["sentiment"],
            insight["actionable"],
            insight.get("recommendation")
        ))
    conn.commit()
    conn.close()
