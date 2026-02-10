import os  # 1. Импортируем модуль для работы с системой
from dotenv import load_dotenv # 2. Импортируем загрузчик переменных окружения из файла .env
load_dotenv()  # 3. Загружаем переменные окружения из файла

import sqlite3 # 4. Импортируем модуль для работы с базой данных SQLite

import hmac, hashlib, time, json # 5. Импортируем модули для работы с криптографией, временем и JSON
from fastapi import FastAPI, HTTPException 
import random 
from pydantic import BaseModel 
from urllib.parse import parse_qsl 



DB_NAME = "bot_database.db"

def init_db(): # Инициализируем базу данных, создавая таблицу для хранения данных пользователей, если она еще не существует
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            last_number INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_user_number(user_id: int, number: int): # Сохраняем сгенерированное число для пользователя
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, last_number) VALUES (?, ?)', (user_id, number))
    conn.commit()
    conn.close()

def get_user_number(user_id: int): # Получаем последнее сохраненное число для пользователя
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT last_number FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone() # Вернет кортеж (число,) или None
    conn.close()
    return result[0] if result else None

init_db()


app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN")

class AuthReq(BaseModel):
    initData: str

def verify_init_data(init_data: str, max_age_sec: int = 3600) -> dict:
    data = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = data.pop("hash", None)
    if not received_hash:
        raise HTTPException(401, "No hash")

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(401, "Bad signature")

    auth_date = int(data.get("auth_date", "0"))
    if auth_date <= 0 or (time.time() - auth_date) > max_age_sec:
        raise HTTPException(401, "Expired")

    return data

@app.post("/auth")
def auth(req: AuthReq):
    data = verify_init_data(req.initData)
    user = json.loads(data["user"])
    user_id = user["id"]

    

    balance = get_user_number(user_id)
    if (balance is None):
        return {"user_id": user_id, "last_number": "нет данных"}
    return {"user_id": user_id, "last_number": balance}


class RangeReq(BaseModel):
    user_id: int
    min: int
    max: int

@app.post("/number")
def number_range(req: RangeReq):
    if req.min > req.max:
        return {"error": "min > max"}


    n = random.randint(req.min, req.max)

    save_user_number(req.user_id, n)

    return {"number": n}
