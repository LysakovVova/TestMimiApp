import asyncio
import random
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()
DB_NAME = os.getenv("DB_NAME")

def init_planets():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Добавляем планеты с координатами
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (0, "космос", 0, 0)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (1, "Земля", 1, 1)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (2, "Марс", -1, -1)')
    
    conn.commit()
    conn.close()
def init_caves():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Добавляем пещеры для каждой планеты
    cursor.execute('INSERT OR IGNORE INTO caves (id, name, planet_id) VALUES (0, "Пещера 1", 0)')
    cursor.execute('INSERT OR IGNORE INTO caves (id, name, planet_id) VALUES (1, "Пещера 2", 1)')
    cursor.execute('INSERT OR IGNORE INTO caves (id, name, planet_id) VALUES (2, "Пещера 3", 2)')
    
    conn.commit()
    conn.close()
def init_items():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Добавляем предметы для каждой пещеры
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, cave_id, chance) VALUES (0, "Кристалл", 100, 0, 0.5)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, cave_id, chance) VALUES (1, "Руда", 50, 0, 0.7)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, cave_id, chance) VALUES (2, "Драгоценный камень", 200, 1, 0.3)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, cave_id, chance) VALUES (3, "Металл", 80, 1, 0.6)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, cave_id, chance) VALUES (4, "Редкий минерал", 150, 2, 0.4)')
    cursor.execute('INSERT OR IGNORE INTO items (id, name, price, cave_id, chance) VALUES (5, "Обычный камень", 20, 2, 0.8)')
    
    conn.commit()
    conn.close()

def init_requirements():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Добавляем требования для каждой пещеры
    cursor.execute('INSERT OR IGNORE INTO cave_requirements (cave_id, item_id, count) VALUES (0, 0, 1)')  # Для пещеры 1 нужно 1 Кристалл
    cursor.execute('INSERT OR IGNORE INTO cave_requirements (cave_id, item_id, count) VALUES (0, 1, 2)')  # Для пещеры 1 нужно 2 Руды
    cursor.execute('INSERT OR IGNORE INTO cave_requirements (cave_id, item_id, count) VALUES (1, 2, 1)')  # Для пещеры 2 нужно 1 Драгоценный камень
    cursor.execute('INSERT OR IGNORE INTO cave_requirements (cave_id, item_id, count) VALUES (1, 3, 3)')  # Для пещеры 2 нужно 3 Металла
    cursor.execute('INSERT OR IGNORE INTO cave_requirements (cave_id, item_id, count) VALUES (2, 4, 2)')  # Для пещеры 3 нужно 2 Редких минерала
    cursor.execute('INSERT OR IGNORE INTO cave_requirements (cave_id, item_id, count) VALUES (2, 5, 5)')  # Для пещеры 3 нужно 5 Обычных камней
    
    conn.commit()
    conn.close()

def init_db():
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
            currently_on_cave_id INTEGER DEFAULT 0,
            
            FOREIGN KEY (target_planet_id) REFERENCES planets(id),
            FOREIGN KEY (currently_on_planet_id) REFERENCES planets(id),
            FOREIGN KEY (currently_on_cave_id) REFERENCES caves(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER DEFAULT 0,
            cave_id INTEGER,
            chance REAL DEFAULT 0,
            FOREIGN KEY (cave_id) REFERENCES caves(id)
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

    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS caves (
            id INTEGER PRIMARY KEY,
            name TEXT,
            planet_id INTEGER,
            FOREIGN KEY (planet_id) REFERENCES planets(id)                
    )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unlock_caves (
            user_id INTEGER,
            cave_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (cave_id) REFERENCES caves(id),
            PRIMARY KEY (user_id, cave_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cave_requirements (
            cave_id INTEGER,
            item_id INTEGER,   -- ID ресурса (из таблицы items)
            count INTEGER,    -- Сколько нужно (например, 100)
            FOREIGN KEY(cave_id) REFERENCES caves(id),
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    ''')

    init_planets()  # Инициализируем планеты
    init_caves()  # Инициализируем пещеры
    init_items()  # Инициализируем предметы
    init_requirements()  # Инициализируем требования для пещер
    
    conn.commit()
    conn.close()