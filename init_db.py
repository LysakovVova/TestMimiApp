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

    planet_items = [
    (0, "Космос", 0, 0),
    (1, "Земля", 5, 5),
    (2, "Меркурий", -10, -10),
    (3, "Венера", 10, -10),
    (4, "Марс", 20, 20),
    (5, "Юпитер", 30, -30),
    (6, "Сатурн", 30, 30),
    (7, "Уран", 40, 40),
    (8, "Нептун", -40, 40),
    (9, "Плутон", 50, 50),
    ]
    for planet in planet_items:
        cursor.execute('INSERT OR IGNORE INTO planets (id, name, coordinate_x, coordinate_y) VALUES (?, ?, ?, ?)', planet)

    
    conn.commit()
    conn.close()
def init_caves():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    all_caves = [
    (1, "Горнодобывающий комбинат «Терра-Майн»", 1),
    (2, "Нефтегазовый комплекс «ГеоЭнерго»", 1),
    (3, "Металлургический завод «ТитанПром»", 1),
    (4, "Кремниевый технопарк «Силикат»", 1),
    (5, "Химический завод «Атмос»", 1),
    (6, "Композитный завод «ОрбитФайбер»", 1),
    (7, "Гелиошахта «Перигелий»", 2),
    (8, "Солнечная плавильня «Фотон-9»", 2),
    (9, "Сборочная станция «Радиант»", 2),
    (10, "Лавовый экстрактор «Пирогранит»", 2),
    (11, "Облачная платформа «Аэрис»", 3),
    (12, "Кислотный перерабатывающий комплекс «Вулканис»", 3),
    (13, "Плавильный купол «Инферно»", 3),
    (14, "Парниковая шахта «Ксенос»", 3),
    (15, "Реголитовая шахта «Арес-1»", 6),
    (16, "Полярная станция «КриоМарс»", 6),
    (17, "Базальтовый карьер «Олимп»", 6),
    (18, "Кремниевый экстрактор «Пыльник»", 6),
    (19, "Атмосферная станция «Зевс»", 7),
    (20, "Плавучий переработчик «Гелион»", 7),
    (21, "Вихревой реактор «Буря»", 7),
    (22, "Давильный комплекс «Глубина»", 7),
    (23, "Кольцевая добывающая станция «Ринг-1»", 8),
    (24, "Метановый переработчик «Титан»", 8),
    (25, "Ледяной экстрактор «Энцелад»", 8),
    (26, "Гравитационная шахта «Хронос»", 8),
    (27, "Криостанция «Бирюза»", 9),
    (28, "Газовый коллектор «Ось»", 9),
    (29, "Полярный реактор «Дейтер»", 9),
    (30, "Ледяная платформа «Ураниум»", 9),
    (31, "Глубинная станция «Тритон»", 10),
    (32, "Штормовой коллектор «Синий Вихрь»", 10),
    (33, "Алмазная платформа «Буря-Н»", 10),
    (34, "Плазменный экстрактор «Посейдон»", 10),
    (35, "Криошахта «Харон»", 11),
    (36, "Азотная станция «Никта»", 11),
    (37, "Поясная добывающая база «Край»", 11),
    (38, "Дальняя лаборатория «Метакристалл»", 11),
    ]

    for cave in all_caves:
        cursor.execute('INSERT OR IGNORE INTO caves (id, name, planet_id) VALUES (?, ?, ?)', cave)
    
    conn.commit()
    conn.close()

