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


def save_to_db(device, cpu_usage, hours, active_time, idle_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO energy_data (device, cpu_usage, hours, active_time, idle_time)
        VALUES (?, ?, ?, ?, ?)
    """, (device, cpu_usage, hours, active_time, idle_time))

    conn.commit()
    conn.close()