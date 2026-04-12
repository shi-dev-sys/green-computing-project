def process_data(cpu_usage, hours, active_time=0, idle_time=0):
    """
    Calculates energy consumption and CO2 emissions
    based on CPU usage.
    """

    # 🔒 Safety checks
    if cpu_usage is None:
        cpu_usage = 0
    if hours is None:
        hours = 1

    # ⚡ Energy calculation logic
    # (simple green computing model)
    power_watts = cpu_usage * 2

    energy_kwh = (power_watts * hours) / 1000

    co2_kg = energy_kwh * 0.82

    # 📦 Return structured data
    return {
        "cpu_usage": cpu_usage,
        "power_watts": power_watts,
        "energy_kwh": energy_kwh,
        "co2_kg": co2_kg,
        "active_time": active_time,
        "idle_time": idle_time
    }