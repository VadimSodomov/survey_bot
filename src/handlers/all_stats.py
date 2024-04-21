import telebot.types

from functions.database_funcs import get_all_stats_db
from init_bot import bot


@bot.callback_query_handler(func=lambda callback: callback.data == "all_stats")
def get_all_stats(callback: telebot.types.CallbackQuery):
    text = get_all_stats_db()
    if text == "":
        bot.send_message(callback.message.chat.id, "Общая статистика пока что пуста")
    else:
        bot.send_message(callback.message.chat.id, text)
