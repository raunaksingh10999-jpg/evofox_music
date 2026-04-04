import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_blacklist_table():
    """Create blacklisted chats table if not exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blacklisted_chats (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id    INTEGER UNIQUE NOT NULL,
            added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_bl_chat(chat_id: int) -> bool:
    """
    Add a chat to the blacklist.
    Returns True if added successfully, False if it was already blacklisted.
    """
    create_blacklist_table() # Ensure table exists
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO blacklisted_chats (chat_id)
            VALUES (?)
        """, (chat_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_all_bl_chats() -> list:
    """Return a list of all blacklisted chat_ids."""
    create_blacklist_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM blacklisted_chats ORDER BY added_at ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def is_chat_blacklisted(chat_id: int) -> bool:
    """Check if a chat is in the blacklist."""
    create_blacklist_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM blacklisted_chats WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def remove_bl_chat(chat_id: int) -> bool:
    """Remove a chat from blacklist."""
    create_blacklist_table()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM blacklisted_chats WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# Auto-create the table when this module is imported
create_blacklist_table()