def item_space():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Добавляем предметы для космоса (планета_id = 0)
    # rank 1
    range_1_items = [
        (86, "Металлические фрагменты", 0, 1),
        (87, "Проводящие пластины", 0, 1),
        (88, "Обгоревшие микросхемы", 0, 1),
        (89, "Топливные баки-осколки", 0, 1),
        (90, "Разрушенные панели", 0, 1),
    ]
    range_2_items = [
        (91, "Ионные катушки", 0, 2),
        (92, "Повреждённые навигационные ядра", 0, 2),
        (93, "Кристаллы стабилизации", 0, 2),
        (94, "Фрагменты гиперсплава", 0, 2),
        (95, "Реакторные оболочки", 0, 2),
    ]
    range_3_items = [
        (96, "Ядро древнего дрона", 0, 3),
        (97, "Осколок варп-кольца", 0, 3),
        (98, "Стабилизатор сингулярности", 0, 3),
        (99, "Тёмный энергетический модуль", 0, 3),
        (100, "Хроно-фрагмент", 0, 3),
    ]
    range_4_items = [
        (101, "Фрагмент портального двигателя", 0, 4),
        (102, "Сердечник неизвестного крейсера", 0, 4),
        (103, "Кристалл искажённого пространства", 0, 4),
        (104, "Омни-процессор", 0, 4),
        (105, "Обломок межзвёздного ковчега", 0, 4),
    ]
    for item in range_1_items + range_2_items + range_3_items + range_4_items:
        cursor.execute('INSERT OR IGNORE INTO items (id, name, cave_id, range) VALUES (?, ?, ?, ?)', item)
    conn.commit()
    conn.close()

def item_palnet():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    items_from_caves = [
    (0, "Железо", 0, 1, 0.32),
    (1, "Медь", 0, 1, 0.2),
    (2, "Никель", 0, 1, 0.13),
    (3, "Камень", 0, 1, 0.1),
    (4, "Кобальт", 0, 1, 0.07),
    (5, "Обсидиан", 0, 1, 0.03),
    (6, "Литий", 0, 1, 0.06),
    (7, "Палладий", 0, 1, 0.03),
    (8, "Уран", 0, 1, 0.02),
    (9, "Золото", 0, 1, 0.02),
    (10, "Платина", 0, 1, 0.01),
    (11, "Алмазы", 0, 1, 0.01),
    (12, "Нефть", 0, 2, 0.4),
    (13, "Газ", 0, 2, 0.35),
    (14, "Керосин", 0, 2, 0.25),
    (15, "Сталь", 0, 3, 0.45),
    (16, "Алюминий", 0, 3, 0.35),
    (17, "Титан", 0, 3, 0.2),
    (18, "Кремний", 0, 4, 0.5),
    (19, "Редкоземельные элементы", 0, 4, 0.35),
    (20, "Квантовый процессор", 0, 4, 0.15),
    (21, "Кислород", 0, 5, 0.55),
    (22, "Водород", 0, 5, 0.45),
    (23, "Композитное волокно", 0, 6, 0.6),
    (24, "Углепластик", 0, 6, 0.4),
    (25, "Гелиокристалл", 0, 7, 0.6),
    (26, "Короний", 0, 7, 0.4),
    (27, "Солнечный феррит", 0, 8, 0.7),
    (28, "Термоний", 0, 8, 0.3),
    (29, "Радиантовая пыль", 0, 9, 0.55),
    (30, "Светозарная слюда", 0, 9, 0.45),
    (31, "Пирогранит", 0, 10, 1),
    (32, "Аэросеребро", 0, 11, 0.45),
    (33, "Туманит", 0, 11, 0.55),
    (34, "Венерианская кислота", 0, 12, 0.7),
    (35, "Серный обсидиан", 0, 12, 0.3),
    (36, "Пламенный кварц", 0, 13, 0.6),
    (37, "Карбониум плотный", 0, 13, 0.4),
    (38, "Облачный ксенолит", 0, 14, 1),
    (39, "Реголит", 0, 15, 0.7),
    (40, "Красный ферроксид", 0, 15, 0.3),
    (41, "Полярный криолит", 0, 16, 0.45),
    (42, "Подповерхностный лед", 0, 16, 0.55),
    (43, "Марсианский базальтин", 0, 17, 0.9),
    (44, "Уран", 0, 17, 0.1),
    (45, "Пылевой кремний", 0, 18, 0.75),
    (46, "Оксидар", 0, 18, 0.25),
    (47, "Штормовой водород", 0, 19, 0.8),
    (48, "Грозовой неон", 0, 19, 0.2),
    (49, "Юпитерианский гелионий", 0, 20, 1),
    (50, "Вихревой плазмат", 0, 21, 1),
    (51, "Аммиачный конденсат", 0, 22, 0.75),
    (52, "Давление-кристалл", 0, 22, 0.25),
    (53, "Кольцевой ледонит", 0, 23, 0.4),
    (54, "Кольцевая пыль", 0, 23, 0.6),
    (55, "Сатурнианский метанит", 0, 24, 0.65),
    (56, "Титановый углевод", 0, 24, 0.35),
    (57, "Энцеладский криогель", 0, 25, 1),
    (58, "Гравиолед", 0, 26, 1),
    (59, "Криометан", 0, 27, 0.65),
    (60, "Лазурный аммиакит", 0, 27, 0.35),
    (61, "Осевой ксеногаз", 0, 28, 0.6),
    (62, "Бирюзовый гидрид", 0, 28, 0.4),
    (63, "Полярный дейтерит", 0, 29, 0.7),
    (64, "Ионный концентрат", 0, 29, 0.3),
    (65, "Ураниум-лед", 0, 30, 1),
    (66, "Глубинный тритонит", 0, 31, 0.45),
    (67, "Океанит", 0, 31, 0.55),
    (68, "Ветровой дейтерий", 0, 32, 1),
    (69, "Алмазный дождь", 0, 33, 0.5),
    (70, "Плазменный инжектор", 0, 33, 0.5),
    (71, "Синий плазмид", 0, 34, 0.55),
    (72, "Нептунианский гидрокристалл", 0, 34, 0.45),
    (73, "Плутонианский криошпат", 0, 35, 0.55),
    (74, "Харонит", 0, 35, 0.45),
    (75, "Теневой азотит", 0, 36, 0.6),
    (76, "Замёрзший аргонит", 0, 36, 0.4),
    (77, "Поясной ледяник", 0, 37, 1),
    (78, "Дальний метакристалл", 0, 38, 1),


    (79, "Гиперсплав", 0, 100, 1),
    (80, "Навигационный кристалл", 0, 100, 1),
    (81, "Термощитовой сплав", 0, 100, 1),
    (82, "Антиматерийный контейнер", 0, 100, 1),
    (83, "Антиматерия", 0, 100, 1),
    (84, "Омни-процессор", 0, 100, 1),
    (85, "Нуль-гравитационный модуль", 0, 100, 1)

]
    for item in items_from_caves:
        cursor.execute('INSERT OR IGNORE INTO items (id, name, price, cave_id, chance) VALUES (?, ?, ?, ?, ?)', item)

    
    conn.commit()
    conn.close()

