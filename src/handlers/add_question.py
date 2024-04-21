import telebot.types
import datetime

from src.functions.database_funcs import add_question_to_db, get_id_last_question_db, add_choices_to_db
from src.handlers.user import States
from src.init_bot import bot
from src.keyboards.inline import get_continue_add_question_keyboard


@bot.callback_query_handler(func=lambda callback: callback.data == "add_question")
def add_question(callback: telebot.types.CallbackQuery):
    bot.send_message(callback.message.chat.id, "Введи, пожалуйста, вопрос: 💬")
    bot.set_state(callback.from_user.id, States.wait_question, callback.message.chat.id)


@bot.message_handler(state=States.wait_question)
def wait_question(message: telebot.types.Message):
    add_question_to_db(question_text=message.text, telegram_id=message.from_user.id, publish_date=datetime.datetime.now())
    bot.send_message(message.chat.id, "Вопрос успешно добавлен! 👍\n\nВведи, пожалуйста, в одном сообщении варианты ответов) Каждый ответ нужно вводить с новой строки 😉")
    bot.set_state(message.from_user.id, States.wait_choice, message.chat.id)


@bot.message_handler(state=States.wait_choice)
def wait_choice(message: telebot.types.Message):
    choices = message.text.split('\n')
    id_last_question = get_id_last_question_db()
    for choice in choices:
        add_choices_to_db(choice_text=choice, question_id=id_last_question)
    markup = get_continue_add_question_keyboard()
    bot.send_message(message.chat.id, "Варианты ответа успешно добавлены! 💫", reply_markup=markup)
    bot.delete_state(message.from_user.id, message.chat.id)
