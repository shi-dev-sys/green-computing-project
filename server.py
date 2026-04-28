from flask import Flask, request, jsonify, render_template, session
import sqlite3
import smtplib
from email.mime.text import MIMEText

from energy import process_data
from energy_db import init_db, save_to_db

app = Flask(__name__)
app.secret_key = "greencomputing123"

# Initialize DB
init_db()

# Global states
latest_sleep = False
latest_alert = False


# ---------------- REAL EMAIL ALERT FUNCTION ----------------
def send_email_alert(power, energy, device):
    # Your Gmail
    sender_email = "greencomputingalerts@gmail.com"

    # Your 16-character Google App Password
    sender_password = "hskt ejbe iumw ggcw"

    # Receiver email (can be same as sender for testing)
    receiver = session.get("alert_email", sender_email)

    subject = "High Energy Usage Alert"

    body = f"""
⚠ High Energy Usage Alert

Device: {device}
Power Consumption: {power} W
Energy Used: {energy} kWh

System is consuming unusually high energy.
Please check the machine immediately.
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

        print("✅ Email alert sent successfully")

    except Exception as e:
        print("❌ Email sending failed:", e)


# ---------------- SET EMAIL (FROM UI) ----------------
@app.route("/set_email", methods=["POST"])
def set_email():
    data = request.json
    email = data.get("email")

    session["alert_email"] = email
    return jsonify({"status": "saved"})


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

    # 📧 REAL EMAIL ALERT (ONLY ON STATE CHANGE)
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


# ---------------- LIVE DATA (MULTI DEVICE) ----------------
@app.route("/live")
def live_data():
    conn = sqlite3.connect("energy.db")
    c = conn.cursor()

    c.execute("""
        SELECT device, cpu_usage, power_watts, energy_kwh, co2_kg,
               active_time, idle_time
        FROM energy_data
        WHERE id IN (
            SELECT MAX(id)
            FROM energy_data
            GROUP BY device
        )
        ORDER BY id DESC
    """)

    rows = c.fetchall()
    conn.close()

    devices = []

    for row in rows:
        devices.append({
            "device": row[0],
            "cpu_usage": row[1],
            "power_watts": row[2],
            "energy_kwh": row[3],
            "co2_kg": row[4],
            "active_time": row[5],
            "idle_time": row[6],
        })

    return jsonify({
        "devices": devices,
        "sleep": latest_sleep,
        "alert": latest_alert
    })


# ---------------- MULTI DEVICE GRAPH DATA ----------------
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
    devices_data = {}

    for row in rows:
        device = row[0]
        record_id = str(row[1])
        cpu = row[2]

        if record_id not in labels:
            labels.append(record_id)

        if device not in devices_data:
            devices_data[device] = []

        devices_data[device].append(cpu)

    return jsonify({
        "labels": labels,
        "devices": devices_data
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