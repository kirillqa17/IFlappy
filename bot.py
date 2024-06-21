import os
import logging
from dotenv import load_dotenv
import telebot
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from threading import Thread
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, PrimaryKeyConstraint, Boolean, ARRAY

# Load environment variables
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
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class GameResult(db.Model):
    __tablename__ = 'game_results'
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_score = Column(Integer, nullable=False, default=0)
    referrals_count = Column(Integer, nullable=False, default=0)
    referrals = db.Column(ARRAY(db.BigInteger), default=[])
    has_referrer = db.Column(db.Boolean, default=False)
    referrer_id = db.Column(db.BigInteger, nullable=True)

    __table_args__ = (PrimaryKeyConstraint('user_id', 'timestamp', name='game_results_pk'),)  # Composite primary key

    def __init__(self, user_id, username, score, total_score, referrals_count, referrals, has_referrer, referrer_id):
        self.user_id = user_id
        self.username = username
        self.score = score
        self.total_score = total_score
        self.referrals_count = referrals_count
        self.referrals = referrals
        self.has_referrer = has_referrer
        self.referrer_id = referrer_id


def get_total_score(user_id):
    result = db.session.query(GameResult.total_score).filter(GameResult.user_id == user_id).order_by(
        GameResult.timestamp.desc()).first()
    return result.total_score if result else 0


def save_game_result(user_id, username, score):
    with app.app_context():
        total_score = get_total_score(user_id) + score
        new_result = GameResult(user_id=user_id, username=username, score=score, total_score=total_score)
        db.session.add(new_result)
        db.session.commit()

def get_username(user_id):
    with app.app_context():
        user = db.session.query(GameResult.username).filter(GameResult.user_id == user_id).first()
        return user.username if user else None

def create_user(user_id, username, referrer_id=None):
    with app.app_context():
        existing_user = db.session.query(GameResult).filter(GameResult.user_id == user_id).first()
        if not existing_user:
            new_user = GameResult(user_id=user_id, username=username, score=0, total_score=0, referrals_count=0,
                                  referrals=[], has_referrer=bool(referrer_id), referrer_id=referrer_id)
            db.session.add(new_user)
            db.session.commit()
            if referrer_id:
                referrer = db.session.query(GameResult).filter(GameResult.user_id == referrer_id).first()
                if referrer:
                    if referrer.referrals is None:
                        referrer.referrals = []
                    updated_referrals = referrer.referrals + [user_id]
                    referrer.referrals = updated_referrals
                    referrer.referrals_count += 1
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
    data = request.get_json()
    score = data.get('score')
    try:
        result = GameResult.query.filter_by(user_id=user_id).first()
        if result:
            result.score = score
            result.timestamp = datetime.now()
            result.total_score += score
            db.session.commit()
            return jsonify(status='update', message='Game result updated successfully')
        else:
            new_result = GameResult(user_id=user_id, username=username, score=score, timestamp=datetime.now(),
                                    total_score=score)
            db.session.add(new_result)
            db.session.commit()
            return jsonify(status='success', message='Game result sent successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify(status='error', error=str(e))


@app.route('/get_referrals_count/<int:user_id>', methods=['GET'])
def handle_get_referrals_count(user_id):
    try:
        referrals_count = db.session.query(GameResult.referrals_count).filter(GameResult.user_id == user_id).scalar()
        return jsonify({"referrals_count": referrals_count})
    except Exception as e:
        app.logger.error(f"Error fetching referrals count for user_id {user_id}: {e}")
        return jsonify({"error": str(e)}), 500



@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username

    referrer_id = None
    if len(message.text.split()) > 1:
        referrer_id = int(message.text.split()[1])

    create_user(user_id, username, referrer_id)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('/play'))

    bot.send_message(message.chat.id, "Помоги Саше не насадиться на член! Используй /play, чтобы начать.",
                     reply_markup=keyboard)


@bot.message_handler(commands=['play'])
def play_game(message):
    user_id = message.from_user.id
    username = message.from_user.username
    game_url = f"https://kirillqa17.github.io/IFlappy/index.html?user_id={user_id}&username={username}"

    keyboard = telebot.types.InlineKeyboardMarkup()
    web_app_info = telebot.types.WebAppInfo(url=game_url)
    web_app_button = telebot.types.InlineKeyboardButton(text="Быстрее жми, Саша умоляет. ну пожалуйста",
                                                        web_app=web_app_info)
    keyboard.add(web_app_button)

    bot.reply_to(message, "Самое главное не посади его на хуй(или посади)", reply_markup=keyboard)


@bot.message_handler(commands=["invite"])
def invite_command_handler(msg):
    user_id = msg.from_user.id

    invite_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    bot.send_message(user_id, f"Пригласите друга по этой ссылке: {invite_link}")

@bot.message_handler(commands=["my_referrals"])
def my_referrals_command_handler(msg):
    user_id = msg.from_user.id
    with app.app_context():
        referrals = db.session.query(GameResult.referrals).filter(GameResult.user_id == user_id).scalar()

        if referrals:
            referral_usernames = [f"@{get_username(referral_id)}" for referral_id in referrals]
            referral_list = "\n".join(referral_usernames)
            bot.send_message(user_id, f"У вас {len(referrals)} рефералов:\n{referral_list}")
        else:
            bot.send_message(user_id, "У вас нет рефералов.")



def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Create tables in the database
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