def init_items():
    item_space()  # Инициализируем предметы для космоса
    item_palnet()  # Инициализируем предметы для планетч

def cave_requirements():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cave_requirements_items = [
    (2, 0, 220),
    (2, 1, 140),
    (2, 2, 90),
    (2, 3, 120),

    (3, 0, 260),
    (3, 12, 160),
    (3, 2, 120),
    (3, 4, 60),

    (4, 15, 200),
    (4, 1, 140),
    (4, 14, 120),
    (4, 9, 6),
    (4, 10, 4),

    (5, 0, 180),
    (5, 1, 130),
    (5, 2, 90),
    (5, 17, 4),

    (6, 16, 240),
    (6, 18, 160),
    (6, 2, 120),
    (6, 5, 25),
    (6, 19, 2),

    (8, 15, 32),
    (8, 16, 14),
    (8, 18, 11),
    (8, 24, 6),
    (8, 25, 3),
    (8, 26, 2),

    (9, 27, 25),
    (9, 26, 18),
    (9, 18, 13),
    (9, 19, 4),

    (10, 15, 30),
    (10, 17, 11),
    (10, 5, 7),
    (10, 30, 7),
    (10, 28, 3),

    (12, 15, 34),
    (12, 32, 16),
    (12, 4, 9),
    (12, 5, 11),
    (12, 18, 9),

    (13, 33, 39),
    (13, 16, 20),
    (13, 17, 14),
    (13, 35, 13),
    (13, 31, 4),
    (13, 28, 3),

    (14, 36, 25),
    (14, 16, 16),
    (14, 18, 11),
    (14, 29, 5),
    (14, 33, 4),

    (16, 15, 30),
    (16, 17, 13),
    (16, 27, 11),
    (16, 24, 9),
    (16, 39, 42),
    (16, 38, 80),
    (16, 31, 70),
    (16, 2, 90),
    (16, 36, 20),

    (17, 15, 34),
    (17, 28, 20),
    (17, 17, 11),
    (17, 18, 9),
    (17, 39, 56),
    (17, 3, 42),
    (17, 0, 180),
    (17, 1, 130),
    (17, 4, 60),

    (18, 29, 28),
    (18, 16, 21),
    (18, 18, 20),
    (18, 19, 4),
    (18, 39, 49),
    (18, 43, 40),
    (18, 1, 130),
    (18, 2, 100),
    (18, 4, 60),

    (20, 45, 26),
    (20, 18, 28),
    (20, 47, 160),
    (20, 48, 60),
    (20, 80, 6),
    (20, 39, 120),
    (20, 46, 18),
    (20, 41, 20),

    (21, 24, 28),
    (21, 18, 20),
    (21, 20, 3),
    (21, 47, 140),
    (21, 48, 50),
    (21, 81, 8),

    (22, 17, 24),
    (22, 18, 18),
    (22, 47, 120),
    (22, 48, 40),
    (22, 39, 100),
    (22, 43, 22),

    (24, 17, 20),
    (24, 18, 18),
    (24, 4, 7),
    (24, 54, 70),
    (24, 53, 30),
    (24, 51, 60),
    (24, 52, 8),

    (25, 17, 18),
    (25, 18, 16),
    (25, 24, 18),
    (25, 53, 60),
    (25, 42, 80),
    (25, 41, 18),

    (26, 17, 22),
    (26, 18, 16),
    (26, 54, 90),
    (26, 52, 10),
    (26, 49, 18),
    (26, 28, 6),

    (28, 79, 13),
    (28, 17, 26),
    (28, 18, 22),
    (28, 20, 3),
    (28, 58, 16),
    (28, 54, 140),
    (28, 52, 20),
    (28, 51, 90),

    (29, 81, 14),
    (29, 17, 28),
    (29, 18, 20),
    (29, 8, 3),
    (29, 58, 12),
    (29, 53, 90),
    (29, 49, 22),

    (30, 17, 26),
    (30, 18, 18),
    (30, 24, 24),
    (30, 59, 120),
    (30, 60, 60),
    (30, 54, 120),
    (30, 52, 16),

    (32, 79, 20),
    (32, 17, 26),
    (32, 18, 22),
    (32, 64, 40),
    (32, 61, 40),
    (32, 62, 30),
    (32, 52, 18),

    (33, 17, 28),
    (33, 18, 24),
    (33, 24, 26),
    (33, 64, 60),
    (33, 68, 70),
    (33, 58, 14),
    (33, 54, 120),

    (34, 81, 18),
    (34, 17, 30),
    (34, 18, 26),
    (34, 20, 3),
    (34, 68, 90),
    (34, 52, 22),
    (34, 66, 60),

    (36, 17, 22),
    (36, 18, 22),
    (36, 20, 3),
    (36, 71, 80),
    (36, 68, 80),
    (36, 72, 40),
    (36, 61, 50),
    (36, 52, 24),
    (36, 54, 220),
    (36, 48, 120),

    (37, 17, 24),
    (37, 18, 24),
    (37, 24, 26),
    (37, 69, 50),
    (37, 70, 50),
    (37, 64, 70),
    (37, 54, 240),
    (37, 48, 120),
    (37, 83, 1),

    (38, 79, 22),
    (38, 17, 24),
    (38, 18, 26),
    (38, 20, 4),
    (38, 82, 2),
    (38, 72, 50),
    (38, 52, 30),
    (38, 71, 90),
    (38, 68, 90),
    (38, 54, 260),
    (38, 84, 1)
    ]
    for requirement in cave_requirements_items:
        cursor.execute(
            'INSERT OR IGNORE INTO cave_requirements (cave_id, item_id, count) VALUES (?, ?, ?)',
            requirement
        )
    conn.commit()
    conn.close()

