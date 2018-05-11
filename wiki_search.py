import re

import wikipedia

from Log import Log


class Wiki:

    def __init__(self, lang: str = 'ru', log: Log = None):
        self.lang = 'ru'
        self.set_lang(lang)
        self.__log = log
        self.text = None
        self.maybe = []
        self.suggest = None
        self.events = None

    def log(self, message: str = None):
        if Log is None or message is None:
            pass
        else:
            self.__log.write(message)

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
            # print('start finding')
            wikipedia.set_lang(self.lang)
            self.text = wikipedia.summary(query)
            self.suggest = wikipedia.suggest(query)
            if self.text == '':
                self.text = get_facked(query)
            return 'OK'
        except wikipedia.exceptions.DisambiguationError as e:
            # print('Too many options')
            self.maybe = e.options
            self.text = 'Too many options\nPlease more definitely'
            return 'OPTIONS'
            # raise e
        except wikipedia.exceptions.PageError:
            # print('not found')
            self.text = 'Page not found'
            return None

    def fullFind(self, query: str):

        code = self.find(query)
        # print('code = ', code, ' text = ', wikies[update.message.chat_id].text)
        self.log(query + ' found with code ' + str(code))
        if code == 'OK' or code is None:
            if self.suggest is None:
                self.log('without suggestion with text' + "'" + str(self.text) + "'")
                return str(self.text)
            else:
                self.log('with suggestion ' + str(self.suggest) + 'with text' + str(self.text))
                return 'you mean ' + str(self.suggest) + '?\n' + str(self.text)
        else:
            self.log('what do you mean?\n' + '\n'.join(self.maybe[:20]))
            return 'what do you mean?\n' + '\n'.join(self.maybe[:20])

    def find_date(self, date: str):
        if date.strip().isdigit():
            date += ' год'
        self.events = None
        self.suggest = None
        # return 'Простите, данный сервис сейчас не доступен(\nПопробуйте что-нибудь другое'
        try:
            page = wikipedia.page(date)
            events = re.search(r'(==(?:.|\n)*?)\n== ', page.content)
            events = events.groups()[0]
            events = events.split('\n=== ')
            events = [tuple([j.strip() for j in i.split('=') if j != '']) for i in events if 'См. также' not in i]
            if events[0][1] == '':
                events.pop(0)
            self.events = events
            self.suggest = wikipedia.suggest(date)
            self.suggest = page.title
            return events
        except:
            return None

    def __str__(self):
        # return str(self.__dict__)
        return self.text


def get_facked(query: str):
    try:
        paragraph_pattern = re.compile('.*\n')
        return paragraph_pattern.match(wikipedia.page(query).content).group()
    except Exception as e:
        # print(e)
        return 'Page not found'

# print("1: Searching Wikipedia for 'Orange'")
# try:
#     # pass
#     print(wikipedia.page('Orange color').summary)
#     # wikipedia.page('Orange')
# except wikipedia.exceptions.DisambiguationError as e:
#     # print(*e.args[-1], sep='\n')
#     print(e)
#     print('DisambiguationError: The page name is ambiguous')
# print()
