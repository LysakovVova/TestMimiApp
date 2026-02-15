import asyncio
import random
import sqlite3
import os
from dotenv import load_dotenv

import hmac, hashlib, time, json # 5. Импортируем модули для работы с криптографией, временем и JSON
from fastapi import FastAPI, HTTPException 
import random 
from pydantic import BaseModel 
from urllib.parse import parse_qsl 

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_user_balance(user_id: int): # Получаем баланс пользователя из базы данных
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


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
    return {"items": [{"name": name, "count": count} for name, count in items]}



def create_user(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)', (user_id, 0))
    
    conn.commit()
    conn.close()


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


def auth_user (initData : str):
    data = verify_init_data(initData)
    user = json.loads(data["user"])
    user_id = user["id"]

    create_user(user_id)
    balance = get_user_balance(user_id)
    if balance is None:
        return {"user_id": user_id, "balance": 0}
    return {"user_id": user_id, "balance": balance}



def get_active_offer(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_name, count FROM active_offers WHERE user_id = ?", (user_id,))
    offer = cursor.fetchone()
    conn.close()
    
    if offer:
        return {"has_offer": True, "item_id": offer[0], "name": offer[1], "count": offer[2]}
    else:
        return {"has_offer": False}


def accept_offer(user_id: int):    
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


def decline_offer(user_id: int):    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_offers WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return {"result": "success", "message": "Предложение отклонено"}

def get_planets(user_id: int):
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


def set_target_planet(user_id: int, target_planet_id: int):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

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


def unlock_cave(user_id: int, cave_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Какие ресурсы нужны?
    cursor.execute("SELECT item_id, count FROM cave_requirements WHERE cave_id = ?", (cave_id,))
    requirements = cursor.fetchall() # Список кортежей [(1, 100), (5, 50)]

    if not requirements:
        # Если требований нет, значит пещера бесплатная или ошибка
        pass 

    # 2. ПРОВЕРКА: Хватает ли у игрока ресурсов?
    for item_id, required_count in requirements:
        cursor.execute("SELECT count FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
        result = cursor.fetchone()
        user_has = result[0] if result else 0

        item_name = cursor.execute("SELECT name FROM items WHERE id = ?", (item_id,)).fetchone()[0]
        
        if user_has < required_count:
            conn.close()
            # Находим имя ресурса для красивой ошибки
            # (можно сделать отдельным запросом, но для простоты вернем ID)
            return {"status": "error", "message": f"Не хватает ресурса {item_name}!"}

    # 3. СПИСАНИЕ: Если мы здесь, значит всего хватает. Списываем.
    try:
        for item_id, required_count in requirements:
            cursor.execute('''
                UPDATE inventory SET count = count - ? 
                WHERE user_id = ? AND item_id = ?
            ''', (required_count, user_id, item_id))
            
        # 4. ОТКРЫВАЕМ ПЕЩЕРУ
        cursor.execute("INSERT INTO unlock_caves (user_id, cave_id) VALUES (?, ?)", (user_id, cave_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback() # Отменяем все изменения, если что-то сломалось
        return {"status": "error", "message": "Ошибка БД"}

    conn.close()
    return {"status": "ok", "message": "Пещера разблокирована!"}


def get_cave_info(cave_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT item_id, count FROM cave_requirements WHERE cave_id = ?", (cave_id,))
    requirements = cursor.fetchall() # Список кортежей [(1, 100), (5, 50)]
    
    if not requirements:
        conn.close()
        return {"requirements": []} # Пещера бесплатная или ошибка
    
    req_list = []
    for item_id, count in requirements:
        item_name = cursor.execute("SELECT name FROM items WHERE id = ?", (item_id,)).fetchone()[0]
        req_list.append({"item_id": item_id, "item_name": item_name, "count": count})

    conn.close()
    return {"requirements": req_list}

def get_cave(user_id: int, planet_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Получаем пещеры на планете
    cursor.execute('''
        SELECT caves.id, caves.name, 
               CASE WHEN unlock_caves.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_unlocked
        FROM caves
        LEFT JOIN unlock_caves ON caves.id = unlock_caves.cave_id AND unlock_caves.user_id = ?
        WHERE caves.planet_id = ?
    ''', (user_id, planet_id))
    
    caves = cursor.fetchall()
    conn.close()

    return {"caves": [{"id": c[0], "name": c[1], "is_unlocked": bool(c[2])} for c in caves]}

def get_used_coordinates(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    create_user(user_id)  # Убедимся, что пользователь есть в базе

    cursor.execute("SELECT coordinate_x, coordinate_y, currently_on_planet_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    planet_name = cursor.execute("SELECT name FROM planets WHERE id = (SELECT currently_on_planet_id FROM users WHERE user_id = ?)", (user_id,)).fetchone()
    conn.close()

    if result and result[2] != 0:
        return {"coordinate_x": result[0], "coordinate_y": result[1],"planet_name": planet_name[0]}
    else:
        return {"coordinate_x": result[0], "coordinate_y": result[1],"planet_name": None}


def get_user_planet(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT currently_on_planet_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

def choice_cave(user_id: int, cave_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Проверяем, разблокирована ли пещера для пользователя
    cursor.execute("SELECT 1 FROM unlock_caves WHERE user_id = ? AND cave_id = ?", (user_id, cave_id))
    if not cursor.fetchone():
        items = cursor.execute('''
            SELECT items.name, cave_requirements.count
            FROM cave_requirements
            JOIN items ON cave_requirements.item_id = items.id
            WHERE cave_requirements.cave_id = ?
        ''', (cave_id,)).fetchall()
        requirements_text = "\n".join([f"{count}x {name}" for name, count in items])

        conn.close()

        return {"status": "error", "message": f"Пещера не разблокирована! Необходимо:\n{requirements_text}"}

    # Если разблокирована, устанавливаем ее как текущую локацию пользователя
    cursor.execute("UPDATE users SET currently_on_cave_id = ? WHERE user_id = ?", (cave_id, user_id))  # Устанавливаем пещеру
    
    cave_name = cursor.execute("SELECT name FROM caves WHERE id = ?", (cave_id,)).fetchone()[0]
    conn.commit()
    conn.close()
    
    return {"status": "ok", "message": f"Вы вошли в пещеру {cave_name}!", "cave_name": cave_name}


def roll_independent(resources):
    result = []
    for item_id, chance, name in resources:
        if random.random() < chance:  # chance от 0 до 1
            result.append(name)
    return result


def mine(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Получаем текущую пещеру пользователя
    cursor.execute("SELECT currently_on_cave_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result or result[0] == 0:
        conn.close()
        return {"status": "error", "message": "Вы не находитесь в пещере!"}
    
    cave_id = result[0]

    if cave_id == 0:
        conn.close()
        return {"status": "error", "message": "Вы не находитесь в пещере!"}

    cave_name = cursor.execute("SELECT name FROM caves WHERE id = ?", (cave_id,)).fetchone()[0]

    # Получаем ресурсы, которые можно добыть в этой пещере
    cursor.execute("SELECT id, chance, name FROM items WHERE cave_id = ?", (cave_id,))
    resources = cursor.fetchall() # [(item_id, chance, name), ...]

    if not resources:
        conn.close()
        return {"status": "error", "message": "В этой пещере нет ресурсов для добычи!"}

    result_items = {}
    for _ in range(5):
        for item_name in roll_independent(resources):
            result_items[item_name] = result_items.get(item_name, 0) + 1

    conn.close()
    return {
    "status": "ok",
    "mined_items": [{"item_name": k, "count": v} for k, v in result_items.items()],
    "cave_name": cave_name
    }