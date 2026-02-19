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
import init_db # 8. Импортируем наш воркер, который будет работать с базой данных
import user_action # 9. Импортируем наш воркер, который будет обрабатывать действия пользователей

from typing import Optional


app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN")

class AuthReq(BaseModel):
    initData: str

class BaseUserReq(BaseModel):
    user_id: int

class CraftReq(BaseUserReq):
    item_id: int

class ShipReq(BaseUserReq):
    ship_id: int

class CaveReq(BaseUserReq):
    cave_id: int

class planetReq(BaseUserReq):
    planet_id: Optional[int] = None
    item_id: Optional[int] = None

game = user_action.GameRepository(os.getenv("DB_NAME")) # Инициализируем репозиторий для работы с базой данных, передавая ему имя базы данных из переменных окружения


@app.post("/auth") # Эндпоинт для аутентификации пользователя, который принимает данные от Telegram и возвращает результат аутентификации
def auth(req: AuthReq):
    return game.auth_user_db(req.initData)



@app.post("/get_inventory") # Эндпоинт, который принимает идентификатор пользователя и возвращает его инвентарь
def number_range(req: BaseUserReq):
    inventory = game.get_user_inventory(req.user_id)
    return inventory


@app.post("/check_offer") # Эндпоинт для получения активных предложений для пользователя
def get_offers(req: BaseUserReq):
    user_id = req.user_id
    return game.get_active_offer(user_id)
    
    
@app.post("/accept_offer") # Эндпоинт для принятия предложения, который принимает идентификатор пользователя и идентификатор предмета, который он хочет принять
def accept_offer(req: BaseUserReq):
    user_id = req.user_id  
    return game.accept_offer(user_id)

@app.post("/decline_offer") # Эндпоинт для отклонения предложения, который принимает идентификатор пользователя и удаляет активное предложение
def decline_offer(req: BaseUserReq):
    user_id = req.user_id
    
    return game.decline_offer(user_id)


@app.post("/get_planets") # Эндпоинт для получения списка всех планет с их координатами
def get_planets(req: BaseUserReq):
    user_id = req.user_id

    return game.get_planets(user_id)


@app.post("/set_target_planet") # Эндпоинт для установки цели планеты
def set_target_planet(req: planetReq):
    user_id = req.user_id
    target_planet_id = req.planet_id
    game.auth_user_db(user_id)
    game.select_cave(user_id, 0) # Если юзер выбирает планету, он автоматически выходит из шахты (если был в ней)
    return game.set_target_planet(user_id, target_planet_id)




@app.post("/get_cave")
def get_cave(req: BaseUserReq):
    user_id = req.user_id
    return game.get_caves(user_id)



@app.post("/get_user_coordinates")
def get_user_coordinates(req: BaseUserReq):
    user_id = req.user_id
    return game.get_user_coordinates(user_id)

@app.post("/choice_cave")
def choice_cave(req: CaveReq):
    user_id = req.user_id
    cave_id = req.cave_id
    return game.select_cave(user_id, cave_id)



@app.post("/unlock_cave")
def unlock_cave(req: CaveReq):
    user_id = req.user_id
    cave_id = req.cave_id
    return game.unlock_cave(user_id, cave_id)


@app.post("/get_cave_info")
def get_cave_info(req: CaveReq):
    cave_id = req.cave_id
    user_id = req.user_id
    return game.get_cave_info(user_id, cave_id)




@app.post("/get_create_items")
def get_create_items(req: BaseUserReq):
    return game.get_craft_list(req.user_id)



@app.post("/get_create_item_info")
def get_create_item_info(req: CraftReq):
    return game.get_craft_info(req.user_id, req.item_id)


@app.post("/create_item")
def create_item(req: CraftReq):
    return game.craft_item(req.user_id, req.item_id)

@app.post("/use_item")
def use_item(req: planetReq):
    user_id = req.user_id
    item_id = req.item_id
    return game.use_item(user_id, item_id)

@app.post("/mine_cave")
def mine(req: BaseUserReq):
    user_id = req.user_id
    return game.mine(user_id)



@app.post("/get_ship")
def get_ships(req: BaseUserReq):
    return game.get_ships(req.user_id)

# 2. Получить цену (инфо)
@app.post("/get_ship_info")
def get_ship_info(req: ShipReq):
    return game.get_ship_info(req.user_id, req.ship_id)

# 3. Купить (Разблокировать)
@app.post("/unlock_ship")
def unlock_ship(req: ShipReq):
    # Фронт может прислать item_id вместо ship_id, если класс DropdownManager так настроен.
    # Если используете мой последний DropdownManager, он шлет и то и другое.
    return game.unlock_ship(req.user_id, req.ship_id)

# 4. Выбрать (Сесть за штурвал)
@app.post("/choice_ship")
def select_ship(req: ShipReq):
    return game.select_ship(req.user_id, req.ship_id)
    



@app.on_event("startup")
async def startup_event():
    init_db.init_db()  # Инициализируем базу данных при запуске сервера
    #conn = sqlite3.connect(os.getenv("DB_NAME"))
    #cursor = conn.cursor()
    #cursor.execute("PRAGMA journal_mode=WAL")
    #cursor.execute("PRAGMA synchronous=NORMAL")
    #cursor.execute("PRAGMA busy_timeout=30000")
    #conn.commit()
    #conn.close()
    asyncio.create_task(worker_of_ivents.gift_worker())
    asyncio.create_task(worker_of_coordinate.coordinate_worker())
