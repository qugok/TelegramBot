from Message import *
from weather import Weather
from wiki_search import Wiki


def dialog(name=None):
    if name is not None:
        update = yield Message(start_message.format(name)).make_keyboard(
            [['Да'], ['Нет']])
        answer = update.message
    if name is None or str(answer.text).lower().startswith('нет'):
        update = yield Message('Как мне тебя называть?')
        answer = update.message
        name = answer.text.rstrip(".!").capitalize()
    wiki = Wiki()
    weather = Weather()
    update = yield info_message
    answer = update.message
    while True:
        if answer.text.startswith('/minimize'):
            weather.minimize = True
            update = yield Message('Done')
            answer = update.message
            continue
        if answer.text.startswith('/find'):
            text = answer.text[5:]
            if text.strip() == '':
                update = yield Message('Введите то, что хотите найти')
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

        if answer.text.startswith('/date'):
            text = answer.text[5:]
            if text.strip(' !.();:') == '':
                update = yield Message('Введите год')
                answer = update.message
                text = answer.text

            update = yield from date(text, wiki)
            answer = update.message
            continue

        if answer.text.startswith('/weather'):
            text = answer.text[8:]
            if text.strip(' !.();:') == '':
                update = yield Message('Введите город')
                answer = update.message
                text = answer.text
            print('town', text)
            update = yield from get_weather(text, weather, wiki)
            answer = update.message
            continue

        if 'спасибо' in answer.text.lower():
            update = yield Message(
                'Всегда пожалуйста, {}!\nРад был помочь)'.format(name),
                'Всё для тебя - рассветы и туманы,\nДля тебя - моря и океаны,\nДля тебя - цветочные поляны,\nДля тебя, {}!'.format(
                    name))
            answer = update.message
            continue

        if 'пожалуйста' in answer.text.lower():
            update = yield Message(
                'Вы так просите, {}!\nЯ просто не могу отказать\nСделаю всё, что в моих силах.'.format(
                    name))
            answer = update.message
            continue

        update = yield info_message.add('Я не понимаю что вы написали(',
                                        'Вот вам подсказка,\nЗдесь всё, что я умею\nВы можете её вызвать командой /help\nУдачи!)')
        answer = update.message


def chose_lang(wiki: Wiki):
    update = yield chose_lang_message
    lang = update.message.text
    if lang.lower().startswith('rus') or lang.lower().startswith('рус'):
        code = 'ru'
    elif lang.lower().startswith('eng') or lang.lower().startswith('анг'):
        code = 'en'
    else:
        code = lang.lower()
    if wiki.set_lang(code) == 'SUCCESSFUL':
        ans = yield Message('язык успешно сменен на ' + lang.capitalize())
    else:
        ans = yield Message(
            'Не удалось смениеть язык на ' + lang.capitalize() + ' попробуйте что-то другое')
    # print('end')
    return ans


def send_find_text(text: str, wiki: Wiki):
    request = wiki.find(text)
    print('request code', request)
    if request == 'OK':
        update = yield from print_page(wiki)
    elif request == 'OPTIONS':
        temp = [i.lower() for i in wiki.maybe]
        update = yield Message('что из этого вы имели ввиду?').make_keyboard(
            [[i.capitalize()] for i in temp if temp.count(i) == 1])
        if update.message.text in wiki.maybe:
            request = wiki.find(update.message.text)
            if request == 'OK':
                update = yield from print_page(wiki)
            else:
                update = yield Message(
                    'Не удалось найти информацию по этому запросу(')
        else:
            update = yield Message('Таких вариантов нет(')
    else:
        update = yield Message('Не удалось найти информацию по этому запросу(')
    return update


def print_page(wiki: Wiki):
    if wiki.suggest is None:
        update = yield Message(link.format(wiki.page.url, wiki.page.title),
                               wiki.text,
                               'Вам нужно больше информации?',
                               parse_mode='HTML').make_keyboard(
            [['Да'], ['Нет']])
    else:
        update = yield Message(
            'Возможно вы имели ввиду ' + link.format(wiki.page.url,
                                                     wiki.suggest), wiki.text,
            'Вам нужно больше информации?', parse_mode='HTML').make_keyboard(
            [['Да'], ['Нет']])
    if str(update.message.text).lower().strip().startswith('да'):
        update = yield Message(str(wiki.page.content))
    else:
        update = yield Message('Ну как хочешь...')
    return update


def date(text, wiki: Wiki):
    if not text.strip('донэ. ').isdigit():
        update = yield Message(
            'Вы ввели не только цифры года, попытайтесь с начала')

        return update
    year = text.strip()
    wiki.find_date(year)
    # print(str(year), wiki.events)
    try:
        temp = [[i.capitalize()] for i, j in wiki.events]
        events = {i.capitalize(): j for i, j in wiki.events}
    except:
        update = yield Message('Не удалось найти информацию по этому запросу(')
        return update
    update = yield Message(link.format(wiki.page.url, str(wiki.suggest)), wiki.text, parse_mode='HTML').make_keyboard(temp)
    while 1:
        if update.message.text in temp:
            update = yield Message(events[update.message.text], parse_mode='HTML').make_keyboard(temp + [['Это всё, что я хотел узнать']])
            continue
        break
    update = yield Message('Ну ок')
    return update


def get_weather(text, weather: Weather, wiki: Wiki = None):
    print('start finding')
    request = weather.get_weather(text, wiki)
    print('request code', request)
    if request == 'OK':
        answer = []
        if weather.suggest is not None:
            answer.append(
                'Возможно вы имели ввиду ' + str(weather.suggest).capitalize())
        answer.append(
            weather_message.format(weather.town, weather.status, weather.wind,
                                   weather.temperature, weather.humidity,
                                   weather.pressure))
        update = yield PhotoMessage(*answer, photo=icon.format(weather.icon))
        return update
    else:
        update = yield Message('я не знаю такого города')
        return update


def bad_bot(name='Никита'):
    """
    специально для Никиты
    :return:
    """
    count = 0
    while True:
        yield Message('Я с тобой не разговариваю!',
                      'вот тебе клавиатура').make_keyboard(
            ['qwertyuiop[]', 'asdfghjkl;', 'zxcvbnm,./'])
        count += 1
        if count % 10 == 0:
            yield Message('Тебе не надоело?').make_keyboard([['Да'], ['Нет']])
