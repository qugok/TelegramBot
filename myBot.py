#!/usr/bin/python3

# Настройки
# from emoji import emojize
import collections

import telegram
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, MessageHandler, Filters

import my_read
from wiki_search import Wiki, Log

log = Log()

message_size_limit = 4000
black_list_ids = [75781753]


def write_error(user: str, time: str, message: str):
    with open(user + time + '.txt', 'x', encoding='utf-8') as f:
        f.write(message)


def split(message: str):
    temp = ''
    for i in message.split('\n'):
        if len(temp + i) > message_size_limit:
            yield temp.strip()
            temp = ''
        temp += '\n' + i
    if len(temp.strip()) != 0:
        yield temp.strip()


class message:
    def __init__(self, *texts, **options):
        self.texts = texts
        if 'reply_markup' not in options:
            options['reply_markup'] = ReplyKeyboardRemove()
        self.options = options

    def send(self, bot: telegram.Bot, chat_id):
        print('start sending')
        self.prepare()
        for text in self.texts:
            print(len(text), text)
            bot.sendMessage(chat_id=chat_id, text=text, **self.options)
            print('send')

    def add(self, *texts: str):
        return message(*texts, *self.texts, **self.options)

    def prepare(self):
        texts = []
        for i in self.texts:
            texts.extend(split(i))
        self.texts = texts
        print('prepare finished')

    def __str__(self):
        return str(self.__dict__)

    def makeKeyboard(self, list):
        new = []
        for i in list:
            line = []
            for j in i:
                line.append(KeyboardButton(text=j))
        self.options['reply_markup'] = ReplyKeyboardMarkup(new)
        print('keyboard Made')

    def makeInlineKeyboard(self, list):
        new = []
        for i in list:
            line = []
            for j in i:
                line.append(
                    InlineKeyboardButton(text=j[0], callback_data=j[1]))
        self.options['reply_markup'] = InlineKeyboardMarkup(new)


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
        self.updater.start_polling()
        # self.updater.start_polling(clean=True)
        # Останавливаем бота, если были нажаты Ctrl + C
        self.updater.idle()

    def handle_message(self, bot: telegram.Bot, update: telegram.Update):
        print("Received", update.message)
        chat_id = str(update.message.chat_id)
        try:
            log.write(
                'получил сообщение ' + str(update.message.text) + ' от ' + str(
                    update.message.from_user.first_name) + '\t id ' + chat_id)
        except:
            pass
        if update.message.text == "/start":
            # если передана команда /start, начинаем всё с начала -- для
            # этого удаляем состояние текущего чатика, если оно есть
            self.handlers.pop(chat_id, None)
        # if update.message.text.startswith('/error'):
        #     bot.sendMessage(chat_id=chat_id, text=update.message.text)
        if chat_id in self.handlers:
            # если диалог уже начат, то надо использовать .send(), чтобы
            # передать в генератор ответ пользователя
            try:
                answer = self.handlers[chat_id].send(update)
            except StopIteration:
                # если при этом генератор закончился -- что делать, начинаем общение с начала
                del self.handlers[chat_id]
                # (повторно вызванный, этот метод будет думать, что пользователь с нами впервые)
                return self.handle_message(bot, update)
        else:
            # диалог только начинается. defaultdict запустит новый генератор для этого
            # чатика, а мы должны будем извлечь первое сообщение с помощью .next()
            # (.send() срабатывает только после первого yield)
            if chat_id in black_list_ids:
                self.handlers[chat_id] = bad_bot()
            answer = next(self.handlers[chat_id])
        # отправляем полученный ответ пользователю
        # print("Answer: %r" % answer)
        print('sending answer:')
        answer.send(bot, chat_id)
        log.write('ответ отправлен ' + str(answer))


telegram_token = my_read.read_telegram_token()

link = my_read.read_message('link')

start_message = my_read.read_message('start_message')
chose_lang_html_text = my_read.read_message('chose_lang_message')
help_message = my_read.read_message('help_message')
info_find_message = my_read.read_message('info_find_message')
info_date_message = my_read.read_message('info_date_message')
info_lang_message = my_read.read_message('info_lang_message')
info_error_message = my_read.read_message('info_error_message')
# print(info_error_message)
chose_lang_message = message(chose_lang_html_text, parse_mode='HTML')
info_message = message(info_find_message, info_lang_message, info_date_message,
                       info_error_message, parse_mode='HTML')


