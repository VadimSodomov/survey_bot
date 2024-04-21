import datetime
from src.smilies import smilies


def get_welcome(name) -> str:
    current_time = datetime.datetime.now()
    if 23 <= current_time.hour or current_time.hour < 5:
        return f"Доброй ночи, {name}! {smilies['night']}"
    if 5 <= current_time.hour < 11:
        return f"Доброе утро, {name}! {smilies['morning']}"
    if 11 <= current_time.hour < 17:
        return f"Добрый день, {name}! {smilies['day']}"
    if 17 <= current_time.hour < 23:
        return f"Добрый вечер, {name}! {smilies['evening']}"


if __name__ == '__main__':
    print(datetime.datetime.now())
