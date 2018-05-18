import collections

import telegram
from telegram.ext import Updater, MessageHandler, Filters

from Message import *
black_list_usernames = []
other_users = []
my_id = 190016290

class MyBot:

    def __init__(self, token, generator, bad_generator=None):
        self.updater = Updater(token=token)  # заводим апдейтера
        text_handler = MessageHandler(Filters.text | Filters.command,
                                      self.handle_message)
        self.updater.dispatcher.add_handler(
            text_handler)  # ставим обработчик всех текстовых сообщений
        if bad_generator is not None:
            self.bad_generator = bad_generator
        else:
            self.bad_generator = generator
        self.generator = generator
        self.handlers = collections.defaultdict(
            generator)  # заводим мапу "id чата -> генератор"

    def start(self):
        # Начинаем поиск обновлений
        print('Init successful. Polling...')
        # self.updater.start_polling()
        self.updater.start_polling(clean=True)
        # Останавливаем бота, если были нажаты Ctrl + C
        self.updater.idle()

    def handle_message(self, bot: telegram.Bot, update: telegram.Update):
        print(update)
        user = update.message['chat']['username']
        chat_id = str(update.message.chat_id)
        if user in black_list_usernames and user in other_users:
            other_users.remove(user)
            self.handlers.pop(chat_id, None)
        if update.message.text == '/block':
            black_list_usernames.append(user)
            self.handlers.pop(chat_id, None)
        elif str(update.message.text).startswith('/block') and int(chat_id) == my_id:
            black_list_usernames.extend(str(update.message.text).split()[1:])
        if update.message.text == '/unblock':
            black_list_usernames.remove(user)
            self.handlers.pop(chat_id, None)
        elif str(update.message.text).startswith('/unblock') and int(chat_id) == my_id:
            try:
                black_list_usernames.remove((update.message.text).split()[-1])
            except:
                pass
        if update.message.text == '/clear_black' and int(chat_id) == my_id:
            black_list_usernames.clear()
        # if update.message.text.starts
        if update.message.text == "/start":
            # если передана команда /start, начинаем всё с начала -- для
            # этого удаляем состояние текущего чатика, если оно есть
            self.handlers.pop(chat_id, None)
        if chat_id in self.handlers:
            try:
                answer = self.handlers[chat_id].send(update)
            except StopIteration:
                del self.handlers[chat_id]
                return self.handle_message(bot, update)
        else:
            name = update.message['chat']['first_name']
            if user in black_list_usernames:
                self.handlers[chat_id] = self.bad_generator(name)
            else:
                self.handlers[chat_id] = self.generator(name)
                other_users.append(user)
            answer = next(self.handlers[chat_id])
        # отправляем полученный ответ пользователю
        answer.send(bot, chat_id)
