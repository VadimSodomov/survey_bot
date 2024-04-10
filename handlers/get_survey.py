import telebot.types

from functions.database_funcs import get_questions_answered_user_db, get_questions_for_user_db, \
    get_last_answered_question_db, get_current_question_db, get_current_choices, add_user_vote_db
from handlers.user import States
from init_bot import bot
from keyboards.inline import get_start_survey_keyboard, get_continue_survey_keyboard, get_choices_markup


@bot.callback_query_handler(func=lambda callback: callback.data == "get_survey")
def get_survey(callback: telebot.types.CallbackQuery):
    answered_questions = get_questions_answered_user_db(telegram_id=callback.from_user.id) #получить id вопросов пройденных из статистики
    questions = get_questions_for_user_db(answered_questions) #получить неотвеченные вопросы
    all_questions = get_questions_for_user_db()
    if questions:
        if answered_questions:
            markup = get_continue_survey_keyboard()
            bot.send_message(
                callback.message.chat.id,
                f'Ранее ты уже ответил на {len(answered_questions)}/{len(all_questions)} вопросов 😉',
                reply_markup=markup
            )
        else:
            markup = get_start_survey_keyboard()
            bot.send_message(
                callback.message.chat.id,
                f'Опрос состоит из {len(questions)} вопросов) Будем рады вашему прохождению! ☺',
                reply_markup=markup
            )
    else:
        bot.send_message(
            callback.message.chat.id,
            'Ты ответил на все вопросы 👍\nСпасибо за прохождение опроса! 😉'
        )
        bot.delete_state(callback.from_user.id, callback.message.chat.id)


def send_question(user_id, chat_id, message_id):
    cnt_answered, last = get_last_answered_question_db(telegram_id=user_id)
    current_question = get_current_question_db(last)  # {id:, text:}
    if current_question:
        current_choices = get_current_choices(current_question["id"])  # -> ["id, text", ]
        markup = get_choices_markup(choices=current_choices)  # template_call_data: "number, answer"
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        bot.send_message(
            text=f'🔸 {cnt_answered + 1}. {current_question["text"]}',
            chat_id=chat_id,
            reply_markup=markup
        )
    else:
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        bot.send_message(
            chat_id,
            'Ты ответил на все вопросы 👍\nСпасибо за прохождение опроса! 😉'
        )
        bot.delete_state(user_id, chat_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "start_survey")
def start_survey(callback: telebot.types.CallbackQuery):
    send_question(callback.from_user.id, callback.message.chat.id, callback.message.id)
    bot.set_state(callback.from_user.id, States.user_on_survey, callback.message.chat.id)


@bot.callback_query_handler(state=States.user_on_survey, func=lambda callback: callback.data[0] == "c")
def survey(callback: telebot.types.CallbackQuery):
    answer_id = int(callback.data[1:])
    add_user_vote_db(choice_id=answer_id, telegram_id=callback.from_user.id)
    send_question(callback.from_user.id, callback.message.chat.id, callback.message.id)
