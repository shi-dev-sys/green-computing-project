 # redeploy trigger
from flask import Flask, request, jsonify, render_template, session
import sqlite3

from energy import process_data
from energy_db import init_db, save_to_db

app = Flask(__name__)
app.secret_key = "greencomputing123"

# 🧱 Initialize DB
init_db()


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
    device = data.get("device", "unknown")

    # 🔥 PUT THIS HERE (IMPORTANT PART)
    result = process_data(cpu, hours, active, idle)

    result["device"] = device

    power = result.get("power_watts", 0)
    energy = result.get("energy_kwh", 0)
    co2 = result.get("co2_kg", 0)

    # 💾 NOW SAVE TO DATABASE (after this)
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
        SELECT device, cpu_usage, hours, active_time, idle_time
        FROM energy_data
        ORDER BY id DESC LIMIT 1
    """)

    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({
            "device": row[0],
            "cpu_usage": row[1],
            "hours": row[2],
            "active_time": row[3],
            "idle_time": row[4]
        })

    return jsonify({
        "device": "No Data",
        "cpu_usage": 0,
        "hours": 0,
        "active_time": 0,
        "idle_time": 0
    })


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