#!/usr/bin/python3

# Настройки
import collections

import telegram
from telegram.ext import Updater, MessageHandler, Filters

import my_read
from wiki_search_v2 import Wiki, Log

log = Log()


class message:
    def __init__(self, *texts, **options):
        self.texts = texts
        self.options = options

    def send(self, bot: telegram.Bot, chat_id):
        for text in self.texts:
            bot.sendMessage(chat_id=chat_id, text=text, **self.options)

    def add(self, *texts: str):
        return message(*texts, *self.texts, **self.options)


class myBot:

    def __init__(self, token, generator):
        self.updater = Updater(token=token)  # заводим апдейтера
        handler = MessageHandler(Filters.text | Filters.command,
                                 self.handle_message)
        self.updater.dispatcher.add_handler(
            handler)  # ставим обработчик всех текстовых сообщений
        self.handlers = collections.defaultdict(
            generator)  # заводим мапу "id чата -> генератор"

    def start(self):
        # Начинаем поиск обновлений
        self.updater.start_polling(clean=True)
        # Останавливаем бота, если были нажаты Ctrl + C
        self.updater.idle()

    def handle_message(self, bot, update):
        # print("Received", update.message)
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
        # print("Answer: %r" % answer)
        answer.send(bot, chat_id)


telegram_token = my_read.read_telegram_token()

start_message = my_read.read_message('start_message')
info_find_message = my_read.read_message('info_find_message')
help_message = my_read.read_message('help_message')
chose_lang_html_text = my_read.read_message('chose_lang_message')
info_date_message = my_read.read_message('info_date_message')

chose_lang_message = message(chose_lang_html_text, parse_mode='HTML')
info_message = message(info_find_message, info_date_message)


def dialog():
    answer = yield message(start_message)
    # убираем ведущие знаки пунктуации, оставляем только
    # первую компоненту имени, пишем её с заглавной буквы
    name = answer.text.rstrip(".!").split()[0].capitalize()
    wiki = Wiki(log=log)
    answer = yield info_message
    while True:
        if answer.text.startswith('/find') or answer.text.lower().startswith(
                'найди'):
            if answer.text.lower().startswith('найди мне'):
                text = answer.text[9:]
            else:
                text = answer.text[5:]
            if text.strip(' !.();:') == '':
                answer = yield message('Введите то, что хотите найти')
            text = answer.text
            # print('pre Wiki')
            current = message(wiki.fullFind(text))
            # print('post Wiki')
            answer = yield current
            continue

        if answer.text.startswith('/lang'):
            answer = yield from chose_lang(wiki)
            continue

        if answer.text.startswith('/help'):
            answer = yield info_message
            continue

        if answer.text.startswith('/date') or answer.text.lower().startswith(
                'что было') or answer.text.lower().startswith('что было в'):
            if answer.text.lower().startswith('что было'):
                text = answer.text[8:]
            elif answer.text.lower().startswith('что было в'):
                text = answer.text[10:]
            else:
                text = answer.text[5:]
            if not text.strip('годyear ').isdigit():
                answer = yield message(
                    'Вы ввели не только цифры года, попытайтесь ещё разок)')
                continue
            year = int(text.strip('годyear '))
            current = message(str(year), wiki.find_date(year))
            answer = yield current
            continue
        if 'спасибо' in answer.text.lower():
            answer = yield message(
                'Всегда пожалуйста, %s!\nРад был помочь)' % name)
            continue

        if 'пожалуйста' in answer.text.lower():
            answer = yield message('Вы так просите, %s!\nЯ просто не могу отказать\nСделаю всё, что в моих силах.' % name)
            continue

        answer = yield info_message.add('Я не понимаю что вы написали(', 'Вот вам подсказка,\nЗдесь всё, что я умею\nВы можете её вызвать командой /help\nУдачи!)')


def chose_lang(wiki: Wiki):
    lang = yield chose_lang_message
    lang = lang.text
    if lang.lower().startswith('rus') or lang.lower().startswith('рус'):
        code = 'ru'
    elif lang.lower().startswith('eng') or lang.lower().startswith('анг'):
        code = 'en'
    else:
        code = lang.lower()
    # print(code)
    if wiki.set_lang(code) == 'SUCCESSFUL':
        # ans = yield message('язык успешно сменен на ' + lang.capitalize() + ' with code ' + code)
        ans = yield message('язык успешно сменен на ' + lang.capitalize())
    else:
        ans = yield message(
            'не удалось смениеть язык на' + lang + 'попробуйте что-то другое')
    # print('end')
    return ans


if __name__ == "__main__":
    dialog_bot = myBot(telegram_token, dialog)
    dialog_bot.start()
