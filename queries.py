class SQL:
    # --- Пользователь и Инициализация ---
    CREATE_USER = "INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)"
    GET_BALANCE = "SELECT balance FROM users WHERE user_id = ?"
    GET_USER_DATA = "SELECT coordinate_x, coordinate_y, currently_on_planet_id, space_ship_id, currently_on_cave_id FROM users WHERE user_id = ?"
    
    # --- Предложения (Offers) ---
    GET_ACTIVE_OFFER = "SELECT item_id, item_name, count FROM active_offers WHERE user_id = ?"
    DELETE_OFFER = "DELETE FROM active_offers WHERE user_id = ?"
    
    # --- Инвентарь (Базовые) ---
    # Обновление инвентаря (Добавить или создать)
    UPSERT_INVENTORY = """
        INSERT INTO inventory (user_id, item_id, count) VALUES (?, ?, ?)
        ON CONFLICT(user_id, item_id) DO UPDATE SET count = count + ?
    """
    CHECK_ITEM_COUNT = "SELECT count FROM inventory WHERE user_id = ? AND item_id = ?"
    GET_ITEM_NAME = "SELECT name FROM items WHERE id = ?"

    GET_USER_INVENTORY = """
        SELECT i.id as item_id, i.name as item_name, inv.count as count
        FROM inventory inv
        JOIN items i ON i.id = inv.item_id
        WHERE inv.user_id = ?
        ORDER BY i.name
    """

    # --- Планеты и Перемещение ---
    GET_ALL_PLANETS = "SELECT id, name, coordinate_x, coordinate_y FROM planets WHERE id != 0"
    GET_PLANET_NAME = "SELECT name FROM planets WHERE id = ?"
    
    UPDATE_TARGET_PLANET = "UPDATE users SET target_planet_id = ?, currently_on_planet_id = 0 WHERE user_id = ?"
    RESET_PLANET_STATUS = "UPDATE users SET currently_on_planet_id = 0 WHERE user_id = ?" # Если улетаем
    
    # --- Пещеры (Caves) ---
    # Получить пещеры на планете + статус разблокировки
    GET_CAVES_WITH_STATUS = """
        SELECT c.id, c.name, 
               CASE WHEN uc.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_unlocked
        FROM caves c
        LEFT JOIN unlock_caves uc ON c.id = uc.cave_id AND uc.user_id = ?
        WHERE c.planet_id = ?
    """
    CHECK_CAVE_UNLOCKED = "SELECT 1 FROM unlock_caves WHERE user_id = ? AND cave_id = ?"
    GET_CAVE_NAME = "SELECT name FROM caves WHERE id = ?"
    SET_CURRENT_CAVE = "UPDATE users SET currently_on_cave_id = ? WHERE user_id = ?"

    # --- Майнинг ---
    GET_CAVE_RESOURCES = "SELECT id, chance, name FROM items WHERE cave_id = ?"
    GET_USER_CURRENT_CAVE = "SELECT currently_on_cave_id FROM users WHERE user_id = ?"


    # ---крафтинг---
    GET_CRAFT_LIST = """
        SELECT 
            ci.id, 
            ci.name,
            CASE 
                -- Если количество недостающих ингредиентов == 0, то можно крафтить (1)
                WHEN SUM(CASE WHEN COALESCE(inv.count, 0) < req.count THEN 1 ELSE 0 END) = 0 
                THEN 1 ELSE 0 
            END as can_create
        FROM items ci
        JOIN item_requirements req ON req.item_id = ci.id
        LEFT JOIN inventory inv ON inv.user_id = ? AND inv.item_id = req.required_item_id
        GROUP BY ci.id, ci.name
        ORDER BY ci.id
    """

    # 2. Получить конкретные требования для одного предмета (для окна информации)
    GET_CRAFT_REQUIREMENTS = """
        SELECT 
            req.required_item_id as item_id,
            i.name as item_name,
            req.count as required,
            COALESCE(inv.count, 0) as have
        FROM item_requirements req
        JOIN items i ON i.id = req.required_item_id
        LEFT JOIN inventory inv ON inv.user_id = ? AND inv.item_id = req.required_item_id
        WHERE req.item_id = ?
    """

    # 3. Добавить предмет (тот же запрос, что и при майнинге)
    UPSERT_INVENTORY = """
        INSERT INTO inventory (user_id, item_id, count) VALUES (?, ?, ?)
        ON CONFLICT(user_id, item_id) DO UPDATE SET count = count + ?
    """

    # 4. Списать ресурс
    REMOVE_ITEM = "UPDATE inventory SET count = count - ? WHERE user_id = ? AND item_id = ?"


    GET_SHIPS_LIST = """
        SELECT 
            s.ship_id, 
            s.name,
            CASE WHEN us.user_id IS NOT NULL THEN 1 ELSE 0 END as is_unlocked,
            CASE 
                -- Если уже куплен ИЛИ хватает ресурсов -> 1, иначе 0
                WHEN us.user_id IS NOT NULL THEN 1
                WHEN SUM(CASE WHEN COALESCE(inv.count, 0) < req.count THEN 1 ELSE 0 END) = 0 THEN 1 
                ELSE 0 
            END as can_create
        FROM spaceship s
        LEFT JOIN unlock_spaceship us ON s.ship_id = us.ship_id AND us.user_id = ?
        LEFT JOIN spaceship_requirements req ON req.ship_id = s.ship_id
        LEFT JOIN inventory inv ON inv.user_id = ? AND inv.item_id = req.item_id
        GROUP BY s.ship_id, s.name
        ORDER BY s.ship_id
    """

    # 2. Требования для покупки конкретного корабля
    GET_SHIP_REQUIREMENTS = """
        SELECT 
            req.item_id, 
            i.name as item_name, 
            req.count as required, 
            COALESCE(inv.count, 0) as have
        FROM spaceship_requirements req
        JOIN items i ON i.id = req.item_id
        LEFT JOIN inventory inv ON inv.user_id = ? AND inv.item_id = req.item_id
        WHERE req.ship_id = ?
    """

    # 3. Проверка: куплен ли корабль?
    CHECK_SHIP_UNLOCKED = "SELECT 1 FROM unlock_spaceship WHERE user_id = ? AND ship_id = ?"

    # 4. Действие: Разблокировать (добавить запись в таблицу)
    UNLOCK_SHIP = "INSERT INTO unlock_spaceship (user_id, ship_id) VALUES (?, ?)"

    # 5. Действие: Выбрать (Экипировать) - обновление таблицы users
    SELECT_SHIP = "UPDATE users SET space_ship_id = ? WHERE user_id = ?"

    # 6. Получить имя корабля (для сообщений)
    GET_SHIP_NAME = "SELECT name FROM spaceship WHERE ship_id = ?"