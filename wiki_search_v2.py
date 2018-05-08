import wikipedia

from Log import Log


class Wiki:

    def __init__(self, lang: str = 'ru', log: Log = None):
        self.lang = 'ru'
        self.set_lang(lang)
        self.__log = log
        self.text = None
        self.maybe = []
        self.page = None

    def set_lang(self, lang: str = 'ru'):
        try:
            wikipedia.set_lang(lang)
            self.lang = lang
            return 'SUCCESSFUL'
        except:
            self.lang = 'ru'
            return 'ERROR'

    def find(self, query: str):
        wikipedia.set_lang(self.lang)
        try:
            # print('start finding')
            self.page = wikipedia.page(query)
            self.text = self.page.summary
            return 'OK'
        except wikipedia.exceptions.DisambiguationError as e:
            # print('Too many options')
            self.maybe = e.options
            self.text = 'Too many options\nPlease more definitely'
            return 'OPTIONS'
            # raise e
        except wikipedia.exceptions.PageError:
            print('not found')
            self.text = 'Page not found'
            return None

    def __str__(self):
        # return str(self.__dict__)
        return self.text

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


