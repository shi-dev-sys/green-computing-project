import sqlite3

DB_NAME = "energy.db"


# 🔌 DB connection
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


# 🧱 Create table (FULL STRUCTURE - FORCE RESET)
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 🔥 VERY IMPORTANT: delete old table
    cursor.execute("DROP TABLE IF EXISTS energy_data")

    # 🔥 create new table with correct columns
    cursor.execute("""
    CREATE TABLE energy_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device TEXT,
        cpu_usage REAL,
        hours REAL,
        active_time REAL,
        idle_time REAL,
        power_watts REAL,
        energy_kwh REAL,
        co2_kg REAL
    )
    """)

    conn.commit()
    conn.close()


# 💾 Insert data into database
def save_to_db(device, cpu_usage, hours, active_time, idle_time,
               power_watts, energy_kwh, co2_kg):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO energy_data (
            device, cpu_usage, hours, active_time, idle_time,
            power_watts, energy_kwh, co2_kg
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        device, cpu_usage, hours, active_time, idle_time,
        power_watts, energy_kwh, co2_kg
    ))

    conn.commit()
    conn.close()
