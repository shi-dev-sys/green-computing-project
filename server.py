from flask import Flask, request, jsonify, render_template, session
import sqlite3
import smtplib
from email.mime.text import MIMEText

from energy import process_data
from energy_db import init_db, save_to_db

app = Flask(__name__)
app.secret_key = "greencomputing123"

# ========================
# INIT DB (ONLY ONCE)
# ========================
init_db()

# ========================
# GLOBAL STATES
# ========================
latest_sleep = False
latest_alert = False

# Store email globally (IMPORTANT FIX)
ALERT_EMAIL = None


# ========================
# EMAIL ALERT FUNCTION
# ========================
def send_email_alert(power, energy, device):
    global ALERT_EMAIL

    sender_email = "greencomputingalerts@gmail.com"
    sender_password = "hskt ejbe iumw ggcw"

    receiver = ALERT_EMAIL or sender_email

    subject = "⚠ High Energy Usage Alert"

    body = f"""
High Energy Alert 🚨

Device: {device}
Power: {power} W
Energy: {energy} kWh

Please check system immediately.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()

        print("✅ Email sent")

    except Exception as e:
        print("❌ Email failed:", e)


# ========================
# SET EMAIL (FIXED)
# ========================
@app.route("/set_email", methods=["POST"])
def set_email():
    global ALERT_EMAIL

    data = request.json
    ALERT_EMAIL = data.get("email")

    return jsonify({"status": "saved"})


# ========================
# HOME
# ========================
@app.route("/")
def home():
    return render_template("index.html")


# ========================
# ENERGY PROCESSING
# ========================
@app.route("/energy", methods=["POST"])
def energy_route():
    global latest_sleep, latest_alert

    data = request.json

    cpu = data.get("cpu_usage", 0)
    hours = data.get("hours", 1)
    active = data.get("active_time", 0)
    idle = data.get("idle_time", 0)
    device = data.get("device", "unknown")

    latest_sleep = data.get("sleep_trigger", False)

    result = process_data(cpu, hours, active, idle)
    result["device"] = device

    power = result.get("power_watts", 0)
    energy = result.get("energy_kwh", 0)
    co2 = result.get("co2_kg", 0)

    # Alert logic
    HIGH_POWER = 70
    HIGH_ENERGY = 0.1

    prev = latest_alert
    latest_alert = (power > HIGH_POWER or energy > HIGH_ENERGY)

    # send email ONLY on transition
    if latest_alert and not prev:
        send_email_alert(power, energy, device)

    result["high_usage"] = latest_alert

    save_to_db(device, cpu, hours, active, idle, power, energy, co2)

    return jsonify(result)


# ========================
# LIVE DATA
# ========================
@app.route("/live")
def live_data():
    conn = sqlite3.connect("energy.db")
    c = conn.cursor()

    c.execute("""
        SELECT device, cpu_usage, power_watts, energy_kwh, co2_kg,
               active_time, idle_time
        FROM energy_data
        WHERE id IN (
            SELECT MAX(id) FROM energy_data GROUP BY device
        )
        ORDER BY id DESC
    """)

    rows = c.fetchall()
    conn.close()

    devices = []

    for r in rows:
        devices.append({
            "device": r[0],
            "cpu_usage": r[1],
            "power_watts": r[2],
            "energy_kwh": r[3],
            "co2_kg": r[4],
            "active_time": r[5],
            "idle_time": r[6]
        })

    return jsonify({
        "devices": devices,
        "sleep": latest_sleep,
        "alert": latest_alert
    })


# ========================
# GRAPH DATA
# ========================
@app.route("/graph")
def graph():
    conn = sqlite3.connect("energy.db")
    c = conn.cursor()

    c.execute("""
        SELECT device, id, cpu_usage
        FROM energy_data
        ORDER BY id DESC
        LIMIT 30
    """)

    rows = c.fetchall()
    conn.close()

    rows.reverse()

    labels = []
    devices = {}

    for r in rows:
        device = r[0]
        rid = str(r[1])
        cpu = r[2]

        labels.append(rid)

        if device not in devices:
            devices[device] = []

        devices[device].append(cpu)

    return jsonify({
        "labels": labels,
        "devices": devices
    })


# ========================
# LOGIN
# ========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if data["username"] == "admin" and data["password"] == "1234":
        session["user"] = "admin"
        return jsonify({"status": "success"})

    return jsonify({"status": "failed"})


# ========================
# LOGOUT
# ========================
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"status": "logged out"})


# ========================
# CHECK LOGIN
# ========================
@app.route("/check_login")
def check_login():
    return jsonify({"logged_in": "user" in session})


# ========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)