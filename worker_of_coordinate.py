import asyncio
import random
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()
DB_NAME = os.getenv("DB_NAME")

async def coordinate_worker():
    while True:
        await asyncio.sleep(10) 
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Берем всех юзеров
        cursor.execute("SELECT user_id, target_planet_id FROM users")
        users = cursor.fetchall()
        
        for user in users:
            user_id = user[0]
            target_planet_id = user[1]

            if (target_planet_id == 0):
                continue  # Если у пользователя нет цели, пропускаем его

            target_x, target_y = cursor.execute("SELECT coordinate_x, coordinate_y FROM planets WHERE id = ?", (target_planet_id,)).fetchone()
            user_x, user_y = cursor.execute("SELECT coordinate_x, coordinate_y FROM users WHERE user_id = ?", (user_id,)).fetchone()
            
            # Двигаем пользователя на 1 единицу в направлении планеты
            if user_x < target_x:
                new_x = user_x + 1
            elif user_x > target_x:
                new_x = user_x - 1
            else:
                new_x = user_x

            if user_y < target_y:
                new_y = user_y + 1
            elif user_y > target_y:
                new_y = user_y - 1
            else:
                new_y = user_y

            if (new_x == target_x) and (new_y == target_y):
                cursor.execute("UPDATE users SET target_planet_id = 0 WHERE user_id = ?", (user_id,))  # Сбрасываем цель

            cursor.execute("UPDATE users SET coordinate_x = ?, coordinate_y = ? WHERE user_id = ?", (new_x, new_y, user_id))
        
        conn.commit()
        conn.close()