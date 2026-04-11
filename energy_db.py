def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # ❗ DROP OLD TABLE (IMPORTANT FIX)
    c.execute("DROP TABLE IF EXISTS energy_data")

    c.execute("""
    CREATE TABLE energy_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        cpu REAL,
        power REAL,
        energy REAL,
        co2 REAL,
        active_time REAL,
        idle_time REAL,
        device TEXT
    )
    """)

    conn.commit()
    conn.close()