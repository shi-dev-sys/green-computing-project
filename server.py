from flask import Flask, request, jsonify, render_template, session
import sqlite3

from energy import process_data
from energy_db import init_db, save_to_db

app = Flask(__name__)
app.secret_key = "greencomputing123"

# Initialize DB
init_db()

# Global states
latest_sleep = False
latest_alert = False


# ---------------- SET EMAIL (FROM UI) ----------------
@app.route("/set_email", methods=["POST"])
def set_email():
    data = request.json
    email = data.get("email")

    session["alert_email"] = email
    return jsonify({"status": "saved"})


# ---------------- EMAIL SIMULATION FUNCTION ----------------
def send_email_alert(power, energy, device):
    receiver = session.get("alert_email", "no-email-set")

    print("\n📧 ================= EMAIL ALERT =================")
    print(f"To: {receiver}")
    print(f"Device: {device}")
    print(f"Power: {power} W")
    print(f"Energy: {energy} kWh")
    print("⚠️ High energy usage detected!")
    print("================================================\n")


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- ENERGY API ----------------
@app.route("/energy", methods=["POST"])
def energy_route():
    global latest_sleep, latest_alert

    data = request.json

    cpu = data.get("cpu_usage", 0)
    hours = data.get("hours", 1)
    active = data.get("active_time", 0)
    idle = data.get("idle_time", 0)
    device = data.get("device", "unknown")

    # 💤 Sleep trigger
    latest_sleep = data.get("sleep_trigger", False)

    # ⚡ Process energy
    result = process_data(cpu, hours, active, idle)
    result["device"] = device

    power = result.get("power_watts", 0)
    energy = result.get("energy_kwh", 0)
    co2 = result.get("co2_kg", 0)

    # 🔥 ALERT LOGIC
    HIGH_POWER_THRESHOLD = 70
    HIGH_ENERGY_THRESHOLD = 0.1

    previous_alert = latest_alert

    high_usage = False
    if power > HIGH_POWER_THRESHOLD or energy > HIGH_ENERGY_THRESHOLD:
        high_usage = True

    latest_alert = high_usage

    # 📧 SIMULATED EMAIL (ONLY ON STATE CHANGE)
    if high_usage and not previous_alert:
        send_email_alert(power, energy, device)

    # send to frontend
    result["high_usage"] = high_usage

    # 💾 SAVE TO DATABASE
    save_to_db(
        device,
        cpu,
        hours,
        active,
        idle,
        power,
        energy,
        co2
    )

    return jsonify(result)


# ---------------- LIVE DATA ----------------
@app.route("/live")
def live_data():
    conn = sqlite3.connect("energy.db")
    c = conn.cursor()

    c.execute("""
        SELECT device, cpu_usage, power_watts, energy_kwh, co2_kg, active_time, idle_time
        FROM energy_data
        ORDER BY id DESC LIMIT 1
    """)

    row = c.fetchone()
    conn.close()

    if row:
        return {
            "device": row[0],
            "cpu_usage": row[1],
            "power_watts": row[2],
            "energy_kwh": row[3],
            "co2_kg": row[4],
            "active_time": row[5],
            "idle_time": row[6],
            "sleep": latest_sleep,
            "alert": latest_alert
        }

    return {
        "device": "No Data",
        "cpu_usage": 0,
        "power_watts": 0,
        "energy_kwh": 0,
        "co2_kg": 0,
        "active_time": 0,
        "idle_time": 0,
        "sleep": False,
        "alert": False
    }


# ---------------- GRAPH DATA ----------------
@app.route("/graph")
def graph():
    conn = sqlite3.connect("energy.db")
    c = conn.cursor()

    c.execute("""
        SELECT id, cpu_usage
        FROM energy_data
        ORDER BY id DESC LIMIT 10
    """)

    rows = c.fetchall()
    conn.close()

    rows.reverse()

    return jsonify({
        "labels": [str(r[0]) for r in rows],
        "values": [r[1] for r in rows]
    })


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "1234":
        session["user"] = username
        return jsonify({"status": "success"})

    return jsonify({"status": "failed"})


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("alert_email", None)
    return jsonify({"status": "logged out"})


# ---------------- CHECK LOGIN ----------------
@app.route("/check_login")
def check_login():
    if "user" in session:
        return jsonify({"logged_in": True})
    return jsonify({"logged_in": False})


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)