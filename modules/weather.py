from httpx import request
from os import getenv
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = getenv('WEATHER_API_KEY')

def get_weather_overview(latlng):
    url = 'https://api.openweathermap.org/data/3.0/onecall/overview'
    response = request('GET', url, params={
        'units': 'metric',
        'lang': 'en',
        'appid': WEATHER_API_KEY,
        'lat': str(latlng[0]),
        'lon': str(latlng[1]),
    })
    return response.json()['weather_overview'].replace('in our area', 'at 620 Bathurst St.')