import sqlite3

def save_to_db(data):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    # ✅ Updated table with device column
    c.execute("""
    CREATE TABLE IF NOT EXISTS energy_data (
        device TEXT,
        cpu REAL,
        power REAL,
        energy REAL,
        co2 REAL,
        active_time REAL,
        idle_time REAL,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ✅ Insert data including device
    c.execute("""
    INSERT INTO energy_data (device, cpu, power, energy, co2, active_time, idle_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["device"],
        data["cpu_usage"],
        data["power_watts"],
        data["energy_kwh"],
        data["co2_kg"],
        data["active_time"],
        data["idle_time"]
    ))

    conn.commit()
    conn.close()