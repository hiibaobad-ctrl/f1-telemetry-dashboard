import streamlit as st
import plotly.graph_objects as go
from data_loader import get_session_key, get_drivers, get_laps, get_lap_telemetry, get_weather

st.set_page_config(page_title="F1 Telemetry Dashboard", layout="wide")

flag_svg = """
<svg width="40" height="40" viewBox="0 0 100 100" style="vertical-align: middle; margin-left: 15px;">
  <rect x="20" y="10" width="60" height="50" fill="#fff" stroke="#333" stroke-width="4"/>
  <path d="M20 10 h20 v16 h-20 z M60 10 h20 v16 h-20 z M40 26 h20 v16 h-20 z M80 26 h-20 v16 h-20 z M20 42 h20 v18 h-20 z M60 42 h20 v18 h-20 z" fill="#111"/>
  <line x1="20" y1="10" x2="20" y2="90" stroke="#888" stroke-width="6" stroke-linecap="round"/>
</svg>
"""

st.markdown(f"<h1 style='display: flex; align-items: center;'>F1 Telemetry Dashboard {flag_svg}</h1>", unsafe_allow_html=True)
st.caption("Compare driver telemetry by Distance (OpenF1)")

with st.sidebar:
    st.header("Session")
    year = st.selectbox("Year", [2026, 2025, 2024, 2023], index=0)
    
    # Changed to a dropdown with valid OpenF1 country names
    countries = ["Italy", "Mexico", "United States", "United Kingdom", "Monaco", "Belgium", "Singapore", "Japan", "Bahrain", "Australia", "Brazil", "Abu Dhabi"]
    country = st.selectbox("Country", countries, index=1) # Defaults to Mexico
    
    session_name = st.selectbox(
        "Session", ["Race", "Qualifying", "Sprint", "Practice 1", "Practice 2", "Practice 3"],
    )

sk = get_session_key(year, country, session_name)
if sk is None:
    st.error(f"Session not found for {year} {country} {session_name}. Try another round.")
    st.stop()

weather = get_weather(sk)
if weather is not None:
    st.sidebar.markdown("### Weather")
    st.sidebar.info(
        f"🌡️ **Air:** {weather.get('air_temperature', 'N/A')}°C  |  "
        f"Track: {weather.get('track_temperature', 'N/A')}°C\n\n"
        f"💧 **Humidity:** {weather.get('humidity', 'N/A')}%\n\n"
        f"🌬️ **Wind:** {weather.get('wind_speed', 'N/A')} m/s\n\n"
        f"🌧️ **Rain:** {'Yes' if weather.get('rainfall') == 1 else 'No'}"
    )

drivers = get_drivers(sk)
if drivers.empty:
    st.warning("No drivers found.")
    st.stop()

driver_options = {
    f"{row['name_acronym']} (#{row['driver_number']})": int(row["driver_number"])
    for _, row in drivers.iterrows()
}

col_d1, col_d2 = st.columns(2)
with col_d1:
    driver_label_1 = st.selectbox("Driver 1", list(driver_options.keys()), index=0)
    driver_num_1 = driver_options[driver_label_1]
    laps_1 = get_laps(sk, driver_num_1)
    lap_numbers_1 = sorted(laps_1["lap_number"].dropna().astype(int).tolist()) if not laps_1.empty else []
    lap_num_1 = st.selectbox("Lap (Driver 1)", lap_numbers_1, index=0) if lap_numbers_1 else None

with col_d2:
    driver_label_2 = st.selectbox("Driver 2", list(driver_options.keys()), index=1)
    driver_num_2 = driver_options[driver_label_2]
    laps_2 = get_laps(sk, driver_num_2)
    lap_numbers_2 = sorted(laps_2["lap_number"].dropna().astype(int).tolist()) if not laps_2.empty else []
    lap_num_2 = st.selectbox("Lap (Driver 2)", lap_numbers_2, index=0) if lap_numbers_2 else None

if not lap_num_1 or not lap_num_2:
    st.stop()

