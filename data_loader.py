import requests
import pandas as pd
import numpy as np
import streamlit as st

BASE = "https://api.openf1.org/v1"

@st.cache_data(show_spinner=False)
def get_session_key(year: int, country: str, session_name: str = "Race"):
    r = requests.get(f"{BASE}/sessions", params={
        "year": year, "country_name": country, "session_name": session_name
    }, timeout=15)
    data = r.json()
    if not data or not isinstance(data, list) or len(data) == 0:
        return None
    return data[0].get("session_key")

@st.cache_data(show_spinner=False)
def get_drivers(session_key: int):
    r = requests.get(f"{BASE}/drivers", params={"session_key": session_key}, timeout=15)
    return pd.DataFrame(r.json())

@st.cache_data(show_spinner=False)
def get_laps(session_key: int, driver_number: int):
    r = requests.get(f"{BASE}/laps", params={
        "session_key": session_key, "driver_number": driver_number
    }, timeout=15)
    return pd.DataFrame(r.json())

@st.cache_data(show_spinner=False)
def get_weather(session_key: int):
    r = requests.get(f"{BASE}/weather", params={"session_key": session_key}, timeout=15)
    df = pd.DataFrame(r.json())
    if df.empty:
        return None
    return df.iloc[0]

@st.cache_data(show_spinner=False)
def get_lap_telemetry(session_key: int, driver_number: int, lap_number: int):
    laps = get_laps(session_key, driver_number)
    lap = laps[laps["lap_number"] == lap_number]
    if lap.empty:
        return None
    start = lap.iloc[0]["date_start"]

    next_lap = laps[laps["lap_number"] == lap_number + 1]
    if next_lap.empty:
        return None
    end = next_lap.iloc[0]["date_start"]

    r = requests.get(f"{BASE}/car_data", params={
        "session_key": session_key,
        "driver_number": driver_number,
        "date>": start,
        "date<": end,
    }, timeout=15)
    df = pd.DataFrame(r.json())
    if df.empty:
        return None
    df["brake_bool"] = df["brake"] > 0
    
    df["date"] = pd.to_datetime(df["date"], format='ISO8601')
    df["time_diff"] = df["date"].diff().dt.total_seconds().fillna(0)
    df["speed_ms"] = df["speed"] / 3.6
    df["distance"] = (df["speed_ms"] * df["time_diff"]).cumsum()
    
    loc_r = requests.get(f"{BASE}/location", params={
        "session_key": session_key,
        "driver_number": driver_number,
        "date>": start,
        "date<": end,
    }, timeout=15)
    loc_df = pd.DataFrame(loc_r.json())
    
    if not loc_df.empty:
        loc_df["date"] = pd.to_datetime(loc_df["date"], format='ISO8601')
        df = pd.merge_asof(df.sort_values('date'), loc_df[['date', 'x', 'y']].sort_values('date'), on='date', direction='nearest')

    return df
