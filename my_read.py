def read_telegram_token():
    with open('myToken') as f:
        my_token = f.readline().replace('\n', '')
    return my_token


def read_message(message_name: str):
    with open('messages/' + message_name, encoding='utf-8') as f:
        message = f.read()
    return message

def read_google_token():
    with open('myGoogleToken') as f:
        my_token = f.readline().replace('\n', '')
    return my_token
