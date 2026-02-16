import os
import sqlite3
import user_action
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

user_id = 776659667

print(user_action.mine(user_id))