st.subheader(f"{driver_label_1} (Lap {lap_num_1}) vs {driver_label_2} (Lap {lap_num_2})")
placeholder = st.empty()

with placeholder.container():
    st.markdown("##### Speed")
    st.markdown('<div style="height: 350px; background-color: rgba(255,255,255,0.05); border-radius: 10px;"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### Throttle")
        st.markdown('<div style="height: 300px; background-color: rgba(255,255,255,0.05); border-radius: 10px;"></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("##### Brake")
        st.markdown('<div style="height: 300px; background-color: rgba(255,255,255,0.05); border-radius: 10px;"></div>', unsafe_allow_html=True)

tel_1 = get_lap_telemetry(sk, driver_num_1, lap_num_1)
tel_2 = get_lap_telemetry(sk, driver_num_2, lap_num_2)

if tel_1 is None or tel_2 is None:
    placeholder.empty()
    st.warning("No telemetry for one of the selected laps.")
    st.stop()

placeholder.empty()

c1 = "#E10600"
c2 = "#00C853"

fig_speed = go.Figure()
fig_speed.add_trace(go.Scatter(x=tel_1["distance"], y=tel_1["speed"], mode="lines", name=driver_label_1, line=dict(color=c1, width=2)))
fig_speed.add_trace(go.Scatter(x=tel_2["distance"], y=tel_2["speed"], mode="lines", name=driver_label_2, line=dict(color=c2, width=2, dash="dot")))
fig_speed.update_layout(title="Speed", xaxis_title="Distance (m)", yaxis_title="Speed (km/h)", height=350, margin=dict(l=40, r=20, t=40, b=40), hovermode="x unified")
st.plotly_chart(fig_speed, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    fig_throttle = go.Figure()
    fig_throttle.add_trace(go.Scatter(x=tel_1["distance"], y=tel_1["throttle"], mode="lines", name=driver_label_1, line=dict(color=c1)))
    fig_throttle.add_trace(go.Scatter(x=tel_2["distance"], y=tel_2["throttle"], mode="lines", name=driver_label_2, line=dict(color=c2, dash="dot")))
    fig_throttle.update_layout(title="Throttle", xaxis_title="Distance (m)", yaxis_title="Throttle (%)", height=300, yaxis=dict(range=[-5, 105]), margin=dict(l=40, r=20, t=40, b=40), hovermode="x unified")
    st.plotly_chart(fig_throttle, use_container_width=True)

with col2:
    fig_brake = go.Figure()
    fig_brake.add_trace(go.Scatter(x=tel_1["distance"], y=tel_1["brake_bool"].astype(int), mode="lines", name=driver_label_1, line=dict(color=c1, shape="hv"), fill="tozeroy", opacity=0.6))
    fig_brake.add_trace(go.Scatter(x=tel_2["distance"], y=tel_2["brake_bool"].astype(int), mode="lines", name=driver_label_2, line=dict(color=c2, shape="hv"), fill="tozeroy", opacity=0.6))
    fig_brake.update_layout(title="Brake", xaxis_title="Distance (m)", yaxis_title="Brake", height=300, yaxis=dict(range=[-0.1, 1.1]), margin=dict(l=40, r=20, t=40, b=40), hovermode="x unified")
    st.plotly_chart(fig_brake, use_container_width=True)

if 'x' in tel_1.columns and 'y' in tel_1.columns:
    st.subheader("Track Map")
    
    fig_map = go.Figure()
    fig_map.add_trace(go.Scatter(
        x=tel_1["x"], y=tel_1["y"], mode="markers", 
        marker=dict(size=4, color=tel_1["speed"], colorscale="Turbo", showscale=True), 
        name=driver_label_1
    ))
    fig_map.add_trace(go.Scatter(
        x=tel_1["x"], y=tel_1["y"], mode="lines", 
        line=dict(color="rgba(255,255,255,0.2)", width=2), 
        showlegend=False
    ))
    
    fig_map.update_layout(
        title="Track Map (Colored by Speed)", 
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        height=600, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_map, use_container_width=True)
