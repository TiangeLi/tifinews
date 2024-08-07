from httpx import request
from os import getenv
from dotenv import load_dotenv
load_dotenv()

GEOCODE_MAPS_APIKEY = getenv("GEOCODE_MAPS_APIKEY")

def get_lat_long(address: str):
    url = 'https://geocode.maps.co/search'
    response = request('GET', url, params={
        'q': address,
        'api_key': GEOCODE_MAPS_APIKEY})
    response = response.json()
    lat = float(response[0]['lat'])
    lon = float(response[0]['lon'])
    return (lat, lon)