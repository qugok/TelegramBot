#!/usr/bin/python3

import time

import requests
from bs4 import BeautifulSoup
# Настройки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class Log:
    def __init__(self):
        self.__file = 'logfile-' + str(
            time.strftime("%d-%m-%Y-%H.%M.%S")) + '.txt'
        with open(self.__file, 'x'):
            pass
        self.write("started")

    def write(self, info: str):
        print("start open")
        with open(self.__file, 'w') as file:
            print("start log")
            file.write(info)
            print("end log")


log = Log()

def findWiki(query: str) -> str:
    dict = ''
    url = 'http://www.google.ru/search?q='
    page = requests.get(url + query)
    soup = BeautifulSoup(page.text, 'html.parser')
    h3 = soup.find_all('h3', class_='r')
    link = None
    index = 0
    print(len(h3))
    for elem in h3:
        print(index, end='\t')
        index += 1
        try:
            elem = elem.contents[0]
            elem = elem['href']
        except:
            pass
        if 'wikipedia' in elem:
            # print(elem)
            link = ('https://www.google.ru' + elem)
            break
    if not link:
        print('Sorry, page not Found')
        log.write('Sorry, page not Found')
        return 'Sorry, page not Found'
    print(link)
    log.write('link Found\n' + link)
    # print(page.text)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser')
    text = soup.find(id='mw-content-text')
    p = text.find('p')
    log.write("with text:\n" + p.get_text())
    return p.get_text()
    # while p is not None:
    #     dict += p.get_text()
    #     p = p.find_next('p')
    # # dict = dict.split()
    # return dict


with open('myToken') as f:
    myToken = f.readline().replace('\n', '')

with open('messages/start_message', encoding='utf-8') as f:
    start_message = f.read()


# print(start_message)
# exit()

updater = Updater(
    token=myToken)  # Токен API к Telegram
dispatcher = updater.dispatcher


# Обработка команд
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=start_message)
    print("pre logging")
    log.write(str('from' + update.message.chat_id + "start command\n"))
    print('start logged')


def textMessage(bot, update):
    current_message = str(update.message.text)
    if 'найди' in current_message:
        current_message = current_message.replace('найди', '')
        log.write(
            'from' + update.message.chat_id + "find command with \t" + current_message + "\n")
        # bot.send_message(chat_id=update.message.chat_id,
        #                  text='ищу ' + current_message)
        bot.send_message(chat_id=update.message.chat_id,
                         text=findWiki(current_message))
        log.write('message send\n')
        print("message send")

    else:
        response = 'Получил Ваше сообщение: ' + update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=response)


# Хендлеры
start_command_handler = CommandHandler('start', startCommand)
text_message_handler = MessageHandler(Filters.text, textMessage)

# Добавляем хендлеры в диспетчер
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(text_message_handler)
# Начинаем поиск обновлений
updater.start_polling(clean=True)
# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
