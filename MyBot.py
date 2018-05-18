import collections

import telegram
from telegram.ext import Updater, MessageHandler, Filters

from Message import *
black_list_ids = [75781753]


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
        chat_id = str(update.message.chat_id)
        Message(link.format('123', '456'), parse_mode='HTML').send(bot, chat_id)
        if update.message.text == '/block':
            black_list_ids.append(int(chat_id))
            self.handlers.pop(chat_id, None)
        if update.message.text == '/unblock':
            black_list_ids.pop(black_list_ids.index(int(chat_id)))
            self.handlers.pop(chat_id, None)
        if update.message.text == '/clear_black':
            black_list_ids.clear()
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
            name = link.format(chat_id, name)
            if int(chat_id) in black_list_ids:
                self.handlers[chat_id] = self.bad_generator(name)
            else:
                self.handlers[chat_id] = self.generator(name)
            answer = next(self.handlers[chat_id])
        # отправляем полученный ответ пользователю
        answer.send(bot, chat_id)
