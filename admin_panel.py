import os
import sqlite3
import user_action
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

user_id = 776659667

for i in range(1, 20):
    user_action.update_user_inventory(user_id, i, 5)