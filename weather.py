import pyowm

import my_read
from wiki_search import Wiki

token = my_read.read_weather_token()


class Weather:
    def __init__(self):
        self.minimize = False
        self.suggest = None
        self.town = None
        self.status = None
        self.icon = None
        self.wind = None
        self.temperature = None  # (curretn, max, min)
        self.humidity = None
        self.pressure = None
        self.own = pyowm.OWM(API_key=token, language='RU')

    def get_weather(self, town: str, wiki: Wiki = None):
        self.suggest = None
        self.status = None
        self.icon = None
        self.wind = None
        self.temperature = None
        """
        (current, max, min)
        """
        if wiki is not None:
            wiki.find(town)
            self.suggest = wiki.suggest
            town = self.suggest
        try:
            current = self.own.weather_at_place(town).get_weather()
        except:
            return 'ERROR'
        self.status = current.get_detailed_status()
        self.icon = current.get_weather_icon_name()
        self.wind = current.get_wind()['speed']
        self.temperature = tuple(
            list(current.get_temperature('celsius').values())[
            0:3])  # (curretn, max, min)
        self.pressure = current.get_pressure()['press']
        self.humidity = current.get_humidity()
        self.town = town
        return 'OK'
