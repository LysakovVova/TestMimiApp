// js/menu.js
import { tg, getUserId, postJson } from "./api.js";
import { updateUserCoordinate } from "./app.js";

class DropdownManager {
    constructor(config) {
        this.config = config;
        this.button = document.getElementById(config.buttonId);
        this.container = document.getElementById(config.containerId);
        
        // Режимы работы:
        // 'craft'  = Рецепты (проверка ресурсов -> кнопка "Создать")
        // 'unlock' = Корабли (если закрыт -> "Разблокировать", если открыт -> "Выбрать")
        // 'simple' = Инвентарь/Планеты (просто список -> кнопка "Действие" -> Alert)
        this.mode = config.mode || 'craft';

        // Текстовые метки и настройки по умолчанию
        this.labels = {
            open: "▲", closed: "▼", loading: "⏳ Загрузка...",
            empty: "Пусто", error: "Ошибка загрузки", 
            actionBtn: "ДЕЙСТВИЕ", // Текст кнопки для simple режима
            ...config.labels 
        };

        // Запуск, только если элементы существуют на странице
        if (this.button && this.container) {
            this.init();
        } else {
            console.warn(`DropdownManager: Элементы не найдены (${config.buttonId})`);
        }
    }

    init() {
        this.button.onclick = (e) => {
            e.stopPropagation();
            const isOpen = this.container.style.display === "block";
            
            // Если нужно закрывать другие меню при открытии этого — добавьте логику здесь
            
            if (isOpen) {
                this.close();
            } else {
                this.open();
            }
        };
    }

    open() {
        this.container.style.display = "block";
        // Меняем стрелочку в тексте кнопки
        this.button.innerText = this.button.innerText.replace(this.labels.closed, this.labels.open);
        this.loadData();
    }

    close() {
        this.container.style.display = "none";
        // Меняем стрелочку обратно
        this.button.innerText = this.button.innerText.replace(this.labels.open, this.labels.closed);
    }

    async loadData() {
        this.container.innerHTML = `<div style="padding:10px; color:#aaa;">${this.labels.loading}</div>`;
        
        try {
            const userId = getUserId();
            // Запрос к API списка
            const data = await postJson(this.config.apiList, { user_id: userId });
            this.container.innerHTML = "";

            // Ищем массив данных в ответе (поддерживаем разные ключи: items, ships, planets, inventory)
            const list = data.items || data.ships || data.planets || data.inventory || [];

            if (!list || list.length === 0) {
                this.container.innerHTML = `<div style="padding:10px;">${this.labels.empty}</div>`;
                return;
            }

            // Рендерим каждый элемент
            for (const item of list) {
                this.renderItem(item, userId);
            }

        } catch (err) {
            console.error(err);
            this.container.innerHTML = `<div style="color:red; padding:10px;">${this.labels.error}</div>`;
        }
    }

