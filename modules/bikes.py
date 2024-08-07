import pybikes
import haversine
from datetime import datetime, timedelta
from pydantic import BaseModel

class Station(BaseModel):
    name: str
    last_updated_time: str
    free_normal_bikes: int
    free_ebikes: int
    free_docks: int
    total_docks: int
    distance: int

class Bikes(object):
    def __init__(self, bikeshare_name='bixi-toronto'):
        self.bikeshare = pybikes.get(bikeshare_name)
        self.last_updated_time = datetime.fromtimestamp(0)
        self.min_update_interval = timedelta(minutes=1)

    def update(self):
        now = datetime.now()
        difference = now - self.last_updated_time
        if difference >= self.min_update_interval:
            self.bikeshare.update()
            self.last_updated_time = now        
    
    def get_closest_stations(self, location, radius_m=500):
        self.update()
        stations = [
            Station(
                name=station.name,
                last_updated_time=datetime.fromtimestamp(station.extra['last_updated']).strftime('%H:%M:%S'),
                free_normal_bikes=station.extra['normal_bikes'],
                free_ebikes=station.extra['ebikes'],
                free_docks=station.free,
                total_docks=station.extra['slots'],
                distance=haversine.haversine(location, (station.latitude, station.longitude), unit=haversine.Unit.METERS)
            ) for station in self.bikeshare.stations if haversine.haversine(location, (station.latitude, station.longitude), unit=haversine.Unit.METERS) < radius_m
        ]
        return sorted(stations, key=lambda x: x.distance)
    
    def get_bikes_report(self, location, radius_m=500):
        stations = self.get_closest_stations(location, radius_m)
        return [[station.name, station.free_normal_bikes, station.free_ebikes] for station in stations]
    
    def get_docks_report(self, location, radius_m=500):
        stations = self.get_closest_stations(location, radius_m)
        return [[station.name, station.free_docks, station.total_docks] for station in stations]