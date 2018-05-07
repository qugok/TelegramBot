import wikipedia

from Log import Log


class Wiki:

    def __init__(self, log: Log = None):
        self.__log = log
        self.text = None
        self.maybe = []
        self.page = None

    def find(self, query: str):
        try:
            self.page = wikipedia.page(query)
            self.text = wikipedia.page(query).summary
            return 'OK'
        except wikipedia.exceptions.DisambiguationError as e:
            self.maybe = e.options
            self.text = 'Too many options\nPlease more definitely'
            return 'OPTIONS'
            # raise e
        except wikipedia.exceptions.PageError:
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


