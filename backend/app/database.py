import sqlite3
import os
from .logger import logger

DB_FILE = "todos.db"

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Dumps an error log if connection fails.
    """
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error("db_connection_failed", details={"error": str(e), "type": "db_error"})
        raise e

def init_db():
    """
    Initializes the Todo table.
    """
    try:
        conn = get_db_connection()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)) DEFAULT 0
                )
            """)
        conn.close()
        logger.info("db_initialized", db_file=DB_FILE)
    except Exception as e:
        logger.critical("db_initialization_failed", details={"error": str(e)})

# Initialize on module load (simple approach) or call from main
init_db()
