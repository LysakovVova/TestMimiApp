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
        await asyncio.sleep(30) 
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Берем всех юзеров
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        
        # Список возможных подарков (id, name)
        possible_gifts = cursor.execute("SELECT id, name FROM items").fetchall()
        
        for user in users:
            user_id = user[0]
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