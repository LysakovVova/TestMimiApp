// js/app.js
import { getUserId, postJson } from "./api.js";
import { initMenu } from "./menu.js";
import { initCaveMenu, toggleMineInterface } from "./menuCave.js";

initMenu();
initCaveMenu();
updateUserCoordinate();

export async function updateUserCoordinate() {
    // 1. Ищем правильный ID (как в HTML)
    const coordElement = document.getElementById("user_coordinate");
    
    // Если элемента нет на странице, выходим, чтобы не было ошибок
    if (!coordElement) return;

    const user_id = getUserId();
    if (!user_id) {
        console.warn("Нет user_id, пропускаем обновление координат");
        return;
    }

    try {
        const response = await fetch("/api/get_user_coordinates", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: user_id })
        });

        if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);

        const data = await response.json();
        
        // 2. Обновляем текст
        // Проверяем, есть ли данные, чтобы не писать undefined
        const x = data.coordinate_x ?? "?";
        const y = data.coordinate_y ?? "?";
        const planet = data.planet_name || "Открытый космос";

        if (planet === "Открытый космос") {
            toggleMineInterface(false); // Скрываем интерфейс шахт
        } else{
            toggleMineInterface(true); // Показываем интерфейс шахт
        }

        coordElement.innerText = `Координаты: (${x}, ${y}) \n 🪐 ${planet}`;
        
    } catch (e) {
        console.error("Ошибка обновления координат:", e);
        coordElement.innerText = "📍 Связь потеряна..."; 
    }
}

export async function updateIvent() {
    const modalText = document.getElementById("modalText");
    const modalBtnYes = document.getElementById("modalBtnYes");
    const modalBtnNo = document.getElementById("modalBtnNo");
    const modalWindow = document.getElementById("choiceModal");

    // Если элементы не найдены, выходим, чтобы не было ошибок
    if (!modalText || !modalBtnYes || !modalBtnNo) {
        console.error("Ошибка: Элементы модального окна не найдены в HTML!");
        return;
    }

    const user_id = getUserId();
    if (!user_id) return;

    try {
        // 1. Проверяем, есть ли находка
        const data = await fetch("/api/check_offer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: user_id })
        });

        const result = await data.json();

        // 2. Если находка есть
        if (result.has_offer) {
            
            // Заполняем текст
            modalText.innerText = `Найдено ${result.name} : ${result.count} шт.`;
            
            // Показываем окно
            modalWindow.classList.remove("hidden");

            modalBtnYes.onclick = async () => {
                try {
                    // Блокируем кнопку, чтобы не нажал дважды
                    modalBtnYes.disabled = true; 
                    
                    const response = await postJson("/api/accept_offer", { user_id: user_id });
                        alert(`✅ Вы забрали предмет!\n${response.message}`);
                        modalWindow.classList.add("hidden"); // Закрываем только после успеха
                } catch (e) {
                    console.error(e);
                } finally {
                    modalBtnYes.disabled = false; // Разблокируем кнопку
                }
            };

            // --- ОБРАБОТЧИК КНОПКИ "ОТКАЗАТЬСЯ" ---
            modalBtnNo.onclick = async () => {
                modalWindow.classList.add("hidden");
                // Тут можно добавить запрос на отказ, если нужно очистить событие на сервере
                const response = await postJson("/api/decline_offer", { user_id: user_id });
            };

        } else {
            // Если предложений нет, скрываем окно (на случай если оно висело)
            modalWindow.classList.add("hidden");
        }

    } catch (e) {
        console.error("Ошибка сети при проверке событий:", e);
    }
}

// Запускаем один раз сразу при загрузке...
updateUserCoordinate();
updateIvent();
// ...и потом каждые 10 секунд
setInterval(() => {
    updateUserCoordinate();
    updateIvent();
}, 10000);