import telebot.types

from functions.database_funcs import get_all_questions_db, delete_question_by_id_db
from init_bot import bot
from keyboards.inline import numbers_questions_delete_keyboard


@bot.callback_query_handler(func=lambda callback: callback.data == "delete_question")
def delete_question(callback: telebot.types.CallbackQuery):
    all_questions_and_id = get_all_questions_db()
    if all_questions_and_id:
        questions_id = [q[0] for q in all_questions_and_id]
        questions_text = [f'▫ {i+1}. {q[1]}' for i, q in enumerate(all_questions_and_id)]
        text = '\n'.join(questions_text)
        markup = numbers_questions_delete_keyboard(questions_id)
        bot.send_message(callback.message.chat.id, f'Выберите вопросы, которые хотите удалить ❎\n{text}', reply_markup=markup)
    else:
        bot.send_message(callback.message.chat.id, "На данный момент не создано ни одного вопроса. Удалять нечего)")


@bot.callback_query_handler(func=lambda callback: callback.data[0] == ">")
def edit_markup_right(callback: telebot.types.CallbackQuery):
    first_id = int(callback.data[1:])
    last_questions = get_all_questions_db(last_id=first_id)
    all_questions_and_id = get_all_questions_db(first_id=first_id)
    questions_id = [q[0] for q in all_questions_and_id]

    bot.edit_message_reply_markup(
        callback.message.chat.id,
        callback.message.id,
        reply_markup=numbers_questions_delete_keyboard(questions_id, k=len(last_questions)//8)
    )


@bot.callback_query_handler(func=lambda callback: callback.data[0] == "<")
def edit_markup_left(callback: telebot.types.CallbackQuery):
    last_id = int(callback.data[1:])+1
    all_questions_and_id = get_all_questions_db(last_id=last_id)
    questions_id = [q[0] for q in all_questions_and_id]
    questions_id = questions_id[len(questions_id)-1-8:]
    first_id = questions_id[0]
    last_questions = get_all_questions_db(last_id=first_id)
    bot.edit_message_reply_markup(
        callback.message.chat.id,
        callback.message.id,
        reply_markup=numbers_questions_delete_keyboard(questions_id, k=len(last_questions)//8)
    )


@bot.callback_query_handler(func=lambda callback: callback.data.isdigit())
def delete_question_by_id(callback: telebot.types.CallbackQuery):
    delete_question_by_id_db(int(callback.data))
    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text="Вопрос, варианты ответа и связанная с ним статистика успешно удалены)",
        reply_markup=None
    )
