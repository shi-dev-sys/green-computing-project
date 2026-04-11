def process_data(cpu_usage, hours, active_time=0, idle_time=0):
    """
    Calculates energy consumption and CO2 emissions
    based on CPU usage.
    """

    # Safety checks (VERY IMPORTANT to avoid crashes)
    if cpu_usage is None:
        cpu_usage = 0
    if hours is None:
        hours = 1

    # Energy calculation logic
    power = cpu_usage * 2
    energy = (power * hours) / 1000
    co2 = energy * 0.82

    return {
        "cpu_usage": cpu_usage,
        "power_watts": power,
        "energy_kwh": energy,
        "co2_kg": co2,
        "active_time": active_time,
        "idle_time": idle_time
    }