import os
import json
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import requests


# ──────────────────────────────────────────────
# Configuration — add/remove locations here
# ──────────────────────────────────────────────
LOCATIONS = [
    {
        "name": "Golden, BC",
        "latitude": 51.30,
        "longitude": -116.66,
    },
    {
        "name": "Radium Hot Springs, BC",
        "latitude": 51.06,
        "longitude": -115.94,
    },
    {
        "name": "Cranbrook, BC",
        "latitude": 49.61,
        "longitude": -115.78,
    },
]

THRESHOLD_C = -15          # Alert if daily minimum drops below this
FORECAST_DAYS = 5           # How many days ahead to check


# ──────────────────────────────────────────────
# Email helpers (placeholder — wire up SMTP later)
# ──────────────────────────────────────────────
def send_alert_email(alerts):
    """Send an email alert. Currently prints instead of sending."""

    # In the future, pull these from GitHub Secrets:
    email_from = os.environ.get("EMAIL_FROM", "placeholder@example.com")
    email_to   = os.environ.get("EMAIL_TO",   "placeholder@example.com")
    smtp_host  = os.environ.get("SMTP_SERVER", "smtp.placeholder.com")
    smtp_port  = int(os.environ.get("SMTP_PORT", "587"))

    subject = f"Cold Weather Alert: {len(alerts)} location(s) below {THRESHOLD_C}°C"

    body_lines = [f"Cold weather alert — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"]
    for a in alerts:
        body_lines.append(f"\nLocation : {a['name']}")
        body_lines.append(f"Min Temp : {a['min_temp']:.1f}°C on {a['date']}")
        body_lines.append(f"Max Temp : {a.get('max_temp', 'N/A')}°C")

    body = "\n".join(body_lines)

    msg = MIMEMultipart()
    msg["From"]    = email_from
    msg["To"]      = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # ── PLACEHOLDER: print instead of sending ──
    print("=" * 60)
    print("ALERT EMAIL (placeholder — not actually sent):")
    print("-" * 60)
    print(msg.as_string())
    print("=" * 60)

    # TODO: Uncomment and fill in real SMTP details when ready:
    # with smtplib.SMTP(smtp_host, smtp_port) as server:
    #     server.starttls()
    #     # server.login(user, password)   # add EMAIL_USER / EMAIL_PASS secrets
    #     server.send_message(msg)


# ──────────────────────────────────────────────
# Open-Meteo API
# ──────────────────────────────────────────────
def fetch_forecast(lat, lon):
    """Fetch daily forecast from Open-Meteo for a single location."""

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":      lat,
        "longitude":     lon,
        "daily":         "temperature_2m_min,temperature_2m_max",
        "timezone":      "auto",
        "forecast_days": FORECAST_DAYS,
    }

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ──────────────────────────────────────────────
# Core logic
# ──────────────────────────────────────────────
def check_location(loc):
    """Return a list of alert dicts for this location (empty = no alerts)."""

    data = fetch_forecast(loc["latitude"], loc["longitude"])

    dates   = data["daily"]["time"]
    temps_min = data["daily"]["temperature_2m_min"]
    temps_max = data["daily"]["temperature_2m_max"]

    alerts = []
    for d, tmin, tmax in zip(dates, temps_min, temps_max):
        if tmin is not None and tmin < THRESHOLD_C:
            alerts.append({
                "name":     loc["name"],
                "date":     d,
                "min_temp": round(tmin, 1),
                "max_temp": round(tmax, 1) if tmax is not None else None,
            })

    return alerts


def main():
    print(f"Checking cold weather forecast (threshold: {THRESHOLD_C}°C, window: {FORECAST_DAYS} days)\n")

    all_alerts = []

    for loc in LOCATIONS:
        alerts = check_location(loc)
        if alerts:
            print(f"[ALERT] {loc['name']}: {len(alerts)} day(s) below threshold")
            for a in alerts:
                print(f"         {a['date']:12s}  min={a['min_temp']}°C  max={a.get('max_temp', 'N/A')}°C")
        else:
            print(f"[OK]     {loc['name']}: no days below threshold in next {FORECAST_DAYS} days")

        all_alerts.extend(alerts)

    # Only email if there are actual alerts
    if all_alerts:
        send_alert_email(all_alerts)
        print(f"\nAlert sent for {len(all_alerts)} day(s).")
    else:
        print("\nNo cold weather alerts — nothing to report.")


if __name__ == "__main__":
    main()
