# Cold Weather Alert Checker

Periodically checks open-meteo weather forecasts for cold temperature alerts across rural BC locations, and sends email notifications when thresholds are breached.

## How It Works

1. **Runs twice daily** via GitHub Actions (cron-scheduled at ~8 AM and ~8 PM)
2. **Fetches 5-day forecast** from [Open-Meteo](https://open-meteo.com/) (free, no API key needed)
3. **Checks minimum temperatures** — alerts if any day drops below the configured threshold (-15°C by default)
4. **Sends email alert** via SMTP when a cold event is detected

## File Structure

`
.github/workflows/cold-check.yml   # GitHub Actions workflow (schedule + job definition)
check_cold.py                      # Python script — fetches weather, checks thresholds, sends email
`

## Setup Steps

### 1. Create this repository on GitHub and push the code here

### 2. Configure Email (when ready to go live)

Add these as **GitHub Repository Secrets** (Settings → Secrets → Actions):

| Secret Name      | Description                                      |
|------------------|--------------------------------------------------|
| EMAIL_FROM     | Your email address (e.g., yourname@gmail.com)   |
| EMAIL_TO       | Recipient(s), comma-separated                    |
| SMTP_SERVER    | SMTP host (e.g., smtp.gmail.com)                 |
| SMTP_PORT      | Port (587 for TLS, 465 for SSL)                  |
| EMAIL_USER     | Email username / full address                     |
| EMAIL_PASSWORD | App password or SMTP credential                   |

### 3. Customize Locations & Thresholds

Edit check_cold.py:

- **Add/remove locations** in the LOCATIONS list — just add name, latitude, longitude
- **Change threshold** by editing THRESHOLD_C = -15
- **Adjust forecast window** with FORECAST_DAYS = 5

### 4. Test Manually

From GitHub: go to Actions → "Cold Weather Alert Check" → click **"Run workflow"** (green button)

Or locally:
`ash
pip install requests
python check_cold.py
`

## Future Enhancements

- [ ] Wind chill threshold support
- [ ] Configurable per-location thresholds
- [ ] Email only once per alert (avoid duplicate emails on consecutive runs)
- [ ] Support for additional weather variables (snowfall, wind speed, etc.)
- [ ] Slack/Teams webhook notifications
