import os
import sqlite3
import user_action
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

DB_NAME = os.getenv("DB_NAME")

user = 797667496
user_action.update_user_inventory(user, 0, 5)
user_action.update_user_inventory(user, 1, 5)
user_action.update_user_inventory(user, 2, 5)
user_action.update_user_inventory(user, 3, 5)
user_action.update_user_inventory(user, 4, 5)
user_action.update_user_inventory(user, 5, 5)