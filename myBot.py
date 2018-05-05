#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
# Настройки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def findWiki(query: str) -> str:
    dict = ""
    url = 'http://www.google.com/search?q='
    page = requests.get(url + query)
    soup = BeautifulSoup(page.text, "html.parser")
    h3 = soup.find_all("h3", class_="r")
    link = None
    for elem in h3:
        try:
            elem = elem.contents[0]
            elem = elem["href"]
        except:
            pass
        if "wikipedia" in elem:
            # print(elem)
            link = ("https://www.google.com" + elem)
            break
    if not link:
        return "Sorry, page not Found"
    # print(link)
    # print(page.text)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, "html.parser")
    text = soup.find(id="mw-content-text")
    p = text.find("p")
    while p is not None:
        dict += p.get_text() + "\n"
        p = p.find_next("p")
    # dict = dict.split()
    return dict


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


def textMessage(bot, update):
    current_message = str(update.message.text)
    if "найди" in current_message:
        current_message.replace("найди", '')
        bot.send_message(chat_id=update.message.chat_id,
                         text=findWiki(current_message))
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
