import fastf1
import os

# FastF1 caches data locally — this makes repeat loads MUCH faster
os.makedirs("f1_cache", exist_ok=True)
fastf1.Cache.enable_cache("f1_cache")

# Load a 2024 race session
session = fastf1.get_session(2024, "Monza", "R")
session.load(telemetry=True, weather=False, messages=False)

# Get Verstappen's fastest lap
lap = session.laps.pick_drivers("VER").pick_fastest()
print(f"Driver: {lap['Driver']}")
print(f"Lap time: {lap['LapTime']}")
print(f"Compound: {lap['Compound']}")

# Get telemetry
tel = lap.get_telemetry()
print(tel[["Distance", "Speed", "Throttle", "Brake", "nGear"]].head())
print(f"Telemetry rows: {len(tel)}")
