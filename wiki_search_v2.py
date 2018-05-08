import wikipedia
import re
from Log import Log


class Wiki:

    def __init__(self, lang: str = 'ru', log: Log = None):
        self.lang = 'ru'
        self.set_lang(lang)
        self.__log = log
        self.text = None
        self.maybe = []
        self.suggest = None

    def set_lang(self, lang: str = 'ru'):
        try:
            wikipedia.set_lang(lang)
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


