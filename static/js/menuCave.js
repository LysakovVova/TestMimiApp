// js/menuCave.js
import { tg, getUserId, postJson } from "./api.js";

export function initCaveMenu() {
    // tg.expand(); // Можно оставить, если нужно

    const menuBtn = document.getElementById("menuCaveBtn");
    const caveList = document.getElementById("caveList");
    const menuContent = document.getElementById("menuCaveContent"); // Сам выпадающий блок
    const caveMiningBtn = document.getElementById("caveMiningBtn");
    const miningresult = document.getElementById("miningResult");

    miningresult.style.display = "none"; // Скрываем блок результата при инициализации
    miningresult.innerHTML = ""; // Очищаем текст результата
    caveMiningBtn.style.display = "none"; // Скрываем кнопку добычи при инициализации

    if (!menuBtn || !caveList || !menuContent) {
        console.error("Элементы меню шахт не найдены!");
        return;
    }

    caveMiningBtn.onclick = async () => {

        const userId = getUserId();
        const data = await postJson("/api/mine_cave", { user_id: userId });

        miningresult.style.display = "block"; // Показываем блок результата

        if (data.status === "ok") {
            miningresult.innerHTML = `<h3>Результат добычи в ${data.cave_name}:</h3>`;

            if (data.mined_items && data.mined_items.length > 0) {
                const ul = document.createElement("ul");

                data.mined_items.forEach(item => {
                    const li = document.createElement("li");
                    li.innerText = `${item.item_name}: ${item.count}`;
                    ul.appendChild(li);
                });
                miningresult.appendChild(ul);
            } else {
                miningresult.innerHTML += "<p>Ничего не найдено...</p>";
            }
        } else {
            miningresult.innerHTML = `<p style="color:red;">Ошибка: ${data.message}</p>`;
        }
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
                data.caves.forEach(async cave => {
                    
                    // 1. Создаем обертку
                    const wrapper = document.createElement("div");
                    wrapper.className = "cave-accordion-item";

                    // 2. Создаем заголовок (Название шахты)
                    const headerBtn = document.createElement("button");
                    headerBtn.className = "cave-header-btn";
                    // Добавляем иконку состояния справа
                    const icon = cave.is_unlocked ? "⛏️" : "🔒";
                    headerBtn.innerHTML = `<span>${cave.name}</span> <span>${icon}</span>`;

                    // 3. Создаем блок деталей (скрытый)
                    const detailsDiv = document.createElement("div");
                    detailsDiv.className = "cave-details";

                    // --- ЛОГИКА НАПОЛНЕНИЯ ---
                    if (cave.is_unlocked) {
                        // ВАРИАНТ А: Шахта открыта -> Показываем кнопку "Выбрать"
                        const desc = document.createElement("p");
                        desc.innerText = "Шахта доступна для добычи.";
                        
                        const selectBtn = document.createElement("button");
                        selectBtn.className = "select-mine-btn";
                        selectBtn.innerText = "✅ ВЫБРАТЬ ЭТУ ШАХТУ";
                        
                        // Клик по кнопке выбора
                        selectBtn.onclick = (e) => {
                            e.stopPropagation(); // Не закрываем меню
                            targetMine(cave.id, headerBtn); // Твоя функция выбора
                        };

                        detailsDiv.appendChild(desc);
                        detailsDiv.appendChild(selectBtn);

                    } else {
                        // ВАРИАНТ Б: Шахта закрыта -> Показываем цену
                        const lockedText = document.createElement("div");
                        lockedText.innerHTML = "<strong>Требования для разблокировки:</strong>";
                        
                        const costList = document.createElement("ul");
                        costList.className = "unlock-cost-list";

                        const caveInfo = await postJson("/api/get_cave_info", { user_id: userId, cave_id: cave.id });


                        if (caveInfo.requirements && caveInfo.requirements.length > 0) {
                            caveInfo.requirements.forEach(cost => {
                                const li = document.createElement("li");
                                li.innerText = `- ${cost.item_name}: ${cost.count}`;
                                costList.appendChild(li);
                            });
                        } else {
                            // Заглушка, если данных нет
                            costList.innerHTML = "<li>Бесплатная шахта</li>";
                        }

                        // Можно добавить кнопку "Разблокировать", если хочешь
                        const unlockBtn = document.createElement("button");
                        unlockBtn.className = "select-mine-btn";
                        unlockBtn.innerText = "⛏️ РАЗБЛОКИРОВАТЬ";
                        unlockBtn.onclick = async (e) => {
                            e.stopPropagation();
                            const data = await postJson("/api/unlock_cave", { user_id: userId, cave_id: cave.id });
                            alert(data.message);
                            if (data.status === "ok") {                                
                                loadCaveData(); // Перезагружаем данные, чтобы отобразить изменения
                            }
                        }
                        
                        detailsDiv.appendChild(lockedText);
                        detailsDiv.appendChild(costList);
                        detailsDiv.appendChild(unlockBtn);
                    }

                    // 4. Клик по ЗАГОЛОВКУ -> Открыть/Закрыть детали
                    headerBtn.onclick = (e) => {
                        e.stopPropagation();
                        
                        // Закрываем все остальные открытые шахты (аккордеон) - ОПЦИОНАЛЬНО
                        document.querySelectorAll('.cave-details').forEach(el => {
                            if (el !== detailsDiv) el.classList.remove('open');
                        });

                        // Переключаем текущий
                        detailsDiv.classList.toggle("open");
                    };

                    // Собираем всё вместе
                    wrapper.appendChild(headerBtn);
                    wrapper.appendChild(detailsDiv);
                    caveList.appendChild(wrapper);
                });
            } else {
                caveList.innerHTML = '<div style="padding:10px; color:#aaa;">Шахты не найдены.</div>';
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
        const caveMiningBtn = document.getElementById("caveMiningBtn");
        caveMiningBtn.style.display = "block";
        caveMiningBtn.innerText = `⛏️ Добывать в ${data.cave_name}`;

    } catch (error) {
        console.error("Ошибка выбора шахты:", error);
        alert("Ошибка сети!");
    }
}

    // Глобальный клик для закрытия (безопасный вариант)
    window.addEventListener("click", (event) => {
       const mineBtn = document.getElementById('caveMiningBtn');
        const mineRes = document.getElementById('miningResult');
        const menuContent = document.getElementById('menuCaveContent');
        const menuBtn = document.getElementById('menuCaveBtn');

        // Если элементов нет на странице, выходим (защита от ошибок)
        if (!mineBtn || !mineRes) return;

        // Проверяем, был ли клик ВНУТРИ важных элементов
        const isClickInside = 
            mineBtn.contains(event.target) ||      // Клик по кнопке "Копать"
            mineRes.contains(event.target) ||      // Клик по тексту результата
            menuContent.contains(event.target) ||  // Клик внутри списка шахт
            menuBtn.contains(event.target);        // Клик по кнопке открытия меню

        // Если клик был СНАРУЖИ (не в важных элементах)
        if (!isClickInside) {
            // 1. Скрываем кнопку
            mineBtn.style.display = 'none';
            
            // 2. Скрываем и очищаем результат
            mineRes.style.display = 'none';
            mineRes.innerHTML = ''; 

            // 3. (Важно!) Сбрасываем выбранную шахту, чтобы игрок выбрал заново
            // (Если ты используешь глобальную переменную из прошлого ответа)
            if (typeof currentSelectedCaveId !== 'undefined') {
                currentSelectedCaveId = null;
            }

            // 4. Снимаем подсветку с кнопок в списке (для красоты)
            document.querySelectorAll(".cave-header-btn").forEach(btn => {
                btn.style.color = "#e94560"; // Возвращаем обычный цвет
                btn.style.border = "none";
            });
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