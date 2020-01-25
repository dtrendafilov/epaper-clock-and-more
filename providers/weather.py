# Original code: https://github.com/prehensile/waveshare-clock
# Modifications: https://github.com/pskowronek/epaper-clock-and-more, Apache 2 license

from .acquire import Acquire

import logging
import requests
import bisect
from collections import namedtuple


WeatherTuple = namedtuple('Weather', ['temp', 'temp_min', 'temp_max', 'icon',
    'summary', 'forecast_summary', 'nearest_storm_distance', 'alert_title',
    'alert_description', 'wind_speed', 'wind_gust', 'apparent_temp', 'beaufort', 'forecast'])


BEAUFORT_SCALE = (
        (1, 2),
        (3, 3),
        (5, 6),
        (7, 9),
        (10, 11),
        (12, 14),
        (15, 17),
        (19, 21),
        (23, 24),
        (27, 28),
        (31, 32),
        )

def beaufort_scale(speed, gust):
    return bisect.bisect_left(BEAUFORT_SCALE, (speed, gust))
    


class Weather(Acquire):


    DEFAULT = WeatherTuple(temp=-99, temp_min=-99, temp_max=-99, icon='n/a', summary='n/a',
                           forecast_summary='n/a', nearest_storm_distance=None, alert_title=None, alert_description=None,
                           wind_speed=-1, wind_gust=-1, apparent_temp=-1, beaufort=-1, forecast=[])


    def __init__(self, key, lat, lon, units, cache_ttl):
        self.key = key
        self.lat = lat
        self.lon = lon
        self.units = units
        self.cache_ttl = cache_ttl


    def cache_name(self):
        return "darksky.json"


    def ttl(self):
        return self.cache_ttl


    def acquire(self):
        logging.info("Getting a fresh forecast from the internet...")

        try:
            r = requests.get(
                "https://api.darksky.net/forecast/{}/{},{}".format(
                    self.key,
                    self.lat,
                    self.lon
                ),
                params = {
                    "units" : self.units,
                }
            )
            return r

        except Exception as e:
            logging.exception(e)

        return None


    def get(self):
        try:
            forecast_data = self.load()
            if forecast_data is None:
                return self.DEFAULT

            return self.compute_data(forecast_data)
        except Exception as e:
            logging.exception(e)
            return self.DEFAULT

    def forecast_day(self, day):
        return WeatherTuple(
            temp_min=day['temperatureMin'],
            temp_max=day['temperatureMax'],
            icon=day['icon'],
            summary=day['summary'],
            wind_speed=day['windSpeed'],
            wind_gust=day['windGust'],
            beaufort=beaufort_scale(day['windSpeed'], day['windGust']),
            temp=None,
            forecast_summary=None,
            nearest_storm_distance=None,
            alert_title=None,
            alert_description=None,
            apparent_temp=None,
            forecast = None,
        )



    def compute_data(self, forecast_data):
        days = forecast_data['daily']['data']
        d = days[0]

        temp_min = d['temperatureMin']
        temp_max = d['temperatureMax']

        c = forecast_data['currently']
        a = forecast_data.get('alerts', None)

        forecast = [ self.forecast_day(d) for d in days[1:4] ]

        return WeatherTuple(
            temp=c['temperature'],
            temp_min=temp_min,
            temp_max=temp_max,
            icon=d['icon'],
            summary=c['summary'],
            forecast_summary=forecast_data['daily']['summary'],
            nearest_storm_distance=c.get('nearestStormDistance', None),
            alert_title=a[0]['title'] if a is not None else None,
            alert_description=a[0]['description'] if a is not None else None,
            wind_speed=c['windSpeed'],
            wind_gust=c['windGust'],
            apparent_temp=c['apparentTemperature'],
            beaufort=beaufort_scale(c['windSpeed'], c['windGust']),
            forecast = forecast,
        )


if __name__ == '__main__':
    import sys
    import json
    with open(sys.argv[1]) as f:
        data = json.load(f)
    weather = Weather(None, None, None, None, None)
    print(json.dumps(weather.compute_data(data), indent=4))

