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
    bot.reply_to(message, "Привет! Добро пожаловать в игру! Используй /play, чтобы начать.")

@bot.message_handler(commands=['play'])
def play_game(message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Логика игры теперь выполняется в браузере, отправляем пользователю ссылку на игру
    game_url = 'http://localhost:8000/index.html'  # Замените на действительный URL игры
    bot.reply_to(message, f'Играй в игру по этой ссылке: {game_url}')

if __name__ == '__main__':
    bot.polling(none_stop=True)
