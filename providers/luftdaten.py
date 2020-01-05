# Original code: https://github.com/prehensile/waveshare-clock
# Modifications: https://github.com/pskowronek/epaper-clock-and-more, Apache 2 license

from .acquire import Acquire

import logging
import requests
from collections import namedtuple, defaultdict


LuftdatenData = namedtuple('LuftdatenData', ['pm25', 'pm10', 'humidity', 'pressure', 'temperature', 'aqi', 'level', 'advice'])


class Luftdaten(Acquire):


    DEFAULT = LuftdatenData(pm25=-1, pm10=-1, pressure=-1, humidity=-1, temperature=None, aqi=-1, level='n/a', advice='n/a')


    def __init__(self, lat, lon, cache_ttl):
        self.lat = lat
        self.lon = lon
        self.cache_ttl = cache_ttl
        self.sensor = '5708'
        self.sensor2 = '5709'
        self.r2 = None


    def cache_name(self):
        return "luftdaten.json"


    def ttl(self):
        return self.cache_ttl


    def acquire(self):
        logging.info("Getting a Luftdaten.info status from the internet...")

        try:
            self.r2 = requests.get(
                    "http://api.luftdaten.info/v1/sensor/{0}/".format(self.sensor2),
                    headers = {
                        "Accept-Language" : "en",
                        "Accept" : "application/json"
                        }
            )
            r = requests.get(
                    "http://api.luftdaten.info/v1/sensor/{0}/".format(self.sensor),
                    headers = {
                        "Accept-Language" : "en",
                        "Accept" : "application/json"
                        }
            )
            return r
        except Exception as e:
            logging.exception(e)

        return None

    def update_data(self, data, result):
        for row in data:
            for r in row['sensordatavalues']:
                result[r['value_type']] += float(r['value']) / len(data)
                

    def get(self):
        try:
            data = self.load()
            if data is None:
                return self.DEFAULT

            d = defaultdict(float)
            self.update_data(data, d)
            if self.r2 != None:
                self.update_data(self.r2.json(), d)


            return LuftdatenData(
                pm25=d.get('P2', -1),
                pm10=d.get('P1', -1),
                pressure=d.get('pressure', -1),
                humidity=d.get('humidity', -1),
                temperature=d.get('temperature', -1),
                aqi=-1,
                level=-1,
                advice=-1,
            )

        except Exception as e:
            logging.exception(e)
            return self.DEFAULT


