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
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (2, "Меркурий", -1, -1)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (3, "Венера", 1, -1)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (4, "Марс", 2, 2)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (5, "Юпитер", 3, -3)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (6, "Сатурн", 3, 3)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (7, "Уран", 4, 4)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (8, "Нептун", -4, 4)')
    cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (9, "Плутон", 5, 5)')

    
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
def item_space():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Добавляем предметы для космоса (планета_id = 0)
    # rank 1
    range_1_items = [
        (0, "Металлические фрагменты", 0, 1),
        (1, "Проводящие пластины", 0, 1),
        (2, "Обгоревшие микросхемы", 0, 1),
        (3, "Топливные баки-осколки", 0, 1),
        (4, "Разрушенные панели", 0, 1),
    ]
    range_2_items = [
        (5, "Ионные катушки", 0, 2),
        (6, "Повреждённые навигационные ядра", 0, 2),
        (7, "Кристаллы стабилизации", 0, 2),
        (8, "Фрагменты гиперсплава", 0, 2),
        (9, "Реакторные оболочки", 0, 2),
    ]
    range_3_items = [
        (10, "Ядро древнего дрона", 0, 3),
        (11, "Осколок варп-кольца", 0, 3),
        (12, "Стабилизатор сингулярности", 0, 3),
        (13, "Тёмный энергетический модуль", 0, 3),
        (14, "Хроно-фрагмент", 0, 3),
    ]
    range_4_items = [
        (15, "Фрагмент портального двигателя", 0, 4),
        (16, "Сердечник неизвестного крейсера", 0, 4),
        (17, "Кристалл искажённого пространства", 0, 4),
        (18, "Омни-процессор", 0, 4),
        (19, "Обломок межзвёздного ковчега", 0, 4),
    ]
    for item in range_1_items + range_2_items + range_3_items + range_4_items:
        cursor.execute('INSERT OR IGNORE INTO items (id, name, cave_id, range) VALUES (?, ?, ?, ?)', item)
    conn.commit()
    conn.close()
def init_items():
    item_space()  # Инициализируем предметы для космоса
def init_spaceship():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Инициализируем данные для космического корабля (можно добавить больше кораблей и их требований)

    ships =[
        ("Орбитальный Кораблт",       1, 1, 200),
        ("Тяжёлый носитель",          2, 1, 400),
        ("Межпланетный корабль",      3, 2, 400),
        ("Гипердвигательный корабль", 4, 2, 600),
        ("Межзвёздный крейсер",       5, 3, 800),
    ]

    for ship in ships:
        cursor.execute('INSERT OR IGNORE INTO spaceship (name, ship_id, speed, carrying_capacity) VALUES (?, ?, ?, ?)', ship)


    
    conn.commit()
    conn.close()

def init_requirements():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    craft_recipes = [
        # range 2 из range 1
        (5, 0, 5),
        (5, 1, 5),
        (6, 1, 5),
        (6, 2, 5),
        (7, 2, 5),
        (7, 3, 5),
        (8, 3, 5),
        (8, 4, 5),
        (9, 0, 4),
        (9, 4, 6),

        # range 3 из range 2
        (10, 5, 3),
        (10, 6, 2),
        (11, 6, 3),
        (11, 7, 2),
        (12, 7, 3),
        (12, 8, 2),
        (13, 8, 3),
        (13, 9, 2),
        (14, 5, 2),
        (14, 9, 3),

        # range 4 из range 3
        (15, 10, 2),
        (15, 11, 2),
        (16, 11, 2),
        (16, 12, 2),
        (17, 12, 2),
        (17, 13, 2),
        (18, 13, 2),
        (18, 14, 2),
        (19, 10, 1),
        (19, 14, 3),
    ]

    for recipe in craft_recipes:
        cursor.execute(
            'INSERT OR IGNORE INTO item_requirements (item_id, required_item_id, count) VALUES (?, ?, ?)',
            recipe,
        )

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
            space_ship_id INTEGER DEFAULT 0,
            
            FOREIGN KEY (space_ship_id) REFERENCES spaceship(ship_id),
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
            range INTEGER DEFAULT 0,
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
            FOREIGN KEY(item_id) REFERENCES items(id),
            PRIMARY KEY (cave_id, item_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spaceship (
            name TEXT,
            ship_id INTEGER PRIMARY KEY,
            speed INTEGER DEFAULT 1,
            carrying_capacity INTEGER DEFAULT 200
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spaceship_requirements (
            ship_id INTEGER,
            item_id INTEGER,
            count INTEGER,
            FOREIGN KEY (ship_id) REFERENCES spaceship(ship_id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            PRIMARY KEY (ship_id, item_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unlock_spaceship (
            user_id INTEGER,
            ship_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (ship_id) REFERENCES spaceship(ship_id),
            PRIMARY KEY (user_id, ship_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_requirements (
            item_id INTEGER,
            required_item_id INTEGER,
            count INTEGER,
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (required_item_id) REFERENCES items(id),
            PRIMARY KEY (item_id, required_item_id)
        )
    ''')

    init_planets()  # Инициализируем планеты
    init_caves()  # Инициализируем пещеры
    init_items()  # Инициализируем предметы
    init_requirements()  # Инициализируем требования для пещер
    init_spaceship()  # Инициализируем данные для космического корабля
    
    conn.commit()
    conn.close()
