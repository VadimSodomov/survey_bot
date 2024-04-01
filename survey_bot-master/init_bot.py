import telebot
from dotenv import load_dotenv
import os

load_dotenv(".env")

bot = telebot.TeleBot(os.getenv("TOKEN"))
