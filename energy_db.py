import sqlite3
from datetime import datetime

def save_to_db(data):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    # Create table (runs only once safely)
    c.execute("""
        CREATE TABLE IF NOT EXISTS energy_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu REAL,
            power REAL,
            energy REAL,
            co2 REAL,
            active_time REAL,
            idle_time REAL,
            time TEXT
        )
    """)

    # Insert data into table
    c.execute("""
        INSERT INTO energy_data (
            cpu, power, energy, co2, active_time, idle_time, time
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("cpu_usage"),
        data.get("power_watts"),
        data.get("energy_kwh"),
        data.get("co2_kg"),
        data.get("active_time"),
        data.get("idle_time"),
        datetime.now().strftime("%H:%M:%S")
    ))

    conn.commit()
    conn.close()