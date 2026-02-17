import sqlite3
import random
from queries import SQL

class GameRepository:
    def __init__(self, db_name):
        self.db_name = db_name

    def _get_conn(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    # --- Вспомогательные методы ---
    def _execute(self, query, params=(), commit=True):
        with self._get_conn() as conn:
            cur = conn.execute(query, params)
            if commit: conn.commit()
            return cur

    def _fetch_one(self, query, params=()):
        with self._get_conn() as conn:
            return conn.execute(query, params).fetchone()

    def _fetch_all(self, query, params=()):
        with self._get_conn() as conn:
            return conn.execute(query, params).fetchall()

    # =====================================================
    # 1. ПОЛЬЗОВАТЕЛЬ
    # =====================================================
    
    def auth_user_db(self, user_id):
        """Создает юзера (если нет) и возвращает баланс."""
        self._execute(SQL.CREATE_USER, (user_id,))
        # Разблокировка первой пещеры (id=0) для новичка - логику можно добавить тут
        # Но лучше проверить: если это была вставка (rowcount > 0), то открыть пещеру.
        
        res = self._fetch_one(SQL.GET_BALANCE, (user_id,))
        return {"user_id": user_id, "balance": res['balance'] if res else 0}

    def get_user_coordinates(self, user_id):
        """Возвращает координаты и имя планеты (если есть)."""
        # Убедимся, что юзер существует
        self._execute(SQL.CREATE_USER, (user_id,)) 
        
        user = self._fetch_one(SQL.GET_USER_DATA, (user_id,))
        if not user:
            return {"coordinate_x": 0, "coordinate_y": 0, "planet_name": None}

        planet_name = None
        if user['currently_on_planet_id'] != 0:
            p_res = self._fetch_one(SQL.GET_PLANET_NAME, (user['currently_on_planet_id'],))
            if p_res: planet_name = p_res['name']

        return {
            "coordinate_x": user['coordinate_x'],
            "coordinate_y": user['coordinate_y'],
            "planet_name": planet_name
        }
    def get_user_inventory(self, user_id):
        res = SQL.GET_USER_INVENTORY
        items = self._fetch_all(res, (user_id,))
        return {"inventory": [{"item_id": i['item_id'], "name": i['item_name'], "count": i['count']} for i in items]}

    # =====================================================
    # 2. ПРЕДЛОЖЕНИЯ
    # =====================================================

    def get_active_offer(self, user_id):
        res = self._fetch_one(SQL.GET_ACTIVE_OFFER, (user_id,))
        if res:
            return {"has_offer": True, "item_id": res['item_id'], "name": res['item_name'], "count": res['count']}
        return {"has_offer": False}

    def decline_offer(self, user_id):
        self._execute(SQL.DELETE_OFFER, (user_id,))
        return {"result": "success", "message": "Предложение отклонено"}

    def accept_offer(self, user_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # 1. Получаем предложение
            offer = cursor.execute(SQL.GET_ACTIVE_OFFER, (user_id,)).fetchone()
            if not offer:
                return {"status": "error", "message": "Нет активного предложения"}
            
            item_id = offer['item_id']
            count = offer['count']
            name = offer['item_name']

            # 2. Добавляем в инвентарь (используем UPSERT)
            cursor.execute(SQL.UPSERT_INVENTORY, (user_id, item_id, count, count))
            
            # 3. Удаляем предложение
            cursor.execute(SQL.DELETE_OFFER, (user_id,))
            
            conn.commit()
            return {"result": "success", "message": f"Принято: {count}x {name}"}

    # =====================================================
    # 3. ПЛАНЕТЫ И ПОЛЕТЫ
    # =====================================================

    def get_planets(self, user_id):
        planets = self._fetch_all(SQL.GET_ALL_PLANETS)
        user = self._fetch_one(SQL.GET_USER_DATA, (user_id,))
        
        return {
            "planets": [dict(p) for p in planets],
            "user_coordinates": {"x": user['coordinate_x'], "y": user['coordinate_y']} if user else {"x":0, "y":0}
        }

    def set_target_planet(self, user_id, target_planet_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Проверки
            user = cursor.execute(SQL.GET_USER_DATA, (user_id,)).fetchone()
            
            if user['currently_on_planet_id'] == target_planet_id:
                return {"result": "success", "message": "Вы уже на этой планете!"}
            
            if user['space_ship_id'] == 0:
                return {"result": "error", "message": "Вы не выбрали корабль!"}

            planet = cursor.execute(SQL.GET_PLANET_NAME, (target_planet_id,)).fetchone()
            if not planet:
                return {"status": "error", "message": "Планета не найдена"}

            # Установка цели
            cursor.execute(SQL.UPDATE_TARGET_PLANET, (target_planet_id, user_id))
            conn.commit()
            
            return {"result": "success", "message": f"Курс проложен на {planet['name']}"}

    # =====================================================
    # 4. ПЕЩЕРЫ (Вход и Выбор)
    # =====================================================

    def get_caves(self, user_id):
        planet_id = self._fetch_one(SQL.GET_USER_DATA, (user_id,))['currently_on_planet_id']

        rows = self._fetch_all(SQL.GET_CAVES_WITH_STATUS, (user_id, planet_id))
        return {"caves": [{"id": r['id'], "name": r['name'], "is_unlocked": bool(r['is_unlocked'])} for r in rows]}

    def enter_cave(self, user_id, cave_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # 1. Проверяем, разблокирована ли
            if not cursor.execute(SQL.CHECK_CAVE_UNLOCKED, (user_id, cave_id)).fetchone():
                return {"status": "error", "message": "Пещера закрыта! Сначала разблокируйте её."}
            
            # 2. Обновляем статус юзера
            cursor.execute(SQL.SET_CURRENT_CAVE, (cave_id, user_id))
            name = cursor.execute(SQL.GET_CAVE_NAME, (cave_id,)).fetchone()['name']
            
            conn.commit()
            return {"status": "ok", "message": f"Вы вошли в {name}", "cave_name": name}

    # =====================================================
    # 5. МАЙНИНГ
    # =====================================================

    def mine(self, user_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # 1. Где юзер?
            user_loc = cursor.execute(SQL.GET_USER_CURRENT_CAVE, (user_id,)).fetchone()
            if not user_loc or user_loc['currently_on_cave_id'] == 0:
                return {"status": "error", "message": "Вы не в пещере!"}
            
            cave_id = user_loc['currently_on_cave_id']
            cave_name = cursor.execute(SQL.GET_CAVE_NAME, (cave_id,)).fetchone()['name']

            # 2. Что тут падает?
            resources = cursor.execute(SQL.GET_CAVE_RESOURCES, (cave_id,)).fetchall()
            if not resources:
                return {"status": "error", "message": "Тут пусто..."}

            # 3. Логика рандома (30 попыток)
            mined_total = {} # Словарь: {item_id: count}
            mined_names = {} # Словарь: {item_id: name}

            for _ in range(30):
                for res in resources: # res = (id, chance, name)
                    # res['chance'] это float 0.0 - 1.0
                    if random.random() < res['chance']:
                        item_id = res['id']
                        mined_total[item_id] = mined_total.get(item_id, 0) + 1
                        mined_names[item_id] = res['name']

            # 4. Запись в БД (Одной пачкой)
            for item_id, count in mined_total.items():
                cursor.execute(SQL.UPSERT_INVENTORY, (user_id, item_id, count, count))

            conn.commit()

            # 5. Красивый вывод
            result_list = [{"item_name": name, "count": count} for item_id, (name, count) in zip(mined_names.keys(), mined_total.values())]
            
            return {
                "status": "ok", 
                "mined_items": result_list, 
                "cave_name": cave_name
            }
        
    # =====================================================
    # 6. КРАФТИНГ
    # =====================================================

    def get_craft_list(self, user_id):
        """Возвращает список предметов. Поле can_create = True, если ресурсов хватает."""
        rows = self._fetch_all(SQL.GET_CRAFT_LIST, (user_id,))
        return {
            "items": [
                {"id": r['id'], "name": r['name'], "can_create": bool(r['can_create'])} 
                for r in rows
            ]
        }

    def get_craft_info(self, user_id, item_id):
        """Возвращает список требований: сколько есть и сколько нужно."""
        rows = self._fetch_all(SQL.GET_CRAFT_REQUIREMENTS, (user_id, item_id))
        
        requirements = []
        for r in rows:
            requirements.append({
                "item_id": r['item_id'],
                "item_name": r['item_name'],
                "count": r['required'],
                "have_count": r['have'],
                "enough": r['have'] >= r['required']
            })
            
        return {"requirements": requirements}

    def craft_item(self, user_id, item_id):
        """
        Главная функция крафта.
        1. Проверяет ресурсы.
        2. Списывает ресурсы.
        3. Добавляет созданный предмет.
        Все в одной транзакции.
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # 1. Снова проверяем требования (безопасность)
            # Используем тот же запрос, что и в get_craft_info
            cursor.execute(SQL.GET_CRAFT_REQUIREMENTS, (user_id, item_id))
            requirements = cursor.fetchall()

            if not requirements:
                return {"status": "error", "message": "Рецепт не найден!"}

            # Проверка: хватает ли всего?
            for req in requirements:
                if req['have'] < req['required']:
                    return {"status": "error", "message": f"Не хватает: {req['item_name']}"}

            try:
                # 2. Списываем ингредиенты
                for req in requirements:
                    cursor.execute(SQL.REMOVE_ITEM, (req['required'], user_id, req['item_id']))

                # 3. Выдаем новый предмет (+1 шт)
                cursor.execute(SQL.UPSERT_INVENTORY, (user_id, item_id, 1, 1))

                # Получим имя для красивого сообщения
                created_name = cursor.execute("SELECT name FROM items WHERE id = ?", (item_id,)).fetchone()['name']
                
                conn.commit()
                return {"status": "ok", "message": f"Создан предмет: {created_name}"}

            except Exception as e:
                conn.rollback()
                print(f"Craft Error: {e}")
                return {"status": "error", "message": "Ошибка при создании предмета"}


    # =====================================================
    # 7. КОРАБЛИ (УПРАВЛЕНИЕ)
    # =====================================================

    def get_ships(self, user_id):
        """Возвращает список всех кораблей со статусами."""
        # Передаем user_id дважды, так как в SQL он используется в двух местах
        rows = self._fetch_all(SQL.GET_SHIPS_LIST, (user_id, user_id))
        return {
            "ships": [
                {
                    "id": r['ship_id'], 
                    "name": r['name'], 
                    "is_unlocked": bool(r['is_unlocked']),
                    "can_create": bool(r['can_create']) # Для кораблей это значит "можно купить"
                } 
                for r in rows
            ]
        }

    def get_ship_info(self, user_id, ship_id):
        """Возвращает цену корабля (требования)."""
        rows = self._fetch_all(SQL.GET_SHIP_REQUIREMENTS, (user_id, ship_id))
        
        requirements = []
        for r in rows:
            requirements.append({
                "item_name": r['item_name'],
                "count": r['required'],
                "have_count": r['have'],
                "enough": r['have'] >= r['required']
            })
            
        return {"requirements": requirements}

    def unlock_ship(self, user_id, ship_id):
        """Покупка корабля за ресурсы."""
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # 1. Проверка: уже куплен?
            if cursor.execute(SQL.CHECK_SHIP_UNLOCKED, (user_id, ship_id)).fetchone():
                return {"status": "ok", "message": "Корабль уже куплен!"}

            # 2. Получаем требования
            cursor.execute(SQL.GET_SHIP_REQUIREMENTS, (user_id, ship_id))
            requirements = cursor.fetchall()

            # 3. Проверяем ресурсы
            for req in requirements:
                if req['have'] < req['required']:
                    return {"status": "error", "message": f"Не хватает: {req['item_name']}"}

            try:
                # 4. Списываем ресурсы
                for req in requirements:
                    # Используем универсальный запрос списания из SQL (тот же, что для крафта)
                    cursor.execute(SQL.REMOVE_ITEM, (req['required'], user_id, req['item_id']))

                # 5. Разблокируем корабль
                cursor.execute(SQL.UNLOCK_SHIP, (user_id, ship_id))
                
                conn.commit()
                return {"status": "ok", "message": "Корабль успешно куплен!"}

            except Exception as e:
                conn.rollback()
                print(f"Unlock Ship Error: {e}")
                return {"status": "error", "message": "Ошибка базы данных"}

    def select_ship(self, user_id, ship_id):
        """
        Выбор (экипировка) корабля.
        Сначала проверяет, куплен ли он.
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # 1. Проверка владения
            if not cursor.execute(SQL.CHECK_SHIP_UNLOCKED, (user_id, ship_id)).fetchone():
                 # Если пытаются выбрать не купленный корабль, можно вернуть детали цены
                 # Но для простоты вернем ошибку
                 return {"status": "error", "message": "Этот корабль еще не куплен!"}

            # 2. Устанавливаем корабль в профиль пользователя
            cursor.execute(SQL.SELECT_SHIP, (ship_id, user_id))
            
            # 3. Получаем имя для сообщения
            name = cursor.execute(SQL.GET_SHIP_NAME, (ship_id,)).fetchone()['name']
            
            conn.commit()
            return {"status": "ok", "message": f"Вы пересели на {name}"}