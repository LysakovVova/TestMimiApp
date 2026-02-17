import os
import sqlite3
import user_action
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

user_id = 776659667

conn = sqlite3.connect(os.getenv("DB_NAME"))
cursor = conn.cursor()

cursor.execute("DELETE FROM caves")

conn.commit()
conn.close()