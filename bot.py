import os
import logging
from dotenv import load_dotenv
import telebot
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
from datetime import datetime

# Загрузите переменные окружения
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

if not API_TOKEN:
    raise ValueError("No API token provided. Set the TELEGRAM_TOKEN environment variable.")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
db = SQLAlchemy(app)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

class GameResult(db.Model):
    __tablename__ = 'game_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_score = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, username, score, total_score):
        self.user_id = user_id
        self.username = username
        self.score = score
        self.total_score = total_score

def get_total_score(user_id):
    result = db.session.query(GameResult.total_score).filter(GameResult.user_id == user_id).order_by(GameResult.timestamp.desc()).first()
    return result.total_score if result else 0

def save_game_result(user_id, username, score):
    total_score = get_total_score(user_id) + score
    new_result = GameResult(user_id=user_id, username=username, score=score, total_score=total_score)
    db.session.add(new_result)
    db.session.commit()

@app.route('/get_total_score/<int:user_id>', methods=['GET'])
def handle_get_total_score(user_id):
    try:
        total_score = get_total_score(user_id)
        return jsonify({"total_score": total_score})
    except Exception as e:
        app.logger.error(f"Error fetching total score for user_id {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/send_result/<int:user_id>/<username>', methods=['POST'])
def handle_send_result(user_id, username):
    try:
        data = request.get_json()
        score = data['score']
        save_game_result(user_id, username, score)
        return jsonify({"status": "success"})
    except Exception as e:
        app.logger.error(f"Error saving game result for user_id {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Создайте таблицы в базе данных
    with app.app_context():
        db.create_all()

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    try:
        bot.polling(none_stop=True)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Telegram API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
