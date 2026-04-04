import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_sudo_table():
    """Create sudo users table if not exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sudo_users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER UNIQUE NOT NULL,
            username   TEXT,
            added_by   INTEGER,
            added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_sudo(user_id: int, username: str, added_by: int) -> bool:
    """
    Add user to sudo list.
    Returns True if added, False if already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO sudo_users (user_id, username, added_by)
            VALUES (?, ?, ?)
        """, (user_id, username, added_by))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def remove_sudo(user_id: int) -> bool:
    """
    Remove user from sudo list.
    Returns True if removed, False if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM sudo_users WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def is_sudo(user_id: int) -> bool:
    """Check if user is in sudo list."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM sudo_users WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_all_sudos() -> list:
    """Return all sudo users as list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, added_at
        FROM sudo_users
        ORDER BY added_at ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "user_id"  : row[0],
            "username" : row[1] or "N/A",
            "added_at" : row[2]
        }
        for row in rows
    ]

def total_sudos() -> int:
    """Return total sudo users count."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sudo_users")
    count = cursor.fetchone()[0]
    conn.close()
    return count
