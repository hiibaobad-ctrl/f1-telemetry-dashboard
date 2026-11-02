# F1 Telemetry Dashboard 🏎️

An interactive web application to compare Formula 1 driver telemetry (Speed, Throttle, Brake, Gear) and visualize track maps using real session data. 

## Features
- **Driver Comparison:** Compare any two drivers on any lap by distance.
- **Track Map:** Interactive circuit map colored by speed.
- **Weather Widget:** Live session weather data (Track/Air temp, humidity, rain).
- **No API Keys Required:** Powered entirely by the free OpenF1 API.

## Tech Stack
- Python
- Streamlit
- Plotly
- Pandas
- OpenF1 API

## How to run locally
1. Clone the repo: `git clone https://github.com/hiibaobad-ctrl/f1-telemetry-dashboard.git`
2. Create a virtual environment: `python -m venv venv`
3. Activate it (Windows): `.\venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the app: `streamlit run app.py`
