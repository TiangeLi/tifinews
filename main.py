from timezonefinder import TimezoneFinder

from modules.taskrunner import AsyncTaskRunner
from modules.emailsender import EmailSender
from modules.utils import get_lat_long
from modules.litterbot import LitterBot
from modules.bikes import Bikes
from modules.weather import get_weather_overview

from datetime import date
from pytz import timezone
import asyncio

from dotenv import load_dotenv
load_dotenv(override=True)

# Get working parameters (timezone, latlng, timezone)
tf = TimezoneFinder()
home_latlng = get_lat_long(HOME_ADDRESS)
work_latlng = get_lat_long(WORK_ADDRESS)
home_timezone = tf.timezone_at(lat=home_latlng[0], lng=home_latlng[1])
home_timezone = timezone(home_timezone)

# -------------------------------------
# Get the data and update email
async def refresh_data():
    litterbot = LitterBot()
    litterstatus = await litterbot.get_status_report(timezone=home_timezone)
    weather = get_weather_overview(latlng=home_latlng)
    bikes = Bikes()
    bikes_home = bikes.get_bikes_report(location=home_latlng)[:6]
    docks_work = bikes.get_docks_report(location=work_latlng)[:6]

    # Create the email
    email_client = EmailSender()
    email_data = {
            'greeting': f'Good morning TiFi! It\'s currently {date.today()}.',
            'bikesheaders': ['Location', 'Bikes', 'E-Bikes'],
            'bikesrows': bikes_home,
            'docksheaders': ['Location', 'Docks', 'Total Docks'],
            'docksrows': docks_work,
            'litterrobot': litterstatus.html(),
            'weather': weather
        }
    return email_client, email_data

async def main_task():
    email_client, email_data = await refresh_data()
    email_client.send_email(subject=EMAIL_SUBJECT, body=email_data, recipients=RECIPIENTS, debug=False)


# -------------------------------------
# main event loop
async def main():
    runner = AsyncTaskRunner(EMAIL_TIME, home_timezone)
    await runner.run_loop(main_task)

if __name__ == "__main__":
    print("Starting Tifi...")
    asyncio.run(main_task())  # cron job
    #asyncio.run(main())  # run loop