    renderItem(item, userId) {
        const wrapper = document.createElement("div");
        wrapper.className = "cave-accordion-item";

        // --- 1. КНОПКА ЗАГОЛОВКА ---
        const headerBtn = document.createElement("button");
        headerBtn.className = "cave-header-btn";
        
        // СТИЛИ ДЛЯ ВЫРАВНИВАНИЯ
        // Делаем кнопку гибким контейнером: текст слева, иконка справа
        headerBtn.style.display = "flex";
        headerBtn.style.justifyContent = "space-between";
        headerBtn.style.alignItems = "center";
        headerBtn.style.width = "100%";
        headerBtn.style.textAlign = "left";
        headerBtn.style.padding = "10px"; // Немного отступов

        // ОПРЕДЕЛЕНИЕ ИКОНКИ СПРАВА
        let icon = "🔹";
        if (this.mode === 'unlock') icon = item.is_unlocked ? "🚀" : "🔒";
        else if (this.mode === 'craft') icon = item.can_create ? "✅" : "🧩";
        else if (this.mode === 'simple') icon = this.config.icon || "📦";

        // ОТОБРАЖЕНИЕ КОЛИЧЕСТВА (если оно есть в данных)
        // Обычно сервер присылает item.count или item.amount
        let countText = "";
        if (item.count !== undefined && item.count !== null) {
            countText = ` <span style="color: #e94560; font-weight: margin-left: 5px;">: ${item.count}</span>`;
        }

        // ФОРМИРУЕМ HTML КНОПКИ
        // Левая часть (Иконка + Имя + Кол-во)
        const leftSide = `
            <div style="display:flex; align-items:center;">
                <span style="margin-right: 8px;">🔹</span> 
                <span>${item.name}${countText}</span>
            </div>
        `;
        
        headerBtn.innerHTML = `${leftSide} <span>${icon}</span>`;

        // --- 2. ДЕТАЛИ (ВЫПАДАЮЩИЙ БЛОК) ---
        const detailsDiv = document.createElement("div");
        detailsDiv.className = "cave-details";

        // === ЛОГИКА ОТОБРАЖЕНИЯ ===
        
        if (this.mode === 'simple') {
            // Описание
            if (item.description) {
                detailsDiv.innerHTML += `<p style="color:#ccc; font-size:0.9em; margin: 5px 0 10px 0;">${item.description}</p>`;
            }
            
            // Кнопка действия (Использовать/Сканировать)
            if (this.config.apiAction) {
                const actionBtn = document.createElement("button");
                actionBtn.className = "select-mine-btn";
                actionBtn.innerText = this.config.labels.actionBtn || "ДЕЙСТВИЕ";
                actionBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.executeAction(this.config.apiAction, { user_id: userId, planet_id: item.id, item_id: item.id });
                };
                detailsDiv.appendChild(actionBtn);
            }
            
            headerBtn.onclick = (e) => {
                e.stopPropagation();
                this.toggleAccordion(detailsDiv);
            };

        } else if (this.mode === 'unlock' && item.is_unlocked) {
            // Если корабль куплен
            detailsDiv.innerHTML = `<p style="margin-bottom:10px; text-align:left;">Готов к полету.</p>`;
            
            const selectBtn = document.createElement("button");
            selectBtn.className = "select-mine-btn";
            selectBtn.innerText = this.config.labels.selectBtn || "✅ ВЫБРАТЬ";
            selectBtn.onclick = (e) => {
                e.stopPropagation();
                this.executeAction(this.config.apiSelect, { user_id: userId, ship_id: item.id });
            };
            detailsDiv.appendChild(selectBtn);

            headerBtn.onclick = (e) => {
                e.stopPropagation();
                this.toggleAccordion(detailsDiv);
            };

        } else {
            // Крафт или покупка корабля
            detailsDiv.innerHTML = `<div style="text-align:left;"><strong>Требования:</strong></div>`;
            
            const reqList = document.createElement("ul");
            reqList.className = "unlock-cost-list";
            reqList.style.textAlign = "left"; // Выравниваем список требований влево
            reqList.innerHTML = "<li>⏳ Загрузка...</li>";
            detailsDiv.appendChild(reqList);

            const createBtn = document.createElement("button");
            createBtn.className = "unlock-ship-btn";
            createBtn.innerText = this.mode === 'unlock' ? "🛠 РАЗБЛОКИРОВАТЬ" : "🛠 СОЗДАТЬ";
            
            createBtn.onclick = (e) => {
                e.stopPropagation();
                if (!confirm(`Вы уверены: ${item.name}?`)) return;
                this.executeAction(this.config.apiCreate, { user_id: userId, item_id: item.id, ship_id: item.id }, true);
            };
            detailsDiv.appendChild(createBtn);

            headerBtn.onclick = (e) => {
                e.stopPropagation();
                this.toggleAccordion(detailsDiv);
                if (detailsDiv.classList.contains("open")) {
                    this.loadRequirements(item, reqList, userId);
                }
            };
        }

