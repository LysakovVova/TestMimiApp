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
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME, timeout=30)
            cursor = conn.cursor()
            cursor.execute("PRAGMA busy_timeout = 30000")

            # Берем всех юзеров
            cursor.execute("SELECT user_id, target_planet_id, space_ship_id FROM users")
            users = cursor.fetchall()

            for user in users:
                user_id = user[0]
                target_planet_id = user[1]
                space_ship_id = user[2]

                if space_ship_id == 0:
                    continue  # Если у пользователя нет корабля, пропускаем его

                ship_speed_row = cursor.execute(
                    "SELECT speed FROM spaceship WHERE ship_id = ?",
                    (space_ship_id,),
                ).fetchone()
                if not ship_speed_row:
                    continue
                space_speed = ship_speed_row[0]

                if target_planet_id == 0:
                    continue  # Если у пользователя нет цели, пропускаем его

                target_row = cursor.execute(
                    "SELECT coordinate_x, coordinate_y FROM planets WHERE id = ?",
                    (target_planet_id,),
                ).fetchone()
                user_row = cursor.execute(
                    "SELECT coordinate_x, coordinate_y FROM users WHERE user_id = ?",
                    (user_id,),
                ).fetchone()
                if not target_row or not user_row:
                    continue
                target_x, target_y = target_row
                user_x, user_y = user_row

                # Двигаем пользователя на 1 единицу в направлении планеты
                if user_x < target_x:
                    new_x = user_x + 1 * space_speed
                    new_x = min(new_x, target_x)  # Не превышаем координату планеты
                elif user_x > target_x:
                    new_x = user_x - 1 * space_speed
                    new_x = max(new_x, target_x)  # Не превышаем координату планеты
                else:
                    new_x = user_x

                if user_y < target_y:
                    new_y = user_y + 1 * space_speed
                    new_y = min(new_y, target_y)  # Не превышаем координату планеты
                elif user_y > target_y:
                    new_y = user_y - 1 * space_speed
                    new_y = max(new_y, target_y)  # Не превышаем координату планеты
                else:
                    new_y = user_y

                if new_x == target_x and new_y == target_y:
                    # Пользователь достиг планеты, обновляем его текущее местоположение
                    cursor.execute(
                        "UPDATE users SET currently_on_planet_id = ? WHERE user_id = ?",
                        (target_planet_id, user_id),
                    )

                cursor.execute(
                    "UPDATE users SET coordinate_x = ?, coordinate_y = ? WHERE user_id = ?",
                    (new_x, new_y, user_id),
                )

            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[coordinate_worker] error: {e}")
        finally:
            if conn:
                conn.close()
