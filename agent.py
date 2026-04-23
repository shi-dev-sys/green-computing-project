import requests
import time
import psutil
import socket

URL = "https://green-computing-project.onrender.com/energy"

device_name = socket.gethostname()

start_time = time.time()

# 🔥 Sleep Trigger Settings
IDLE_THRESHOLD = 10      # CPU % below this = idle
IDLE_LIMIT = 2           # 🔥 Trigger faster (~1 min since loop is 30 sec)
idle_count = 0

while True:
    try:
        # CPU usage (%)
        cpu_usage = psutil.cpu_percent(interval=1)

        # Runtime in hours
        hours = (time.time() - start_time) / 3600

        # Better interpretation
        active_time = cpu_usage / 100 * hours
        idle_time = hours - active_time

        # 🔥 Idle detection logic
        if cpu_usage < IDLE_THRESHOLD:
            idle_count += 1
        else:
            idle_count = 0

        # 🔥 Trigger condition
        sleep_triggered = False

        if idle_count >= IDLE_LIMIT:
            print("💤 Auto Sleep Trigger Activated!")
            sleep_triggered = True
            idle_count = 0

        # 📡 Send data to server
        data = {
            "device": device_name,
            "cpu_usage": cpu_usage,
            "hours": hours,
            "active_time": active_time,
            "idle_time": idle_time,
            "sleep_trigger": sleep_triggered   # NEW FIELD
        }

        response = requests.post(URL, json=data, timeout=30)

        print("Device:", device_name)
        print("Sent:", data)

        try:
            print("Received:", response.json())
        except:
            print("Server response not JSON:", response.text)

        print("-" * 40)

    except requests.exceptions.ConnectionError:
        print("❌ Server not reachable")

    except requests.exceptions.Timeout:
        print("❌ Request timed out")

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(30)