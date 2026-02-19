import { tg, getUserId, postJson } from "./api.js";

class CaveManager {
    constructor() {
        // Кеш элементов DOM
        this.dom = {
            interface: document.getElementById("mine_interface"),
            menuBtn: document.getElementById("menuCaveBtn"),
            menuContent: document.getElementById("menuCaveContent"),
            list: document.getElementById("caveList"),
            mineBtn: document.getElementById("caveMiningBtn"),
            result: document.getElementById("miningResult")
        };
    }

    init() {
        if (!this.dom.menuBtn || !this.dom.list) {
            console.error("CaveManager: Элементы не найдены");
            return;
        }

        // Скрываем лишнее при старте
        this.dom.result.style.display = "none";
        this.dom.mineBtn.style.display = "none";

        // Листенеры
        this.dom.mineBtn.onclick = () => this.mine();
        
        this.dom.menuBtn.onclick = (e) => {
            e.stopPropagation();
            this.toggleMenu();
        };

        window.addEventListener("click", (e) => this.handleGlobalClick(e));
    }

    // --- Меню ---
    toggleMenu() {
        if (this.dom.menuContent.classList.contains("show")) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }

    openMenu() {
        this.dom.menuContent.classList.add("show");
        this.dom.menuBtn.innerText = "⛏️ Выбор Шахт ▲";
        this.loadCaveList();
    }

    closeMenu() {
        this.dom.menuContent.classList.remove("show");
        this.dom.menuBtn.innerText = "⛏️ Выбор Шахт ▼";
    }

    toggleInterface(show) {
        if (!this.dom.interface) return;
        if (show) {
            this.dom.interface.classList.remove("hidden");
        } else {
            this.dom.interface.classList.add("hidden");
            this.closeMenu();
            this.dom.result.style.display = "none";
        }
    }

    // --- Загрузка списка шахт ---
    async loadCaveList() {
        this.dom.list.innerHTML = '<div style="padding:10px; color:#aaa;">⏳ Загрузка списка...</div>';
        const userId = getUserId();

        try {
            const data = await postJson("/api/get_cave", { user_id: userId });
            this.dom.list.innerHTML = "";

            if (data.caves && data.caves.length > 0) {
                data.caves.forEach(cave => this.renderCaveItem(cave, userId));
            } else {
                this.dom.list.innerHTML = '<div style="padding:10px;">Нет доступных шахт</div>';
            }
        } catch (e) {
            console.error(e);
            this.dom.list.innerHTML = '<div style="color:red;">Ошибка сети</div>';
        }
    }

    // --- Рендер одной строки (Аккордеон) ---
    renderCaveItem(cave, userId) {
        const wrapper = document.createElement("div");
        wrapper.className = "cave-accordion-item";

        // 1. Заголовок
        const headerBtn = document.createElement("button");
        headerBtn.className = "cave-header-btn";
        const icon = cave.is_unlocked ? "🟢" : "🔒"; // Зеленый круг или замок
        headerBtn.innerHTML = `<span>${cave.name}</span> <span>${icon}</span>`;

        // 2. Блок деталей (скрытый)
        const detailsDiv = document.createElement("div");
        detailsDiv.className = "cave-details";

        if (cave.is_unlocked) {
            // -- ЕСЛИ ОТКРЫТА --
            detailsDiv.innerHTML = `<p style="margin:10px 0; font-size:14px; color:#aaa;">Шахта готова к работе.</p>`;
            
            const selectBtn = document.createElement("button");
            selectBtn.className = "select-mine-btn"; // Используем твой CSS класс кнопки
            selectBtn.innerHTML = "✅ ВЫБРАТЬ";
            selectBtn.onclick = (e) => {
                e.stopPropagation();
                this.selectCave(cave.id, cave.name);
            };
            detailsDiv.appendChild(selectBtn);

        } else {
            // -- ЕСЛИ ЗАКРЫТА (Показываем требования как крафт) --
            detailsDiv.innerHTML = `<div style="margin-bottom:5px;"><strong>Требуется для открытия:</strong></div>`;
            
            // Контейнер для списка ресурсов
            const reqList = document.createElement("div");
            reqList.className = "requirements-list";
            reqList.innerHTML = "⏳ Проверка ресурсов..."; 
            detailsDiv.appendChild(reqList);

            // Кнопка разблокировки (изначально скрыта или неактивна)
            const unlockBtn = document.createElement("button");
            unlockBtn.className = "select-mine-btn btn-disabled"; // Добавляем класс disabled
            unlockBtn.innerText = "🔒 РАЗБЛОКИРОВАТЬ";
            unlockBtn.disabled = true;

            unlockBtn.onclick = (e) => {
                e.stopPropagation();
                this.unlockCave(cave.id, userId);
            };
            detailsDiv.appendChild(unlockBtn);

            // ! ГЛАВНОЕ: При клике на заголовок загружаем инфу и сравниваем с инвентарем
            headerBtn.addEventListener('click', () => {
                if (!detailsDiv.classList.contains("open")) {
                    // Передаем кнопку, чтобы активировать её, если ресурсов хватает
                    this.loadRequirements(cave.id, userId, reqList, unlockBtn);
                }
            });
        }

        // Клик по аккордеону
        headerBtn.onclick = (e) => {
            e.stopPropagation();
            this.toggleAccordion(detailsDiv);
        };

        wrapper.appendChild(headerBtn);
        wrapper.appendChild(detailsDiv);
        this.dom.list.appendChild(wrapper);
    }

