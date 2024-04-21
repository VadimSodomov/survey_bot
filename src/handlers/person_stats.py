import telebot.types

from src.functions.database_funcs import get_questions_answered_user_db, get_questions_for_user_db
from src.init_bot import bot
from src.smilies import smilies


@bot.callback_query_handler(func=lambda callback: callback.data == 'my_stats')
def get_my_stats(callback: telebot.types.CallbackQuery):
    answered_questions = get_questions_answered_user_db(callback.from_user.id)
    all_questions = get_questions_for_user_db()
    if answered_questions:
        questions_choices = []
        for i, c in enumerate(get_questions_answered_user_db(callback.from_user.id, for_stats=True)):
            questions_choices.append(f'🔹 {i+1}. {c[0]} -- {c[1]}')
        stats = "\n\n".join(questions_choices)
        if len(answered_questions) == len(all_questions):
            bot.send_message(
                callback.message.chat.id,
                f'{smilies["checkbox"]} Ты ответил(а) на все вопросы {smilies["checkbox"]}\n\n{smilies["statistic"]} Твоя статистика прохождения опроса:\n\n{stats}'
            )
        else:
            bot.send_message(
                callback.message.chat.id,
                f'Ты ответил(а) на {len(answered_questions)}/{len(all_questions)} вопросов {smilies["ok"]}\n\n{smilies["statistic"]} Твоя статистика прохождения опроса:\n\n{stats}'
            )
    else:
        bot.send_message(callback.message.chat.id, 'Твоя статистика пока что пуста, пройди опрос и она появится)')
