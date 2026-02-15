// js/menuCave.js
import { tg, getUserId, postJson } from "./api.js";

export function initCaveMenu() {
    // tg.expand(); // Можно оставить, если нужно

    const menuBtn = document.getElementById("menuCaveBtn");
    const caveList = document.getElementById("caveList");
    const menuContent = document.getElementById("menuCaveContent"); // Сам выпадающий блок

    if (!menuBtn || !caveList || !menuContent) {
        console.error("Элементы меню шахт не найдены!");
        return;
    }

    // Обработчик клика по кнопке
    menuBtn.addEventListener("click", async (e) => {
        e.stopPropagation(); // Остановить всплытие, чтобы window не поймал клик сразу

        // Проверяем, открыто ли меню через класс (это надежнее)
        const isOpen = menuContent.classList.contains("show");

        if (isOpen) {
            // ЗАКРЫВАЕМ
            closeCaveMenu();
        } else {
            // ОТКРЫВАЕМ
            menuContent.classList.add("show"); // Сразу показываем блок
            menuBtn.innerText = "⛏️ Выбор Шахт ▲";
            menuBtn.style.color = "#e94560";
            
            // Если список пуст, загружаем данные
            if (caveList.innerHTML.trim() === "") {
                await loadCaveData();
            }
        }
    });

    // Функция загрузки данных
    async function loadCaveData() {
        caveList.innerHTML = '<div style="padding:10px; color:#aaa;">⏳ Загрузка...</div>';
        
        try {
            const userId = getUserId();
            const data = await postJson("/api/get_cave", { user_id: userId });

            caveList.innerHTML = ""; // Очищаем "Загрузку"

            if (data.caves && data.caves.length > 0) {
                data.caves.forEach(cave => {
                    const btn = document.createElement("button");
                    btn.className = "inventory-item-btn"; // Используем стиль из CSS

                    if (cave.is_unlocked) {
                        btn.innerText = `🔓 ${cave.name}`;
                    } else {
                        btn.innerText = `🔒 ${cave.name}`;
                        // btn.disabled = true; // Заблокированная шахта не кликабельна
                    }
                    
                    btn.onclick = (ev) => {
                        ev.stopPropagation(); 
                        targetMine(cave.id, btn);
                        // Тут логика выбора шахты
                    };
                    caveList.appendChild(btn);
                });
            } else {
                caveList.innerHTML = '<div style="padding:10px; color:#555;">Пусто...</div>';
            }
        } catch (e) {
            console.error(e);
            caveList.innerHTML = '<div style="padding:10px; color:red;">Ошибка связи!</div>';
        }
    }

    // Функция закрытия (вынесли отдельно, чтобы удобно вызывать)
    function closeCaveMenu() {
        menuContent.classList.remove("show");
        menuBtn.innerText = "⛏️ Выбор Шахт ▼";
        menuBtn.style.color = "white";
    }

    async function targetMine(caveId, buttonElement) {
    try {
        const userId = getUserId(); // Получаем ID игрока
        
        // Отправляем запрос на сервер
        const data = await postJson("/api/choice_cave", { 
            user_id: userId, 
            cave_id: caveId 
        });
        if (data.status === "error") {
            alert(`Ошибка: ${data.message}`);
            
            return;
        }
        // Если сервер вернул успех
        alert(`${data.message}`);
        loadCaveData(); // Обновляем список шахт, чтобы отобразить изменения (например, разблокированные шахты)

    } catch (error) {
        console.error("Ошибка выбора шахты:", error);
        alert("Ошибка сети!");
    }
}

    // Глобальный клик для закрытия (безопасный вариант)
    window.addEventListener("click", (event) => {
        // Если клик был НЕ по кнопке и НЕ внутри меню
        if (!menuBtn.contains(event.target) && !menuContent.contains(event.target)) {
            // Если меню открыто — закрываем
            if (menuContent.classList.contains("show")) {
                closeCaveMenu();
            }
        }
    });
}


export function toggleMineInterface(show) {
    const mineBlock = document.getElementById("mine_interface");
    
    if (!mineBlock) return; // Защита от ошибок

    if (show) {
        mineBlock.classList.remove("hidden"); // Убираем класс -> блок появляется
    } else {
        mineBlock.classList.add("hidden");    // Добавляем класс -> блок исчезает
    }
}