import sqlite3
from sqlite3 import Connection, Cursor
from pathlib import Path
from backend.utils.config import DB_PATH
from backend.utils.logger import app_logger

def get_db_connection() -> Connection:
    """Gets a connection to the SQLite database."""
    # Ensure the directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schemas."""
    app_logger.info("Initializing database schemas...")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Jobs Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            voice_id TEXT NOT NULL,
            avatar_url TEXT,
            script_mode TEXT,
            script_input TEXT,
            preferred_engine TEXT,
            selected_engine TEXT,
            status TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            message TEXT,
            generated_script TEXT,
            result_url TEXT,
            fallback_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Voice Models Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS voices (
            voice_id TEXT PRIMARY KEY,
            engine TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        app_logger.info("Database schemas initialized.")
    except Exception as e:
        app_logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()

def save_voice(voice_id: str, engine: str, status: str):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO voices (voice_id, engine, status) VALUES (?, ?, ?)",
            (voice_id, engine, status)
        )
        conn.commit()
    finally:
        conn.close()

def get_voice(voice_id: str) -> dict | None:
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM voices WHERE voice_id = ?", (voice_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def save_job(job_data: dict):
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO jobs (
                job_id, voice_id, avatar_url, script_mode, script_input,
                preferred_engine, selected_engine, status, progress, message, generated_script
            ) VALUES (
                :job_id, :voice_id, :avatar_url, :script_mode, :script_input,
                :preferred_engine, :selected_engine, :status, :progress, :message, :generated_script
            )
        ''', job_data)
        conn.commit()
    finally:
        conn.close()

def update_job_status(job_id: str, updates: dict):
    conn = get_db_connection()
    try:
        set_clauses = []
        values = []
        for k, v in updates.items():
            set_clauses.append(f"{k} = ?")
            values.append(v)
            
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(job_id)
        
        query = f"UPDATE jobs SET {', '.join(set_clauses)} WHERE job_id = ?"
        conn.execute(query, values)
        conn.commit()
    finally:
        conn.close()

def get_job(job_id: str) -> dict | None:
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
