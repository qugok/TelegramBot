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
        self.temperature = None  # curretn
        self.humidity = None
        self.pressure = None
        self.own = pyowm.OWM(API_key=token, language='RU')

    def get_weather(self, town: str, wiki: Wiki = None):
        print(town, 'Town')
        self.suggest = None
        self.status = None
        self.icon = None
        self.wind = None
        self.temperature = None
        """
        (current, max, min)
        """
        ERROR = False
        try:
            current = self.own.weather_at_place(town).get_weather()
        except:
            print('first error')
            ERROR = True

        if ERROR and wiki is not None:
            try:
                code = wiki.find(town)
            except:
                return 'ERROR'
            if wiki.suggest is not None:
                self.suggest = wiki.suggest
                town = self.suggest
                ERROR = False
            elif code == 'OK':
                self.suggest = wiki.page.title
                town = self.suggest
                ERROR = False
        if ERROR:
            return 'ERROR'
        else:
            try:
                current = self.own.weather_at_place(town).get_weather()
            except:
                print('final error')
                return 'ERROR'
        print('errors are in the past')
        self.status = current.get_detailed_status()
        self.icon = current.get_weather_icon_name()
        self.wind = current.get_wind()['speed']
        self.temperature = current.get_temperature('celsius').values()[0] # current
        self.pressure = current.get_pressure()['press']
        self.humidity = current.get_humidity()
        self.town = town
        return 'OK'