def init_spaceship():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Инициализируем данные для космического корабля (можно добавить больше кораблей и их требований)

    ships =[
        ("Орбитальный Корабль",       1, 1, 200),
        ("Тяжёлый носитель",          2, 1, 400),
        ("Межпланетный корабль",      3, 2, 400),
        ("Гипердвигательный корабль", 4, 2, 600),
        ("Межзвёздный крейсер",       5, 3, 800)
    ]

    for ship in ships:
        cursor.execute('INSERT OR IGNORE INTO spaceship (name, ship_id, speed, carrying_capacity) VALUES (?, ?, ?, ?)', ship)


    
    conn.commit()
    conn.close()

def init_requirements():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    craft_recipes = [
    (79, 15, 20),
    (79, 17, 10),
    (79, 2, 6),
    (79, 19, 4),
    (79, 24, 5),

    (80, 18, 30),
    (80, 25, 6),
    (80, 36, 10),
    (80, 19, 8),

    (81, 15, 25),
    (81, 37, 8),
    (81, 35, 10),
    (81, 17, 8),

    (82, 20, 4),
    (82, 72, 6),
    (82, 52, 2),

    (83, 71, 30),
    (83, 68, 40),
    (83, 52, 4),

    (84, 20, 6),
    (84, 64, 20),
    (84, 52, 6),
    (84, 71, 25),
    ]


    for recipe in craft_recipes:
        cursor.execute(
            'INSERT OR IGNORE INTO item_requirements (item_id, required_item_id, count) VALUES (?, ?, ?)',
            recipe,
        )

    conn.commit()
    conn.close()

