import telebot
from dotenv import load_dotenv
import os
from db import add_user, add_score
# Здесь не нужно импортировать game, так как логика игры выполняется в браузере

# Загрузка переменных окружения из .env файла
load_dotenv()

# Инициализация бота с вашим токеном
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Помоги Саше не насадиться на член! Используй /play, чтобы начать.")

@bot.message_handler(commands=['play'])
def play_game(message):
    user_id = message.from_user.id
    username = message.from_user.username
    keyboard = telebot.types.InlineKeyboardMarkup()
    game_url = 'https://kirillqa17.github.io/IFlappy/'
    web_app_info = telebot.types.WebAppInfo(url=game_url)
    web_app_button = telebot.types.InlineKeyboardButton(text="Играть в игру", web_app=web_app_info)
    keyboard.add(web_app_button)
    # Логика игры теперь выполняется в браузере, отправляем пользователю ссылку на игру

    bot.reply_to(message,'Жми быстрее бля', reply_markup=keyboard)

if __name__ == '__main__':
    bot.polling(none_stop=True)
