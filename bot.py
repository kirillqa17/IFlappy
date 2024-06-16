import os
from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import telebot
from threading import Thread

load_dotenv()

app = Flask(__name__)

# Настройки Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настройки базы данных
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Подключение к базе данных
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

def create_user(user_id, username):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO game_results (user_id, username, total_score)
            VALUES (%s, %s, 0)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, username))
        conn.commit()

def update_game_result(user_id, score):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE game_results
            SET total_score = total_score + %s, timestamp = NOW()
            WHERE user_id = %s
        """, (score, user_id))
        conn.commit()

def get_total_score(user_id):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT total_score
            FROM game_results
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

@app.route('/send_result/<user_id>', methods=['POST'])
def send_result(user_id):
    data = request.get_json()
    score = data['score']
    update_game_result(user_id, score)
    return jsonify({'status': 'success'})

@app.route('/get_total_score/<user_id>', methods=['GET'])
def get_total_score_route(user_id):
    total_score = get_total_score(user_id)
    return jsonify({'total_score': total_score})

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    create_user(user_id, username)
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

    bot.reply_to(message, 'Жми быстрее бля', reply_markup=keyboard)

def start_bot():
    bot.polling()

if __name__ == '__main__':
    bot_thread = Thread(target=start_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=5000)