    // --- Логика сравнения ресурсов (Крафт-стайл) ---
    async loadRequirements(caveId, userId, listContainer, unlockBtn) {
        try {
            // Делаем два запроса параллельно: Требования шахты и Инвентарь игрока
            // Внимание: замените "/api/get_inventory" на ваш реальный эндпоинт получения инвентаря!
            const [caveInfo, userInventory] = await Promise.all([
                postJson("/api/get_cave_info", { user_id: userId, cave_id: caveId })
            ]);

            listContainer.innerHTML = "";
            let canUnlock = true; // Флаг: можно ли открыть


            if (caveInfo.requirements && caveInfo.requirements.length > 0) {
                caveInfo.requirements.forEach(req => {
                    // Получаем сколько есть у юзера
                    // req.item_id должно совпадать с тем, что в инвентаре
                    const userHas = req.have_count || 0;
                    const needed = req.count;
                    const isEnough = req.enough;

                    if (!isEnough) canUnlock = false;

                    // Создаем красивую строку
                    const row = document.createElement("div");
                    row.className = "resource-row";
                    
                    // Левая часть: Название
                    const nameSpan = document.createElement("span");
                    nameSpan.innerText = req.item_name;

                    // Правая часть: 5/10
                    const countSpan = document.createElement("span");
                    countSpan.className = isEnough ? "res-sufficient" : "res-insufficient";
                    countSpan.innerHTML = isEnough 
                        ? `✅ ${userHas} / ${needed}` 
                        : `❌ ${userHas} / ${needed}`;

                    row.appendChild(nameSpan);
                    row.appendChild(countSpan);
                    listContainer.appendChild(row);
                });
            } else {
                listContainer.innerHTML = "<div style='padding:10px'>Бесплатно</div>";
            }

            // Активируем кнопку, если всего хватает
            if (canUnlock) {
                unlockBtn.disabled = false;
                unlockBtn.classList.remove("btn-disabled");
                unlockBtn.innerText = "⛏️ РАЗБЛОКИРОВАТЬ";
                unlockBtn.style.background = "#4cd964"; // Зеленый фон
            } else {
                unlockBtn.innerText = "🔒 НЕДОСТАТОЧНО РЕСУРСОВ";
            }

        } catch (e) {
            console.error(e);
            listContainer.innerHTML = "<div style='color:red'>Ошибка загрузки данных</div>";
        }
    }

    // --- Действия (Остались прежними) ---

    async unlockCave(caveId, userId) {
        if(!confirm("Разблокировать шахту? Ресурсы будут списаны.")) return;

        try {
            const data = await postJson("/api/unlock_cave", { user_id: userId, cave_id: caveId });
            alert(data.message);
            if (data.status === "ok") {
                this.loadCaveList(); // Перезагружаем список
            }
        } catch (e) {
            alert("Ошибка сервера");
        }
    }

    async selectCave(caveId, caveName) {
        try {
            const userId = getUserId();
            const data = await postJson("/api/choice_cave", { user_id: userId, cave_id: caveId });
            
            if (data.status === "error") {
                alert(data.message); return;
            }

            alert(data.message);
            this.dom.mineBtn.style.display = "block";
            this.dom.mineBtn.innerText = `⛏️ Добывать в ${data.cave_name || caveName}`;
            this.dom.result.style.display = "none";
            this.closeMenu();

        } catch (e) {
            alert("Ошибка сети");
        }
    }

    async mine() {
        const userId = getUserId();
        this.dom.result.style.display = "block";
        this.dom.result.innerHTML = "⏳ Добыча...";

        try {
            const data = await postJson("/api/mine_cave", { user_id: userId });
            if (data.status === "ok") {
                this.dom.result.innerHTML = `<h3>Итог (${data.cave_name}):</h3>`;
                if (data.mined_items?.length) {
                    const ul = document.createElement("ul");
                    data.mined_items.forEach(item => {
                        const li = document.createElement("li");
                        li.innerHTML = `${item.item_name} : ${item.count}`;
                        ul.appendChild(li);
                    });
                    this.dom.result.appendChild(ul);
                } else {
                    this.dom.result.innerHTML += "<p>Пусто...</p>";
                }
            } else {
                this.dom.result.innerHTML = `<p style="color:red">${data.message}</p>`;
            }
        } catch (e) {
            this.dom.result.innerHTML = "Ошибка сети";
        }
    }

    // Хелперы
    toggleAccordion(target) {
        document.querySelectorAll('.cave-details').forEach(el => {
            if (el !== target) el.classList.remove('open');
        });
        target.classList.toggle("open");
    }

    handleGlobalClick(e) {
        if (!this.dom.interface || this.dom.interface.classList.contains("hidden")) return;
        const target = e.target;
        const inside = this.dom.mineBtn.contains(target) ||
                       this.dom.result.contains(target) ||
                       this.dom.menuContent.contains(target) ||
                       this.dom.menuBtn.contains(target);
        
        if (!inside) {
            this.dom.result.style.display = "none";
            this.closeMenu();
        }
    }
}

// Экземпляр и Экспорт
const caveManager = new CaveManager();

export function initCaveMenu() {
    caveManager.init();
}

export function toggleMineInterface(show) {
    caveManager.toggleInterface(show);
}