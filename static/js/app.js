// js/app.js
import { getUserId, postJson } from "./api.js";
import { initMenu } from "./menu.js";

initMenu();
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
        // Проверь, точно ли адрес API правильный (get_used_coordinates или get_user_coordinates?)
        const response = await fetch("/api/get_used_coordinates", {
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

        coordElement.innerText = `Координаты: (${x}, ${y}) \n 🪐 ${planet}`;
        
    } catch (e) {
        console.error("Ошибка обновления координат:", e);
        coordElement.innerText = "📍 Связь потеряна..."; 
    }
}

// Запускаем один раз сразу при загрузке...
updateUserCoordinate();

// ...и потом каждые 10 секунд
setInterval(() => {
    updateUserCoordinate();
}, 10000);