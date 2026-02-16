import os
import sqlite3
import user_action
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

DB_NAME = os.getenv("DB_NAME")

user_id = 776659667

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("UPDATE users SET coordinate_x = ?, coordinate_y = ? WHERE user_id = ?", (15, 15, user_id))
conn.commit()
conn.close()

print(user_action.get_ships(user_id), sep="\n")

print(user_action.get_ship_info(1), sep="\n")