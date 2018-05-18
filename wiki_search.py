import re

import wikipedia


class Wiki:

    def __init__(self, lang: str = 'ru'):
        self.lang = 'ru'
        self.set_lang(lang)
        self.text = None
        self.maybe = []
        self.suggest = None
        self.events = None
        self.page = None

    def set_lang(self, lang: str = 'ru'):
        try:
            wikipedia.set_lang(lang)
            wikipedia.search('сталин')
            self.lang = lang
            return 'SUCCESSFUL'
        except:
            self.lang = 'ru'
            return 'ERROR'

    def find(self, query: str):
        self.suggest = None
        try:
            wikipedia.set_lang(self.lang)
            self.text = wikipedia.summary(query)
            self.suggest = wikipedia.suggest(query)
            self.page = wikipedia.page(query)
            if self.text == '':
                self.text = self.page.content
            return 'OK'
        except wikipedia.exceptions.DisambiguationError as e:
            self.maybe = e.options
            self.text = 'Too many options\nPlease more definitely'
            return 'OPTIONS'
            # raise e
        except wikipedia.exceptions.PageError:
            self.text = 'Page not found'
            return None

    def find_date(self, date: str):
        if self.lang == 'ru':
            date = date.strip()
            if date.strip() == '400':
                date = date.strip() + 'й год'
            elif date.strip().isdigit():
                date = date.strip() + ' год'
            else:
                date = date.strip() + ' до н.э'
            wikipedia.set_lang('ru')
        else:
            if date.strip().isdigit():
                date = 'AD ' + date
            else:
                date = date.strip('донэ.') + ' BC'
            wikipedia.set_lang('en')
        self.events = None
        self.suggest = None
        # return 'Простите, данный сервис сейчас не доступен(\nПопробуйте что-нибудь другое'
        try:
            page = wikipedia.page(date)
            # page.t
            events = re.search(r'(==(?:.|\n)*?)\n== ', page.content)
            events = events.groups()[0]
            events = events.split('\n=== ')
            events = [tuple([j.strip() for j in i.split('=') if j != '']) for i in events if 'См. также' not in i]
            if events[0][1] == '':
                events.pop(0)
            self.events = events
            self.suggest = wikipedia.suggest(date)
            self.suggest = page.title
            self.page = page
            self.text = page.summary
            return events
        except:
            return None

    def __str__(self):
        # return str(self.__dict__)
        return self.text
