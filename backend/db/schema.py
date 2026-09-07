"""Database schema initialization and management."""
import psycopg2
from psycopg2 import pool
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# PostgreSQL connection pool
db_pool = None


def init_connection_pool():
    """Initialize PostgreSQL connection pool."""
    global db_pool
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "voice_insights")
    db_user = os.getenv("DB_USER", "voice_user")
    db_password = os.getenv("DB_PASSWORD", "voice_password")
    
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )


def get_db_connection():
    """Get a database connection from pool."""
    if db_pool is None:
        init_connection_pool()
    return db_pool.getconn()


def return_connection(conn):
    """Return connection to pool."""
    if db_pool is not None:
        db_pool.putconn(conn)


def init_db() -> None:
    """Initialize database schema if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
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
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                speaker TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create llm_calls table for observability
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_calls (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                latency_ms INTEGER,
                retry_count INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                theme TEXT NOT NULL,
                quote TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                actionable BOOLEAN,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("[DB] Tables initialized successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"[DB] Error initializing tables: {e}")
        raise
    finally:
        cursor.close()
        return_connection(conn)


def save_session(session_id: str, metadata: Optional[str] = None) -> None:
    """Save a new session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO sessions (id, session_metadata)
            VALUES (%s, %s)
        """, (session_id, metadata))
        conn.commit()
    finally:
        cursor.close()
        return_connection(conn)


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
    
    try:
        total_tokens = input_tokens + output_tokens
        cursor.execute("""
            INSERT INTO llm_calls 
            (id, session_id, prompt, response, latency_ms, retry_count, input_tokens, output_tokens, total_tokens, success)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (llm_call_id, session_id, prompt, response, latency_ms, retry_count, input_tokens, output_tokens, total_tokens, success))
        conn.commit()
    finally:
        cursor.close()
        return_connection(conn)


def save_insights(session_id: str, insights_data: list[dict]) -> None:
    """Save extracted insights for a session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for insight in insights_data:
            cursor.execute("""
                INSERT INTO insights 
                (id, session_id, theme, quote, sentiment, actionable, recommendation)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
    finally:
        cursor.close()
        return_connection(conn)
