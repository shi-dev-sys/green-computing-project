import requests
import time
import psutil

# Flask server URL
URL = "http://127.0.0.1:5000/energy"

# ⏱️ Start time for calculating runtime hours
start_time = time.time()

while True:
    try:
        # CPU usage (%)
        cpu_usage = psutil.cpu_percent(interval=1)

        # CPU time breakdown (%)
        cpu_times = psutil.cpu_times_percent()

        # ⏱️ REAL RUNNING HOURS
        hours = (time.time() - start_time) / 3600

        # ⏱️ IDLE TIME IN HOURS (converted from % approximation)
        idle_hours = hours * (cpu_times.idle / 100)

        # Data packet sent to Flask
        data = {
            "cpu_usage": cpu_usage,
            "hours": hours,
            "active_time": cpu_times.user + cpu_times.system,
            "idle_time": idle_hours
        }

        # Send request to server
        response = requests.post(URL, json=data, timeout=5)

        print("Sent:", data)

        # Safe response handling
        try:
            print("Received:", response.json())
        except:
            print("Server response not JSON:", response.text)

        print("-" * 40)

    except requests.exceptions.ConnectionError:
        print("❌ Server not running")

    except requests.exceptions.Timeout:
        print("❌ Request timed out")

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(5)
