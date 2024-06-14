import psycopg2
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Параметры базы данных
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Подключение к базе данных
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

def add_user(telegram_id, username):
    cursor.execute("""
    INSERT INTO users (telegram_id, username) 
    VALUES (%s, %s) 
    ON CONFLICT (telegram_id) DO NOTHING RETURNING id;
    """, (telegram_id, username))
    conn.commit()

    cursor.execute("SELECT id FROM users WHERE telegram_id = %s;", (telegram_id,))
    return cursor.fetchone()[0]

def add_score(user_id, score):
    cursor.execute("INSERT INTO scores (user_id, score) VALUES (%s, %s);", (user_id, score))
    conn.commit()
