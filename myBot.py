#!/usr/bin/python3
import collections
import time

# Настройки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import my_read
# from wiki_search import Wiki
from wiki_search_v2 import Wiki
from Log import Log

myToken = my_read.read_telegram_token()
start_message = my_read.read_message('start_message')

log = Log()

# print(start_message)
# exit()

updater = Updater(
    token=myToken)  # Токен API к Telegram
dispatcher = updater.dispatcher


# class MyBot:
#
#     def __init__(self):
#         self.updater = Updater(token=myToken)  # заводим апдейтера
#         handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
#         self.updater.dispatcher.add_handler(handler)  # ставим обработчик всех текстовых сообщений
#         self.handlers = collections.defaultdict()  # заводим мапу "id чата -> генератор"

def getName(update):
    try:
        return update.message.from_user.first_name
    except:
        return 'unknown'


wikies = {}

# Обработка команд
def startCommand(bot, update):
    name = getName(update)
    bot.send_message(chat_id=update.message.chat_id,
                     text=start_message % name)
    wikies[update.message.chat_id] = Wiki(log=log)
    print("pre logging")
    log.write(str('from ' + str(
        update.message.chat_id) + ' named ' + name + ' start command\n'))
    print('start logged')


def textMessage(bot, update):
    current_message = str(update.message.text)
    if 'найди' in current_message.lower():
        current_message = current_message.lower().replace('найди', '')
        print("find log start")
        print(str(current_message))
        name = getName(update)
        log.write(
            'from ' + str(
                update.message.chat_id) + ' named ' + name + " find command with \t"
            + str(current_message))
        # print("find logged")
        # bot.send_message(chat_id=update.message.chat_id,
        #                  text='ищу ' + current_message)
        # print(wikies[update.message.chat_id])
        # link = wikies[update.message.chat_id].find_link(current_message)
        code = wikies[update.message.chat_id].find(current_message)
        print('code = ', code, ' text = ', wikies[update.message.chat_id].text)
        log.write(current_message + ' found with code ' + code)
        if code == 'OK' or code is None:
            bot.send_message(chat_id=update.message.chat_id, text=wikies[update.message.chat_id].text)
        else:
            wikies[update.message.chat_id].find(wikies[update.message.chat_id].maybe[0])
            print('code = ', code, ' text = ', wikies[update.message.chat_id].text)
            bot.send_message(chat_id=update.message.chat_id, text=wikies[update.message.chat_id].text)
        log.write('message ' + wikies[update.message.chat_id].text + ' send to ' + name)
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
