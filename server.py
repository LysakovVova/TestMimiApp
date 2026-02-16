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


app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN")

class AuthReq(BaseModel):
    initData: str



@app.post("/auth") # Эндпоинт для аутентификации пользователя, который принимает данные от Telegram и возвращает результат аутентификации
def auth(req: AuthReq):
    return user_action.auth_user(req.initData)



class RangeReq(BaseModel):
    user_id: int

@app.post("/get_inventory") # Эндпоинт, который принимает идентификатор пользователя и возвращает его инвентарь
def number_range(req: RangeReq):
    inventory = user_action.get_user_inventory(req.user_id)
    return inventory

class offerReq(BaseModel):
    user_id: int

@app.post("/check_offer") # Эндпоинт для получения активных предложений для пользователя
def get_offers(req: offerReq):
    user_id = req.user_id
    return user_action.get_active_offer(user_id)
    
    
@app.post("/accept_offer") # Эндпоинт для принятия предложения, который принимает идентификатор пользователя и идентификатор предмета, который он хочет принять
def accept_offer(req: offerReq):
    user_id = req.user_id  
    return user_action.accept_offer(user_id)

@app.post("/decline_offer") # Эндпоинт для отклонения предложения, который принимает идентификатор пользователя и удаляет активное предложение
def decline_offer(req: offerReq):
    user_id = req.user_id
    
    return user_action.decline_offer(user_id)


@app.post("/get_planets") # Эндпоинт для получения списка всех планет с их координатами
def get_planets(req: offerReq):
    user_id = req.user_id

    return user_action.get_planets(user_id)

class target_planetReq(BaseModel):
    user_id: int
    target_planet_id: int

@app.post("/set_target_planet") # Эндпоинт для установки цели планеты
def set_target_planet(req: target_planetReq):
    user_id = req.user_id
    target_planet_id = req.target_planet_id
    user_action.create_user(user_id) # Создаем пользователя, если его нет в базе данных
    return user_action.set_target_planet(user_id, target_planet_id)

class unlock_caveReq(BaseModel):
    user_id: int
    cave_id: int

class get_caveReg(BaseModel):
    user_id: int
@app.post("/get_cave")
def get_cave(req: get_caveReg):
    user_id = req.user_id
    planet_id = user_action.get_user_planet(user_id)
    return user_action.get_cave(user_id, planet_id)

class get_shipReg(BaseModel):
    user_id: int
@app.post("/get_ship")
def get_ship(req: get_shipReg):
    user_id = req.user_id
    return user_action.get_ships(user_id)

@app.post("/get_used_coordinates")
def get_used_coordinates(req: offerReq):
    user_id = req.user_id
    return user_action.get_used_coordinates(user_id)

@app.post("/choice_cave")
def choice_cave(req: unlock_caveReq):
    user_id = req.user_id
    cave_id = req.cave_id
    return user_action.choice_cave(user_id, cave_id)

class unlock_shipReq(BaseModel):
    user_id: int
    ship_id: int

@app.post("/choice_ship")
def choice_ship(req: unlock_shipReq):
    user_id = req.user_id
    ship_id = req.ship_id
    return user_action.choice_ship(user_id, ship_id)

@app.post("/unlock_cave")
def unlock_cave(req: unlock_caveReq):
    user_id = req.user_id
    cave_id = req.cave_id
    return user_action.unlock_cave(user_id, cave_id)



@app.post("/unlock_ship")
def unlock_ship(req: unlock_shipReq):
    user_id = req.user_id
    ship_id = req.ship_id
    return user_action.unlock_ship(user_id, ship_id)

@app.post("/get_cave_info")
def get_cave_info(req: unlock_caveReq):
    user_id = req.user_id
    cave_id = req.cave_id
    return user_action.get_cave_info(cave_id)

class unlock_shipReq(BaseModel):
    ship_id: int

@app.post("/get_ship_info")
def get_ship_info(req: unlock_shipReq):
    ship_id = req.ship_id
    return user_action.get_ship_info(ship_id)


class createItemListReq(BaseModel):
    user_id: int


@app.post("/get_create_items")
def get_create_items(req: createItemListReq):
    return user_action.get_create_items(req.user_id)


class createItemInfoReq(BaseModel):
    user_id: int
    item_id: int


@app.post("/get_create_item_info")
def get_create_item_info(req: createItemInfoReq):
    return user_action.get_create_item_info(req.item_id, req.user_id)


@app.post("/create_item")
def create_item(req: createItemInfoReq):
    return user_action.create_item(req.user_id, req.item_id)

@app.post("/use_item")
def use_item(req: unlock_caveReq):
    user_id = req.user_id
    item_id = req.cave_id
    return user_action.use_item(user_id, item_id)

@app.post("/mine_cave")
def mine(req: get_caveReg):
    user_id = req.user_id
    return user_action.mine(user_id)
    



@app.on_event("startup")
async def startup_event():
    init_db.init_db()  # Инициализируем базу данных при запуске сервера
    conn = sqlite3.connect(os.getenv("DB_NAME"))
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    conn.commit()
    conn.close()
    asyncio.create_task(worker_of_ivents.gift_worker())
    asyncio.create_task(worker_of_coordinate.coordinate_worker())
