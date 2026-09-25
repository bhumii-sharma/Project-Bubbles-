import os
import sqlite3
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "bubbles_memory.db"
)


def get_connection(db_path=None):
    """Returns a SQLite database connection, ensuring data directory exists."""
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return sqlite3.connect(path)


def init_db(db_path=None):
    """Creates the necessary tables for persistent memory if they do not exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # User Profile (Name, Nickname, Preferences)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Long-Term Memories (Life events, struggles, goals, favorites)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            importance INTEGER DEFAULT 3
        )
    """)

    # Conversation History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            mood TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_profile_value(key, default=None, db_path=None):
    """Retrieves a single setting or profile value from the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default


def set_profile_value(key, value, db_path=None):
    """Saves or updates a profile value in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_profile (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
    """, (key, str(value)))
    conn.commit()
    conn.close()


def save_memory(category, content, importance=3, db_path=None):
    """Saves an important event, preference, or emotional memory."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memories (category, content, importance)
        VALUES (?, ?, ?)
    """, (category, content, importance))
    conn.commit()
    conn.close()


def get_recent_memories(limit=8, db_path=None):
    """Retrieves the most recent important memories."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, category, content FROM memories
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"timestamp": r[0], "category": r[1], "content": r[2]} for r in rows]


def save_conversation_turn(sender, message, mood=None, db_path=None):
    """Logs a single message in the conversation history."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (sender, message, mood)
        VALUES (?, ?, ?)
    """, (sender, message, mood))
    conn.commit()
    conn.close()


def get_recent_conversation(limit=6, db_path=None):
    """Retrieves the last N messages from conversation history."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message, mood FROM conversations
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    # Reverse so they appear in chronological order
    rows.reverse()
    return [{"sender": r[0], "message": r[1], "mood": r[2]} for r in rows]


def format_memory_context(db_path=None):
    """
    Constructs a formatted summary of user profile, long-term memories,
    and recent dialogue for prompt injection.
    """
    memories = get_recent_memories(limit=5, db_path=db_path)
    recent_chat = get_recent_conversation(limit=6, db_path=db_path)

    sections = []

    if memories:
        memory_lines = [f"- [{m['category'].upper()}] {m['content']}" for m in memories]
        sections.append("LONG-TERM MEMORIES OF YOUR HUMAN:\n" + "\n".join(memory_lines))

    if recent_chat:
        chat_lines = [f"{c['sender']}: {c['message']}" for c in recent_chat]
        sections.append("RECENT CONVERSATION HISTORY:\n" + "\n".join(chat_lines))

    return "\n\n".join(sections)
