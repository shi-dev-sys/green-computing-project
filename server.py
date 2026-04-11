from flask import Flask, request, jsonify, render_template, session
import sqlite3
from energy import process_data
from energy_db import save_to_db

app = Flask(__name__)
app.secret_key = "greencomputing123"


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- ENERGY API ----------------
@app.route("/energy", methods=["POST"])
def energy_route():
    data = request.json

    cpu = data.get("cpu_usage", 0)
    hours = data.get("hours", 1)
    active = data.get("active_time", 0)
    idle = data.get("idle_time", 0)
    device = data.get("device", "unknown")  # ✅ NEW

    # Process energy
    result = process_data(cpu, hours, active, idle)

    # Add device to result
    result["device"] = device  # ✅ NEW

    # Save to database
    save_to_db(result)

    return jsonify(result)


# ---------------- LIVE DATA ----------------
@app.route("/live")
def live_data():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("""
        SELECT device, cpu, power, energy, co2, active_time, idle_time
        FROM energy_data
        ORDER BY rowid DESC LIMIT 1
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
            "idle_time": row[6]
        }

    return {
        "device": "No Data",
        "cpu_usage": 0,
        "power_watts": 0,
        "energy_kwh": 0,
        "co2_kg": 0,
        "active_time": 0,
        "idle_time": 0
    }


# ---------------- GRAPH DATA ----------------
@app.route("/graph")
def graph():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("""
        SELECT time, energy
        FROM energy_data
        ORDER BY rowid DESC LIMIT 10
    """)

    rows = c.fetchall()
    conn.close()

    rows.reverse()

    return jsonify({
        "labels": [r[0] for r in rows],
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
    return jsonify({"status": "logged out"})


# ---------------- CHECK LOGIN ----------------
@app.route("/check_login")
def check_login():
    if "user" in session:
        return jsonify({"logged_in": True})
    return jsonify({"logged_in": False})


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)