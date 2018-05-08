#!/usr/bin/python3

# Настройки
import collections

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import my_read


class message:
    def __init__(self, *texts, **options):
        self.texts = texts
        self.options = options

    def send(self, bot: telegram.Bot, chat_id):
        for text in self.texts:
            bot.sendMessage(chat_id=chat_id, text=text, *self.options)



class myBot:

    def __init__(self, token, generator):
        self.updater = Updater(token=token)  # заводим апдейтера
        handler = MessageHandler(Filters.text | Filters.command,
                                 self.handle_message)
        self.updater.dispatcher.add_handler(
            handler)  # ставим обработчик всех текстовых сообщений
        self.handlers = collections.defaultdict(
            generator)  # заводим мапу "id чата -> генератор"

    def handle_message(self, bot, update):
        print("Received", update.message)
        chat_id = update.message.chat_id
        if update.message.text == "/start":
            # если передана команда /start, начинаем всё с начала -- для
            # этого удаляем состояние текущего чатика, если оно есть
            self.handlers.pop(chat_id, None)
        if chat_id in self.handlers:
            # если диалог уже начат, то надо использовать .send(), чтобы
            # передать в генератор ответ пользователя
            try:
                answer = self.handlers[chat_id].send(update.message)
            except StopIteration:
                # если при этом генератор закончился -- что делать, начинаем общение с начала
                del self.handlers[chat_id]
                # (повторно вызванный, этот метод будет думать, что пользователь с нами впервые)
                return self.handle_message(bot, update)
        else:
            # диалог только начинается. defaultdict запустит новый генератор для этого
            # чатика, а мы должны будем извлечь первое сообщение с помощью .next()
            # (.send() срабатывает только после первого yield)
            answer = next(self.handlers[chat_id])
        # отправляем полученный ответ пользователю
        print("Answer: %r" % answer)
        bot.sendMessage(chat_id=chat_id, text=answer)


start_message = my_read.read_message('start_message')

def dialog():
    answer = yield start_message
    # убираем ведущие знаки пунктуации, оставляем только
    # первую компоненту имени, пишем её с заглавной буквы
    name = answer.text.rstrip(".!").split()[0].capitalize()
    likes_python = yield from ask_yes_or_no("Приятно познакомиться, %s. Вам нравится Питон?" % name)
    if likes_python:
        answer = yield from discuss_good_python(name)
    else:
        answer = yield from discuss_bad_python(name)
