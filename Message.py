import telegram
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

import my_read

message_size_limit = 4000


def split(message: str):
    temp = ''
    for i in message.split('\n'):
        if len(temp + i) > message_size_limit:
            yield temp.strip()
            temp = ''
        temp += '\n' + i
    if len(temp.strip()) != 0:
        yield temp.strip()


class Message:
    def __init__(self, *texts, **options):
        self.texts = texts
        if 'reply_markup' not in options:
            options['reply_markup'] = ReplyKeyboardRemove()
        self.options = options

    def send(self, bot: telegram.Bot, chat_id):
        self.prepare()
        for text in self.texts:
            if len(text.strip()) != 0:
                bot.sendMessage(chat_id=chat_id, text=text, **self.options)

    def add(self, *texts: str):
        return Message(*texts, *self.texts, **self.options)

    def prepare(self):
        texts = []
        for i in self.texts:
            texts.extend(split(i))
        self.texts = texts

    def __str__(self):
        return str(self.__dict__)

    def make_keyboard(self, list):
        new = []
        for i in list:
            line = []
            for j in i:
                line.append(KeyboardButton(text=j))
            new.append(line)
        self.options['reply_markup'] = ReplyKeyboardMarkup(new)
        return self

    def make_inline_keyboard(self, list):
        new = []
        for i in list:
            line = []
            for j in i:
                line.append(
                    InlineKeyboardButton(text=j[0], callback_data=j[1]))
            new.append(line)
        self.options['reply_markup'] = InlineKeyboardMarkup(new)
        return self


class PhotoMessage(Message):

    def __init__(self, *texts, **options):
        self.photo = None
        if 'photo' in options:
            self.photo = options['photo']
            options.pop('photo')
        super().__init__(*texts, **options)

    def send(self, bot: telegram.Bot, chat_id):
        self.prepare()
        for text in self.texts[:-1]:
            if len(text.strip()) != 0:
                bot.sendMessage(chat_id=chat_id, text=text, **self.options)
        try:
            if len(self.texts) > 0:
                bot.sendPhoto(chat_id=chat_id, photo=self.photo,
                              caption=self.texts[-1])
            else:
                bot.sendPhoto(chat_id=chat_id, photo=self.photo)
        except:
            if len(self.texts) > 0:
                bot.sendMessage(chat_id=chat_id, text=self.texts[-1])


link = my_read.read_message('link')
icon = my_read.read_message('image')

start_message = my_read.read_message('start_message')
chose_lang_html_text = my_read.read_message('chose_lang_message')
help_message = my_read.read_message('help_message')
info_find_message = my_read.read_message('info_find_message')
info_date_message = my_read.read_message('info_date_message')
info_lang_message = my_read.read_message('info_lang_message')
weather_message = my_read.read_message('weather')

chose_lang_message = Message(chose_lang_html_text, parse_mode='HTML')
info_message = Message(info_find_message, info_lang_message, info_date_message,
                       parse_mode='HTML')
