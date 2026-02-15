// js/menu.js
import { tg, getUserId, postJson } from "./api.js";
import { updateUserCoordinate } from "./app.js";

export function initMenu() {
  tg.expand();

  const menuBtn = document.getElementById("menuBtn");
  const menuContent = document.getElementById("menuContent");

  const inventoryBtn = document.getElementById("inventoryBtn");
  const inventoryList = document.getElementById("inventoryList");

  const getPlanetBtn = document.getElementById("getPlanetBtn");
  const getPlanetList = document.getElementById("getPlanetList");

  menuBtn.onclick = (e) => {
    e.stopPropagation();
    menuContent.classList.toggle("show");

    if (menuContent.classList.contains("show")) {
      menuBtn.innerText = "❌ ЗАКРЫТЬ";
      menuBtn.style.color = "#e94560";
    } else {
      menuBtn.innerText = "☰ МЕНЮ ИГРЫ";
      menuBtn.style.color = "white";
    }
  };

  window.onclick = (event) => {
    if (!event.target.matches("#menuBtn") && !event.target.matches(".main-menu-btn")) {
      if (menuContent.classList.contains("show")) {
        menuContent.classList.remove("show");
        menuBtn.innerText = "☰ МЕНЮ ИГРЫ";
        menuBtn.style.color = "white";
      }
    }
  };

  document.getElementById("reloadBtn").onclick = () => location.reload();


    // Функция: Что делать при клике на ПРЕДМЕТ
    async function useItem(itemName, itemCount) {
        if (confirm(`Использовать предмет "${itemName}"?`)) {
            // Тут можно отправить запрос на сервер /api/use_item
            alert(`Вы использовали ${itemName}! (Логику нужно дописать в Python)`);
            
            // После использования лучше обновить инвентарь
        }
    }

  // Клик по кнопке "Инвентарь"
  inventoryBtn.onclick = async (e) => {
      e.stopPropagation(); // Чтобы меню не закрылось

      // 1. Если список уже открыт — закрываем его
      if (inventoryList.style.display === "block") {
          inventoryList.style.display = "none";
          inventoryBtn.innerText = "🎒 Инвентарь ▼";
          return;
      }

      // 2. Если закрыт — загружаем данные и открываем
      inventoryBtn.innerText = "🎒 Загрузка...";
      
      try {
          // Запрос к серверу (как мы делали раньше)
          const response = await fetch("/api/get_inventory", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ user_id: tg.initDataUnsafe.user.id })
          });
          
          const data = await response.json();

          // Очищаем старый список
          inventoryList.innerHTML = "";

          if (data.items && data.items.length > 0) {
              // Генерируем кнопки для каждого предмета
              data.items.forEach(item => {
                  const btn = document.createElement("button");
                  btn.className = "inventory-item-btn"; // Наш новый стиль
                  btn.innerText = `🔹 ${item.name} (x${item.count})`;
                  
                  // Вешаем событие клика на предмет
                  btn.onclick = (ev) => {
                      ev.stopPropagation(); // Чтобы меню не закрылось
                      useItem(item.name, item.count);
                  };

                  inventoryList.appendChild(btn);
              });
          } else {
              // Если пусто
              const emptyMsg = document.createElement("div");
              emptyMsg.innerText = "Пусто...";
              emptyMsg.style.padding = "10px";
              emptyMsg.style.color = "#555";
              inventoryList.appendChild(emptyMsg);
          }

          // Показываем список
          inventoryList.style.display = "block";
          inventoryBtn.innerText = "🎒 Инвентарь ▲"; // Меняем стрелочку

      } catch (error) {
          console.error(error);
          inventoryBtn.innerText = "🎒 Ошибка";
      }
  };


  async function travelToPlanet(planetId, planetName) {
  if (!confirm(`Отправиться на ${planetName}?`)) return;

  try {
    const user_id = getUserId();
    if (!user_id) return alert("Открыто не из Telegram");

    const data = await postJson("/api/set_target_planet", {
      user_id,
      target_planet_id: planetId,
    });
    updateUserCoordinate(); // Обновляем координаты после отправки команды
    alert(data.message);
  } catch (e) {
    console.error(e);
    alert("Ошибка связи с кораблем!");
  }
}

  // Клик по кнопке "Сканировать космос"
  getPlanetBtn.onclick = async (e) => {
      e.stopPropagation(); // Чтобы меню не закрылось

      // 1. Если список уже открыт — закрываем его
      if (getPlanetList.style.display === "block") {
          getPlanetList.style.display = "none";
          getPlanetBtn.innerText = "🔭 Сканировать космос ▼";
          return;
      }

      // 2. Если закрыт — загружаем данные и открываем
      getPlanetBtn.innerText = "🔭 Загрузка...";
      
      try {
          // Запрос к серверу (как мы делали раньше)
          const response = await fetch("/api/get_planets", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ user_id: tg.initDataUnsafe.user.id })
          });
          
          const data = await response.json();

          // Очищаем старый список
          getPlanetList.innerHTML = "";

          if (data.planets && data.planets.length > 0) {
              // Генерируем кнопки для каждого планеты
              data.planets.forEach(planet => {
                  const btn = document.createElement("button");
                  btn.className = "planet-item-btn"; // Наш новый стиль
                  btn.innerText = `🔹 ${planet.name} (${planet.coordinate_x},${planet.coordinate_y})`;
                  
                  // Вешаем событие клика на предмет
                  btn.onclick = (ev) => {
                      ev.stopPropagation(); // Чтобы меню не закрылось
                      travelToPlanet(planet.id, planet.name);
                  };

                  getPlanetList.appendChild(btn);
              });
          } else {
              // Если пусто
              const emptyMsg = document.createElement("div");
              emptyMsg.innerText = "Пусто...";
              emptyMsg.style.padding = "10px";
              emptyMsg.style.color = "#555";
              getPlanetList.appendChild(emptyMsg);
          }

          // Показываем список
          getPlanetList.style.display = "block";
          getPlanetBtn.innerText = "🔭 Сканировать космос ▲"; // Меняем стрелочку

      } catch (error) {
          console.error(error);
          getPlanetBtn.innerText = "🔭 Ошибка";
      }
  };
}
