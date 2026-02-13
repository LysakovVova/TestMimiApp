import os  # 1. Импортируем модуль для работы с системой
from dotenv import load_dotenv # 2. Импортируем загрузчик переменных окружения из файла .env
load_dotenv()  # 3. Загружаем переменные окружения из файла

import sqlite3 # 4. Импортируем модуль для работы с базой данных SQLite

import hmac, hashlib, time, json # 5. Импортируем модули для работы с криптографией, временем и JSON
from fastapi import FastAPI, HTTPException 
import random 
from pydantic import BaseModel 
from urllib.parse import parse_qsl 
import asyncio


import worker_of_ivents # 6. Импортируем наш воркер, который будет раздавать подарки пользователям
import worker_of_coordinate # 7. Импортируем наш воркер, который будет двигать пользователей по координатам


DB_NAME = os.getenv("DB_NAME")

def init_db(): # Инициализируем базу данных, создаем таблицы и добавляем начальные данные
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            coordinate_x INTEGER DEFAULT 0,
            coordinate_y INTEGER DEFAULT 0,
            target_planet_id INTEGER DEFAULT 0,
            currently_on_planet_id INTEGER DEFAULT 0,
            FOREIGN KEY (target_planet_id) REFERENCES planets(id),
            FOREIGN KEY (currently_on_planet_id) REFERENCES planets(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER,
            planet_id INTEGER,
            FOREIGN KEY (planet_id) REFERENCES planets(id)
        )
    '''

)

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_offers (
            user_id INTEGER,
            item_id INTEGER,
            item_name TEXT,
            count INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(id)
    )''' )

    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS planets (
            id INTEGER PRIMARY KEY,
            name TEXT,
            coordinate_x INTEGER,
            coordinate_y INTEGER                
    )''')

    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (0, "Космос", 0, 0)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (1, "Земля", 10, 10)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (2, "Марс", -20, -10)')

    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, planet_id) VALUES (1, "Камень", 1, 0)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, planet_id) VALUES (2, "Мусор", 1, 0)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, planet_id) VALUES (3, "Обломок", 1, 0)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, planet_id) VALUES (4, "Дерево", 10, 1)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, planet_id) VALUES (5, "Вода", 10, 1)')    
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, planet_id) VALUES (6, "Камень", 10, 1)')    
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, planet_id) VALUES (7, "Песок", 10, 2)')    
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, planet_id) VALUES (8, "Красный камень", 10, 2)')

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

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    current_planet_id = cursor.execute("SELECT currently_on_planet_id FROM users WHERE user_id = ?", (req.user_id,)).fetchone()[0]

    
    possible_gifts = cursor.execute("SELECT id, name, planet_id FROM items WHERE planet_id = ?", (current_planet_id,)).fetchall()



    item_id = random.choice(possible_gifts)[0]  # Здесь можно заменить на реальный выбор предмета
    item_count = random.randint(1, 5)  # Здесь можно заменить на реальное количество

    item_name = cursor.execute("SELECT name FROM items WHERE id = ?", (item_id,)).fetchone()[0]


    update_user_inventory(req.user_id, item_id, item_count)
    cursor.close()
    conn.close()
    return {
        "result": "success",
        "message": f"Куплено {item_count} единиц предмета {item_name}"
    }


class offerReq(BaseModel):
    user_id: int

@app.post("/check_offer") # Эндпоинт для получения активных предложений для пользователя
def get_offers(req: offerReq):
    user_id = req.user_id
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_name, count FROM active_offers WHERE user_id = ?", (user_id,))
    offer = cursor.fetchone()
    conn.close()
    
    if offer:
        return {"has_offer": True, "item_id": offer[0], "name": offer[1], "count": offer[2]}
    else:
        return {"has_offer": False}
@app.post("/accept_offer") # Эндпоинт для принятия предложения, который принимает идентификатор пользователя и идентификатор предмета, который он хочет принять
def accept_offer(req: offerReq):
    user_id = req.user_id
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_name, count FROM active_offers WHERE user_id = ?", (user_id,))
    offer = cursor.fetchone()
    
    if not offer:
        conn.close()
        raise HTTPException(404, "Нет активного предложения")
    
    item_id, item_name, count = offer
    update_user_inventory(user_id, item_id, count)
    
    cursor.execute("DELETE FROM active_offers WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return {"result": "success", "message": f"Принято предложение: {count}x {item_name}"}

@app.post("/decline_offer") # Эндпоинт для отклонения предложения, который принимает идентификатор пользователя и удаляет активное предложение
def decline_offer(req: offerReq):
    user_id = req.user_id
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_offers WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return {"result": "success", "message": "Предложение отклонено"}


@app.post("/get_planets") # Эндпоинт для получения списка всех планет с их координатами
def get_planets(req: offerReq):
    user_id = req.user_id

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, coordinate_x, coordinate_y FROM planets WhERE id != 0")  # Получаем все планеты, кроме "Космоса"
    planets = cursor.fetchall()
    
    user_coordinates = cursor.execute("SELECT coordinate_x, coordinate_y FROM users WHERE user_id = ?", (user_id,)).fetchone()

    cursor.close()
    conn.close()


    return {"planets": [{"id": p[0], "name": p[1], "coordinate_x": p[2], "coordinate_y": p[3]} for p in planets],
            "user_coordinates": {"x": user_coordinates[0], "y": user_coordinates[1]}
            }

class target_planetReq(BaseModel):
    user_id: int
    target_planet_id: int

@app.post("/set_target_planet") # Эндпоинт для установки цели планеты
def set_target_planet(req: target_planetReq):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    user_id = req.user_id
    target_planet_id = req.target_planet_id

    current_planet_id = cursor.execute("SELECT currently_on_planet_id FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    if current_planet_id == target_planet_id:
        cursor.close()
        conn.close()
        return {"result": "success", "message": "Вы уже на этой планете!"}
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Проверяем, существует ли планета с таким ID
    cursor.execute("SELECT id FROM planets WHERE id = ?", (target_planet_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(404, "Планета не найдена")
    
    cursor.execute("UPDATE users SET currently_on_planet_id = 0 WHERE user_id = ?", (user_id,))  # Сбрасываем текущее местоположение, если пользователь уже на планете
    
    
    # Устанавливаем цель планеты для пользователя
    cursor.execute("UPDATE users SET target_planet_id = ? WHERE user_id = ?", (target_planet_id, user_id))

    planet_name = cursor.execute("SELECT name FROM planets WHERE id = ?", (target_planet_id,)).fetchone()[0]
    conn.commit()
    conn.close()
    
    return {"result": "success", "message": f"Цель планеты установлена на {planet_name}"}


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(worker_of_ivents.gift_worker())
    asyncio.create_task(worker_of_coordinate.coordinate_worker())

