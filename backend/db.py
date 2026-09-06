import sqlite3


def get_db():
    conn = sqlite3.connect("vayunetra.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pollution_type TEXT,
            severity INTEGER,
            confidence FLOAT,
            lat REAL,
            lon REAL,
            image_url TEXT,
            is_spam BOOLEAN
        )
    """)
    conn.commit()
