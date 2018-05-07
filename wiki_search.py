import re

import requests
from bs4 import BeautifulSoup

from Log import Log


class Wiki:

    def __init__(self, language: str = 'ru', log: Log = None):
        self.__link = None
        self.__log = log
        if len(language) == 2:
            self.__url = 'https://www.google.ru/search?q=site%3A' + language.lower() + '.wikipedia.com+'
        else:
            if language.lower() == 'English'.lower() or 'Английский'.lower():
                self.__url = 'https://www.google.ru/search?q=site%3Aen.wikipedia.com+'
            elif language.lower() == 'Russian'.lower() or 'Русский'.lower():
                self.__url = 'https://www.google.ru/search?q=site%3Aru.wikipedia.com+'
            else:
                self.__url = 'https://www.google.ru/search?q=site%3Aru.wikipedia.com+'

    def set_language(self, language: str = 'ru'):
        if len(language) == 2:
            self.__url = 'https://www.google.ru/search?q=site%3A' + language.lower() + '.wikipedia.com+'
        else:
            if language.lower() == 'English'.lower() or 'Английский'.lower():
                self.__url = 'https://www.google.ru/search?q=site%3Aen.wikipedia.com+'
            elif language.lower() == 'Russian'.lower() or 'Русский'.lower():
                self.__url = 'https://www.google.ru/search?q=site%3Aru.wikipedia.com+'
            else:
                self.__url = 'https://www.google.ru/search?q=site%3Aru.wikipedia.com+'

    def find_link(self, query: str) -> str:
        dict = ''
        # page = requests.get(self.__url + query,
        #                     params=[('accept-language', 'en')])
        print(query)
        page = requests.get(self.__url + query)
        print(self.__url + query)
        soup = BeautifulSoup(page.text, 'html.parser')
        h3 = soup.find_all('h3', class_='r')
        link = None
        index = 0
        # print(len(h3))
        for elem in h3:
            # print(index, end='\t')
            index += 1
            try:
                elem = elem.contents[0]
                elem = elem['href']
            except:
                pass
            if 'wikipedia' in elem:
                # print(str(elem))
                # print("'", re.search(r'=(.*?)&', str(elem)).groups()[0], "'")
                link = re.search(r'=(.*?)&', str(elem)).groups()[0]
                # link = ('https://www.google.ru' + elem)
                break
        if not link:
            # print('Sorry, not Found')
            self.__log.write('Sorry, not Found')
            self.__link = None
            return 'Sorry, not Found'
        # print(link)
        if self.__log is not None:
            self.__log.write('link Found\n' + link)
        self.__link = link
        return link

    def get_text(self):
        if self.__link is None:
            return 'Sorry, not Found'
        print(self.__link)
        page = requests.get(self.__link)
        soup = BeautifulSoup(page.text, 'html.parser')
        text = soup.find(id='mw-content-text')
        p = text.find('p')
        print('pre log')
        if self.__log is not None:
            self.__log.write("Found text:\n" + p.get_text())
        return p.get_text()

    def __str__(self):
        return str(self.__dict__)

# def findWiki(query: str, log=None) -> str:
#     dict = ''
#     url = 'http://www.google.ru/search?q='
#     page = requests.get(url + query)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     h3 = soup.find_all('h3', class_='r')
#     link = None
#     index = 0
#     print(len(h3))
#     for elem in h3:
#         print(index, end='\t')
#         index += 1
#         try:
#             elem = elem.contents[0]
#             elem = elem['href']
#         except:
#             pass
#         if 'wikipedia' in elem:
#             # print(elem)
#             link = ('https://www.google.ru' + elem)
#             break
#     if not link:
#         print('Sorry, not Found')
#         log.write('Sorry, not Found')
#         return 'Sorry, not Found'
#     print(link)
#     log.write('link Found\n' + link)
#     # print(page.text)
#     page = requests.get(link)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     text = soup.find(id='mw-content-text')
#     p = text.find('p')
#     log.write("with text:\n" + p.get_text())
#     return p.get_text()
#     # while p is not None:
#     #     dict += p.get_text()
#     #     p = p.find_next('p')
#     # # dict = dict.split()
#     # return dict
