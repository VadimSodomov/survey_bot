import telebot.types
import os

from telebot.handler_backends import StatesGroup, State

from functions.database_funcs import add_admin_to_db
from functions.datetime_funcs import get_welcome
from init_bot import bot
from keyboards.inline import get_admin_keyboard, get_default_keyboard


class States(StatesGroup):
    wait_question = State()
    wait_choice = State()
    user_on_survey = State()


def start_help(user_id, username, chat_id):
    if str(user_id) in os.getenv("ADMINS").split(', '):
        add_admin_to_db(telegram_id=user_id, name=username)
        markup = get_admin_keyboard()
        bot.send_message(
            chat_id,
            f'\U0001F4A5Версия для админов\U0001F4A5\n\n{get_welcome(username)}\nЯ бот для опросов)',
            reply_markup=markup
        )
    else:
        markup = get_default_keyboard()
        bot.send_message(
            chat_id,
            f'{get_welcome(username)}\nЯ бот для опросов \U0001F31F',
            reply_markup=markup
        )


@bot.message_handler(commands=["start", "help"])
def start_help_message(message: telebot.types.Message):
    start_help(message.from_user.id, message.from_user.username, message.chat.id)


@bot.callback_query_handler(func=lambda callback: callback.data == "/start")
def start_help_callback(callback: telebot.types.CallbackQuery):
    bot.edit_message_reply_markup(callback.message.chat.id,callback.message.id,reply_markup=None)
    start_help(callback.from_user.id, callback.from_user.username, callback.message.chat.id)
