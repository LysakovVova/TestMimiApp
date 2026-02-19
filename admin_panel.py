import os
import sqlite3
import user_action
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

user_id = 797667496

game = user_action.GameRepository(os.getenv("DB_NAME"))  # Инициализируем репозиторий для работы с базой данных

DB_NAME = os.getenv("DB_NAME")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