def dialog():
    update = yield message(start_message)
    answer = update.message
    # убираем ведущие знаки пунктуации, оставляем только
    # первую компоненту имени, пишем её с заглавной буквы
    name = answer.text.rstrip(".!").split()[0].capitalize()
    wiki = Wiki(log=log)
    update = yield info_message
    answer = update.message
    while True:
        if answer.text.startswith('/find'):
            text = answer.text[5:]
            if text.strip() == '':
                update = yield message('Введите то, что хотите найти')
                answer = update.message
                text = answer.text
            update = yield from send_find_text(text, wiki)
            answer = update.message
            continue

        if answer.text.startswith('/lang'):
            update = yield from chose_lang(wiki)
            answer = update.message
            continue

        if answer.text.startswith('/help'):
            update = yield info_message
            answer = update.message
            continue

        if answer.text.startswith('/date') or answer.text.lower().startswith(
                'что было') or answer.text.lower().startswith('что было в'):
            if answer.text.lower().startswith('что было'):
                text = answer.text[8:]
            elif answer.text.lower().startswith('что было в'):
                text = answer.text[10:]
            else:
                text = answer.text[5:]
            if text.strip(' !.();:') == '':
                update = yield message('Введите год')
                answer = update.message
                text = answer.text
            if not text.strip('годyear нэ.').isdigit():
                update = yield message(
                    'Вы ввели не только цифры года, попытайтесь с начала)')
                answer = update.message
                continue
            year = text.strip()
            wiki.find_date(year)
            # print('find year ' + year)
            # print('to send')
            # print(str(year), wiki.events)
            update = yield message(str(wiki.suggest),
                                   *[i + '\n' + j for i, j in
                                     wiki.events])
            answer = update.message
            # print('send')
            continue

        if 'спасибо' in answer.text.lower():
            update = yield message(
                'Всегда пожалуйста, {}!\nРад был помочь)'.format(name),
                'Всё для тебя - рассветы и туманы,\nДля тебя - моря и океаны,\nДля тебя - цветочные поляны,\nДля тебя, {}!'.format(
                    name))
            answer = update.message
            continue

        if 'пожалуйста' in answer.text.lower():
            update = yield message(
                'Вы так просите, {}!\nЯ просто не могу отказать\nСделаю всё, что в моих силах.'.format(
                    name))
            answer = update.message
            continue

        if answer.text.startswith('/error'):
            text = answer.text[6:]
            if text.strip(' !.();:') == '':
                update = yield message('Введите ваше сообщение')
                answer = update.message
                text = answer.text
            write_error(name + answer.from_user.first_name + answer.chat_id,
                        str(answer.date), text)
            update = yield message(
                'Ваше сообщение было успешно сохранено и создатель в скором времени его обязательно прочитает)')
            answer = update.message
            continue

        update = yield info_message.add('Я не понимаю что вы написали(',
                                        'Вот вам подсказка,\nЗдесь всё, что я умею\nВы можете её вызвать командой /help\nУдачи!)')
        answer = update.message


def chose_lang(wiki: Wiki):
    update = yield chose_lang_message
    lang = update.message
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


def send_find_text(text: str, wiki: Wiki):
    request = wiki.find(text)
    print('request code', request)
    if request == 'OK':
        print(link, link.format(wiki.page.url, text))
        if wiki.suggest is None:
            update = yield message(link.format(wiki.page.url, text), wiki.text,
                'Вам нужно больше информации?').makeKeyboard([['Да'], ['Нет']])
        else:
            update = yield message('Возможно вы имели ввиду ' + link.format(wiki.page.url, wiki.suggest),wiki.text,'Вам нужно больше информации?').makeKeyboard([['Да'], ['Нет']])
        if str(update.message.text).lower().strip().startswith('да'):
            update = yield message(str(wiki.page.content))
        print('returning')
        return update
    else:
        update = yield message('Не удалось найти информацию по этому запросу(')
        return update


def bad_bot():
    """
    специально для Никиты
    :return:
    """
    count = 0
    while True:
        yield message('Я с тобой не разговариваю!')
        count += 1
        if count % 10 == 0:
            yield message('Тебе не надоело?')


if __name__ == "__main__":
    dialog_bot = myBot(telegram_token, dialog)
    dialog_bot.start()
