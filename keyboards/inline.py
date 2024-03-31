import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(text="Пройти опрос", callback_data="get_survey"),
        InlineKeyboardButton(text="Личная статистика", callback_data="my_stats"),
        InlineKeyboardButton(text="Общая статистика", callback_data="all_stats"),
        InlineKeyboardButton(text="Создать вопрос", callback_data="add_question"),
        InlineKeyboardButton(text="Удалить вопрос", callback_data="delete_question")
    )
    return markup


def get_default_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(text="Пройти опрос", callback_data="get_survey"),
        InlineKeyboardButton(text="Личная статистика", callback_data="my_stats")
    )
    return markup


def get_continue_add_question_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(text="Ввести следующий вопрос", callback_data="add_question"),
        InlineKeyboardButton(text="Выйти в меню", callback_data="/start")
    )
    return markup


def get_start_survey_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Начать прохождение", callback_data="start_survey"))
    return markup


def get_continue_survey_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Продолжить прохождение", callback_data="start_survey"))
    return markup


def get_choices_markup(choices):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    print(choices)
    for choice in choices:
        choice_id = choice.split(", ")[0]
        markup.add(InlineKeyboardButton(text=choice.split(", ")[1], callback_data=f'c{choice_id}'))
    return markup


def numbers_questions_delete_keyboard(questions_id, k=0):
    #print(questions_id)
    d = {}
    r = 8
    if k > 0:
        d[f'<{r*k}'] = {"callback_data": f"<{questions_id[0]-1}"}
    for i, q_id in enumerate(questions_id):
        if i+(r*k) < r + r*k:
            d[str(i+1+(r*k))] = {"callback_data": str(q_id)}
        else:
            d[f'>{i+(r*k)}'] = {"callback_data": f">{q_id}"}
            break
    markup = telebot.util.quick_markup(d, row_width=8)
    return markup