def ship_requirements():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    ship_requirements = [

    (2, 15, 200),
    (2, 17, 120),
    (2, 16, 150),
    (2, 2, 70),
    (2, 4, 60),
    (2, 24, 100),
    (2, 22, 400),
    (2, 21, 400),
    (2, 14, 300),
    (2, 7, 25),
    (2, 6, 40),

    (3, 79, 60),
    (3, 81, 70),
    (3, 52, 80),
    (3, 51, 120),
    (3, 49, 60),
    (3, 54, 90),
    (3, 80, 25),
    (3, 20, 7),
    (3, 22, 600),
    (3, 21, 600),
    (3, 82, 3),

    (4, 79, 120),
    (4, 64, 180),
    (4, 85, 25),
    (4, 71, 60),
    (4, 68, 80),
    (4, 61, 60),
    (4, 80, 40),
    (4, 20, 12),
    (4, 82, 15),
    (4, 52, 10),

    (5, 78, 80),
    (5, 72, 60),
    (5, 52, 40),
    (5, 74, 70),
    (5, 75, 90),
    (5, 50, 60),
    (5, 71, 80),
    (5, 83, 60),
    (5, 79, 220),
    (5, 20, 25),
    (5, 80, 60),
]


    for requirement in ship_requirements:
        cursor.execute(
            'INSERT OR IGNORE INTO spaceship_requirements (ship_id, item_id, count) VALUES (?, ?, ?)',
            requirement,
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
    conn.commit()
    conn.close()

    init_planets()  # Инициализируем планеты
    init_caves()  # Инициализируем пещеры
    init_items()  # Инициализируем предметы
    init_requirements()  # Инициализируем требования для пещер
    init_spaceship()  # Инициализируем данные для космического корабля
    cave_requirements()  # Инициализируем требования для пещер
    ship_requirements()  # Инициализируем требования для кораблей
    
    
