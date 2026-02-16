import asyncio
import random
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()
DB_NAME = os.getenv("DB_NAME")

async def gift_worker():
    while True:
        # 1. Ждем 10 секунд перед следующей раздачей (для теста, потом поставь больше)
        await asyncio.sleep(600)  # 600 секунд = 10 минут
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Берем всех юзеров
        cursor.execute("SELECT user_id, coordinate_x, coordinate_y, currently_on_planet_id FROM users")
        users = cursor.fetchall()
        
        # Список возможных подарков (id, name, planet_id)
        
        for user in users:
            user_id = user[0]
            user_coordinates = (user[1], user[2])
            currently_on_planet_id = user[3]

            if currently_on_planet_id != 0:
                continue  # Если юзер не на планете, пропускаем его

            # Список возможных подарков (id, name, planet_id)

            range = 1

            if (max(abs(user_coordinates[0]), abs(user_coordinates[1])) > 0):  # 0-10
                range = 1
            if (max(abs(user_coordinates[0]), abs(user_coordinates[1])) > 10):  # 10-20
                range = 2
            if (max(abs(user_coordinates[0]), abs(user_coordinates[1])) > 20):  # 20-30
                range = 3
            if (max(abs(user_coordinates[0]), abs(user_coordinates[1])) > 30):  # -30 и дальше
                range = 4

            possible_gifts = cursor.execute("SELECT id, name, cave_id, range FROM items WHERE cave_id = ? AND range <= ?", (0, range)).fetchall()
            
            gift = random.choice(possible_gifts)
            
            # Сначала удаляем старое (оно сгорает!)
            cursor.execute("DELETE FROM active_offers WHERE user_id = ?", (user_id,))
            
            if random.random() > 0:
                count = random.randint(1, 3) # Количество подарков от 1 до 3
                cursor.execute(
                    "INSERT INTO active_offers (user_id, item_id, item_name, count) VALUES (?, ?, ?, ?)", 
                    (user_id, gift[0], gift[1], count)
                )
                print(f"Игроку {user_id} выпал {count}x {gift[1]}")
        
        conn.commit()
        conn.close()