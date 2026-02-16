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
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME, timeout=30)
            cursor = conn.cursor()
            cursor.execute("PRAGMA busy_timeout = 30000")

            # Берем всех юзеров
            cursor.execute("SELECT user_id, coordinate_x, coordinate_y, currently_on_planet_id FROM users")
            users = cursor.fetchall()

            for user in users:
                user_id = user[0]
                user_coordinates = (user[1], user[2])
                currently_on_planet_id = user[3]

                if currently_on_planet_id != 0:
                    continue  # Если юзер не на планете, пропускаем его

                gift_range = 1

                if max(abs(user_coordinates[0]), abs(user_coordinates[1])) > 0:  # 0-10
                    gift_range = 1
                if max(abs(user_coordinates[0]), abs(user_coordinates[1])) > 10:  # 10-20
                    gift_range = 2
                if max(abs(user_coordinates[0]), abs(user_coordinates[1])) > 20:  # 20-30
                    gift_range = 3
                if max(abs(user_coordinates[0]), abs(user_coordinates[1])) > 30:  # -30 и дальше
                    gift_range = 4

                possible_gifts = cursor.execute(
                    "SELECT id, name, cave_id, range FROM items WHERE cave_id = ? AND range <= ?",
                    (0, gift_range),
                ).fetchall()
                if not possible_gifts:
                    continue

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
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[gift_worker] error: {e}")
        finally:
            if conn:
                conn.close()
