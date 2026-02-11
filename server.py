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

def init_db(): # Инициализируем базу данных, создаем таблицы и добавляем начальные данные
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER,
            item_id INTEGER,
            count INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            PRIMARY KEY (user_id, item_id)
        )
    ''')

    cursor.execute('INSERT OR IGNORE INTO items (id, name, price) VALUES (1, "Камень", 1)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price) VALUES (2, "Мусор", 1)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price) VALUES (3, "Обломок", 1)')

    conn.commit()
    conn.close()
def get_user_balance(user_id: int): # Получаем баланс пользователя

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    balance = cursor.fetchone()
    conn.close()
    return balance[0] if balance else None

def update_user_inventory(user_id: int, item_id: int, count: int): # Обновляем инвентарь пользователя в базе данных
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = '''
        INSERT INTO inventory (user_id, item_id, count)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, item_id)
        DO UPDATE SET count = count + ?
    '''
    cursor.execute(query, (user_id, item_id, count, count))
    conn.commit()
    conn.close()
def get_user_inventory(user_id: int): # Получаем инвентарь пользователя из базы данных
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = '''
        SELECT items.name, inventory.count
        FROM inventory
        JOIN items ON inventory.item_id = items.id
        WHERE inventory.user_id = ?
    '''
    cursor.execute(query, (user_id,))
    items = cursor.fetchall()
    conn.close()
    return [{"name": name, "count": count} for name, count in items]
def create_user(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)', (user_id, 0))
    
    conn.commit()
    conn.close()
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

    create_user(user_id)

    balance = get_user_balance(user_id)
    if balance is None:
        return {"user_id": user_id, "balance": 0}
    return {"user_id": user_id, "balance": balance}



class RangeReq(BaseModel):
    user_id: int

@app.post("/get_inventory") # Эндпоинт, который принимает идентификатор пользователя и возвращает его инвентарь
def number_range(req: RangeReq):
    inventory = get_user_inventory(req.user_id)
    return {"inventory": inventory}

class BuyReq(BaseModel):
    user_id: int

@app.post("/buy_item") # Эндпоинт для покупки предмета, который принимает идентификатор пользователя и идентификатор предмета, который он хочет купить
def buy_item(req: BuyReq):
    item_id = random.randint(1, 3)  # Здесь можно заменить на реальный выбор предмета
    item_count = random.randint(1, 5)  # Здесь можно заменить на реальное количество
    update_user_inventory(req.user_id, item_id, item_count)
    return {
        "result": "success",
        "message": f"Куплено {item_count} единиц предмета с ID {item_id}"
    }