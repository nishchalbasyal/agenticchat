import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from datetime import datetime

# Shared database connection and checkpointer for all backends
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# Create metadata table for conversation titles
def init_metadata_table():
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_metadata (
                thread_id TEXT PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP
            )
        """)
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Table already exists

# Initialize metadata table on import
init_metadata_table()

# Helper functions for metadata
def save_title(thread_id: str, title: str):
    """Save conversation title to metadata table"""
    conn.execute(
        "INSERT OR REPLACE INTO conversation_metadata (thread_id, title, created_at) VALUES (?, ?, ?)",
        (thread_id, title, datetime.now())
    )
    conn.commit()

def get_title(thread_id: str) -> str:
    """Retrieve conversation title from metadata table"""
    cursor = conn.execute(
        "SELECT title FROM conversation_metadata WHERE thread_id = ?",
        (thread_id,)
    )
    result = cursor.fetchone()
    return result[0] if result else None

def get_all_titles() -> dict:
    """Get all thread IDs with their titles"""
    cursor = conn.execute("SELECT thread_id, title FROM conversation_metadata")
    return {row[0]: row[1] for row in cursor.fetchall()}
