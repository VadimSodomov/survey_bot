import telebot

from src.functions.database_funcs import create_tables_from_db
from src.handlers import register_handlers
from src.init_bot import bot

if __name__ == '__main__':
    create_tables_from_db()
    register_handlers()
    bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
    print("Bot is active!")
    bot.infinity_polling()
