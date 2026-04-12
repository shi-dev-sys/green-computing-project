import sqlite3

DB_NAME = "energy.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS energy_data")

    cursor.execute("""
        CREATE TABLE energy_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT,
            cpu_usage REAL,
            hours REAL,
            active_time REAL,
            idle_time REAL
        )
    """)

    conn.commit()
    conn.close()