        wrapper.appendChild(headerBtn);
        wrapper.appendChild(detailsDiv);
        this.container.appendChild(wrapper);
    }

    // Хелпер для переключения аккордеона (чтобы открывался только один)
    toggleAccordion(targetDiv) {
        // Закрываем все остальные в этом контейнере
        this.container.querySelectorAll(".cave-details").forEach(el => {
            if (el !== targetDiv) el.classList.remove("open");
        });
        targetDiv.classList.toggle("open");
    }

    // Хелпер для загрузки требований (цены)
    async loadRequirements(item, listElement, userId) {
        try {
            // Запрашиваем инфо о предмете/корабле
            const data = await postJson(this.config.apiInfo, { user_id: userId, item_id: item.id, ship_id: item.id });
            
            listElement.innerHTML = "";
            if (data.requirements && data.requirements.length > 0) {
                data.requirements.forEach(req => {
                    // Логика цвета: если enough = false, то красный, иначе зеленый
                    // (если сервер не шлет enough для кораблей, можно считать всегда белым или проверять client-side)
                    const color = (req.enough === false) ? "#ff6b6b" : "#9eff9e";
                    
                    const li = document.createElement("li");
                    li.style.color = color;
                    li.innerText = `- ${req.item_name}: ${req.have_count !== undefined ? req.have_count + '/' : ''}${req.count}`;
                    listElement.appendChild(li);
                });
            } else {
                listElement.innerHTML = "<li>Бесплатно / Нет требований</li>";
            }
        } catch (err) {
            console.error(err);
            listElement.innerHTML = "<li>Ошибка получения данных</li>";
        }
    }

    // Хелпер для выполнения действия (клик по кнопке)
    async executeAction(endpoint, payload, reloadOnSuccess = false) {
        try {
            const res = await postJson(endpoint, payload);
            
            // Выводим сообщение (как просили для инвентаря и пр.)
            alert(res.message || "Готово");

            // Если действие успешное и нужно обновить список (например, после крафта)
            if ((res.status === "ok" || res.success) && reloadOnSuccess) {
                this.loadData();
            }
        } catch (err) {
            console.error(err);
            alert(`Ошибка: ${err.message || "Сбой соединения"}`);
        }
    }
}


export function initMenu() {
    tg.expand();

    // 1. Логика Главного Меню (Кнопка меню)
    const menuBtn = document.getElementById("menuBtn");
    const menuContent = document.getElementById("menuContent");

    menuBtn.onclick = (e) => {
        e.stopPropagation();
        menuContent.classList.toggle("show");
        const isOpen = menuContent.classList.contains("show");
        menuBtn.innerText = isOpen ? "❌ ЗАКРЫТЬ" : "☰ МЕНЮ ИГРЫ";
        menuBtn.style.color = "white";
    };

    // Закрытие по клику вне меню
    window.onclick = (event) => {
        if (!event.target.matches("#menuBtn") && !event.target.matches(".main-menu-btn")) {
            if (menuContent.classList.contains("show")) {
                menuContent.classList.remove("show");
                menuBtn.innerText = "☰ МЕНЮ ИГРЫ";
            }
        }
    };

    // 2. Инициализация выпадающих списков

    // --- ИНВЕНТАРЬ (Simple Mode) ---
    new DropdownManager({
        buttonId: "inventoryBtn",
        containerId: "inventoryList",
        mode: "simple",
        icon: "🎒",
        apiList: "/api/get_inventory",
        apiAction: "/api/use_item", // При клике "Использовать"
        labels: {
            loading: "🎒 Открываем рюкзак...",
            empty: "Рюкзак пуст",
            actionBtn: "💡 ИСПОЛЬЗОВАТЬ"
        }
    });

    // --- СКАНИРОВАНИЕ КОСМОСА (Simple Mode) ---
    new DropdownManager({
        buttonId: "getPlanetBtn",
        containerId: "getPlanetList",
        mode: "simple",
        icon: "🪐",
        apiList: "/api/get_planets",
        apiAction: "/api/set_target_planet", // При клике "Сканировать"
        labels: {
            loading: "🔭 Сканирование сектора...",
            empty: "Планет не обнаружено",
            actionBtn: "🚀 Полететь"
        }
    });

    // --- СОЗДАНИЕ ПРЕДМЕТОВ (Craft Mode) ---
    new DropdownManager({
        buttonId: "requirementsBtn",
        containerId: "requirementsList",
        mode: "craft",
        apiList: "/api/get_create_items",
        apiInfo: "/api/get_create_item_info",
        apiCreate: "/api/create_item",
        labels: {
            loading: "⏳ Поиск чертежей...",
            empty: "Нет доступных рецептов"
        }
    });

    // --- ВЫБОР КОРАБЛЯ (Unlock Mode) ---
    new DropdownManager({
        buttonId: "choiceShipBtn",
        containerId: "choiceShipList", // Важно: ID контейнера списка
        mode: "unlock",
        apiList: "/api/get_ship",
        apiInfo: "/api/get_ship_info",
        apiCreate: "/api/unlock_ship", // Кнопка "Разблокировать"
        apiSelect: "/api/choice_ship", // Кнопка "Выбрать"
        labels: {
            loading: "🚀 Проверка ангара...",
            selectBtn: "✅ СЕСТЬ ЗА ШТУРВАЛ"
        }
    });
}