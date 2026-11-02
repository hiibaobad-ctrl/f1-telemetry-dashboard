from data_loader import get_session_key, get_drivers, get_laps, get_lap_telemetry

sk = get_session_key(2024, "Italy", "Race")
print("session_key:", sk)

drivers = get_drivers(sk)
print(drivers[["driver_number", "name_acronym"]].head())

laps = get_laps(sk, 1)
print(laps[["lap_number", "lap_duration"]].head())

tel = get_lap_telemetry(sk, 1, 1)
print(tel[["speed", "throttle", "brake_bool", "n_gear"]].head())
print("max speed:", tel["speed"].max())
