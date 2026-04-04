import sqlite3
import os

# --- Database file path ---
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DB_PATH)

def create_table():
    """Create users table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER UNIQUE NOT NULL,
            username    TEXT,
            first_name  TEXT,
            joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str, first_name: str):
    """
    Add a new user to the database.
    Skips if user already exists (no duplicates).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username, first_name))
        conn.commit()
    finally:
        conn.close()

def user_exists(user_id: int) -> bool:
    """Check if a user already exists in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def total_users() -> int:
    """Return total number of users in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count
