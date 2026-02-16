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

  const requirementsBtn = document.getElementById("requirementsBtn");
  const requirementsList = document.getElementById("requirementsList");

  const choiceShipBtn = document.getElementById("choiceShipBtn");
  const choiceShipList = document.getElementById("choiceShipList");
  const menuShipContent = document.getElementById("menuShipContent");

  menuBtn.onclick = (e) => {
    e.stopPropagation();
    menuContent.classList.toggle("show");

    if (menuContent.classList.contains("show")) {
      menuBtn.innerText = "❌ ЗАКРЫТЬ";
      menuBtn.style.color = "white";
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

  function animateListOpen(listElement) {
    listElement.style.display = "block";
    listElement.classList.remove("list-fade-in");
    void listElement.offsetWidth;
    listElement.classList.add("list-fade-in");
  }


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
                  btn.className = "cave-item-btn"; // Наш новый стиль
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

          // Показываем список с анимацией
          animateListOpen(inventoryList);
          inventoryBtn.innerText = "🎒 Инвентарь ▲"; // Меняем стрелочку

      } catch (error) {
          console.error(error);
          inventoryBtn.innerText = "🎒 Ошибка";
      }
  };

  function closePlanetList() {
    getPlanetList.style.display = "none";
    getPlanetList.classList.remove("list-fade-in");
    getPlanetBtn.innerText = "🔭 Сканировать космос ▼";
  }

  function openPlanetList() {
    animateListOpen(getPlanetList);
    getPlanetBtn.innerText = "🔭 Сканировать космос ▲";
  }

  function isPlanetListOpen() {
    return getPlanetList.style.display === "block";
  }

  function addPlanetButton(planetId, planetLabel) {
    const btn = document.createElement("button");
    btn.className = "planet-item-btn";
    btn.innerText = planetLabel;
    btn.onclick = (event) => {
      event.stopPropagation();
      travelToPlanet(planetId, planetLabel.replace(/^🔹\s*/, ""));
    };
    getPlanetList.appendChild(btn);
  }

  let isTravelInProgress = false;
  async function travelToPlanet(planetId, planetName) {
    if (isTravelInProgress) return;
    isTravelInProgress = true;

    const isConfirmed = confirm(`Отправиться на ${planetName}?`);
    if (!isConfirmed) {
      isTravelInProgress = false;
      return;
    }

    const userId = getUserId();
    if (!userId) {
      alert("Открыто не из Telegram");
      isTravelInProgress = false;
      return;
    }

    closePlanetList();

    try {
      getPlanetBtn.innerText = "🔭 Путешествие...";

      const data = await postJson("/api/set_target_planet", {
        user_id: userId,
        target_planet_id: planetId,
      });

      const status = data?.status || data?.result || "ok";
      alert(data?.message || (status === "error" ? "Не удалось установить цель планеты" : "Команда отправлена."));
      if (status === "error") return;

      await updateUserCoordinate();

      // Сбрасываем выбор шахты при путешествии, но не мешаем основному действию
      postJson("/api/choice_cave", { user_id: userId, cave_id: 0 }).catch((resetErr) => {
        console.warn("Не удалось сбросить выбор шахты:", resetErr);
      });
    } catch (error) {
      console.error(error);
      alert(`Ошибка: ${error.message || "не удалось выполнить запрос"}`);
    } finally {
      isTravelInProgress = false;
      closePlanetList();
    }
  }

  // Клик по кнопке "Сканировать космос"
  getPlanetBtn.onclick = async (e) => {
    e.stopPropagation();

    if (isPlanetListOpen()) {
      closePlanetList();
      return;
    }

    const userId = getUserId();
    if (!userId) {
      alert("Открыто не из Telegram");
      return;
    }

    getPlanetBtn.innerText = "🔭 Загрузка...";

    try {
      const data = await postJson("/api/get_planets", { user_id: userId });
      getPlanetList.innerHTML = "";

      if (data.planets && data.planets.length > 0) {
        data.planets.forEach((planet) => {
          addPlanetButton(planet.id, `🔹 ${planet.name} (${planet.coordinate_x},${planet.coordinate_y})`);
        });
        addPlanetButton(0, "🔹 Открытый космос (стоп)");
      } else {
        const emptyMsg = document.createElement("div");
        emptyMsg.innerText = "Пусто...";
        emptyMsg.style.padding = "10px";
        emptyMsg.style.color = "#555";
        getPlanetList.appendChild(emptyMsg);
      }

      openPlanetList();
    } catch (error) {
      console.error(error);
      getPlanetBtn.innerText = "🔭 Ошибка";
    }
  };

  requirementsBtn.onclick = async (e) => {
    e.stopPropagation();

    if (requirementsList.style.display === "block") {
      closeCreateMenu();
      return;
    }

    requirementsBtn.innerText = "📋 Создание ▲";
    requirementsList.style.display = "block";
    await loadCreateData();
  };

  function closeCreateMenu() {
    requirementsList.style.display = "none";
    requirementsBtn.innerText = "📋 Создание ▼";
  }

  async function loadCreateData() {
    requirementsList.innerHTML = '<div style="padding:10px; color:#aaa;">⏳ Поиск рецептов...</div>';

    try {
      const userId = getUserId();
      if (!userId) {
        requirementsList.innerHTML = '<div style="padding:10px;">Откройте mini app в Telegram.</div>';
        return;
      }

      const data = await postJson("/api/get_create_items", { user_id: userId });
      requirementsList.innerHTML = "";

      if (!data.items || data.items.length === 0) {
        requirementsList.innerHTML = '<div style="padding:10px;">Рецепты не найдены.</div>';
        return;
      }

      for (const item of data.items) {
        const wrapper = document.createElement("div");
        wrapper.className = "cave-accordion-item";

        const headerBtn = document.createElement("button");
        headerBtn.className = "cave-header-btn";
        const icon = item.can_create ? "✅" : "🧩";
        headerBtn.innerHTML = `🔹 <span>${item.name}</span> <span>${icon}</span>`;

        const detailsDiv = document.createElement("div");
        detailsDiv.className = "cave-details";

        const reqTitle = document.createElement("div");
        reqTitle.innerHTML = "<strong>Требования:</strong>";
        detailsDiv.appendChild(reqTitle);

        const reqList = document.createElement("ul");
        reqList.className = "unlock-cost-list";
        reqList.innerHTML = "<li>⏳ Загрузка...</li>";
        detailsDiv.appendChild(reqList);

        const createBtn = document.createElement("button");
        createBtn.className = "unlock-ship-btn";
        createBtn.innerText = "🛠 СОЗДАТЬ";
        createBtn.onclick = async (event) => {
          event.stopPropagation();
          if (!confirm(`Создать предмет "${item.name}"?`)) return;

          try {
            const res = await postJson("/api/create_item", {
              user_id: userId,
              item_id: item.id,
            });
            alert(res.message || "Готово");
            if (res.status === "ok") {
              await loadCreateData();
            }
          } catch (err) {
            console.error("Ошибка создания:", err);
            alert(`Ошибка: ${err.message || "не удалось создать предмет"}`);
          }
        };

        try {
          const recipe = await postJson("/api/get_create_item_info", {
            user_id: userId,
            item_id: item.id,
          });

          reqList.innerHTML = "";
          if (recipe.requirements && recipe.requirements.length > 0) {
            recipe.requirements.forEach((req) => {
              const li = document.createElement("li");
              li.style.color = req.enough ? "#9eff9e" : "#ff6b6b";
              li.innerText = `- ${req.item_name}: ${req.have_count}/${req.count}`;
              reqList.appendChild(li);
            });
          } else {
            reqList.innerHTML = "<li>Рецепт пуст</li>";
          }
        } catch (err) {
          reqList.innerHTML = "<li>Ошибка получения требований</li>";
        }

        detailsDiv.appendChild(createBtn);

        headerBtn.onclick = (event) => {
          event.stopPropagation();
          document.querySelectorAll(".cave-details").forEach((el) => {
            if (el !== detailsDiv) el.classList.remove("open");
          });
          detailsDiv.classList.toggle("open");
        };

        wrapper.appendChild(headerBtn);
        wrapper.appendChild(detailsDiv);
        requirementsList.appendChild(wrapper);
      }
    } catch (err) {
      console.error(err);
      requirementsList.innerHTML = '<div style="color:red; padding:10px;">Ошибка загрузки рецептов!</div>';
    }
  }

  choiceShipBtn.onclick = async (e) => {
    e.stopPropagation();

    const isHidden = menuShipContent.style.display === "none";
    if (isHidden) {
      menuShipContent.style.display = "block";
      choiceShipBtn.innerText = "🔍 Выбор Корабля ▲";
      await loadChoiceShipData();
    } else {
      closeShipMenu();
    }
  };

  function closeShipMenu() {
    menuShipContent.style.display = "none";
    choiceShipList.style.display = "none";
    choiceShipBtn.innerText = "🔍 Выбор Корабля ▼";
  }

  async function loadChoiceShipData() {
    choiceShipList.style.display = "block";
    choiceShipList.innerHTML = '<div style="padding:10px; color:#aaa;">⏳ Поиск кораблей...</div>';

    try {
      const userId = getUserId();
      const data = await postJson("/api/get_ship", { user_id: userId });
      choiceShipList.innerHTML = "";

      if (!data.ships || data.ships.length === 0) {
        choiceShipList.innerHTML = '<div style="padding:10px;">Корабли не найдены.</div>';
        return;
      }

      for (const ship of data.ships) {
        const wrapper = document.createElement("div");
        wrapper.className = "cave-accordion-item";

        const headerBtn = document.createElement("button");
        headerBtn.className = "cave-header-btn";
        const icon = ship.is_unlocked ? "🚀" : "🔒";
        headerBtn.innerHTML = `🔹 <span>${ship.name}</span> <span>${icon}</span>`;

        const detailsDiv = document.createElement("div");
        detailsDiv.className = "cave-details";

        if (ship.is_unlocked) {
          const desc = document.createElement("p");
          desc.innerText = "Корабль готов к полету.";

          const selectBtn = document.createElement("button");
          selectBtn.className = "select-mine-btn";
          selectBtn.innerText = "✅ ВЫБРАТЬ ЭТОТ КОРАБЛЬ";
          selectBtn.onclick = (event) => {
            event.stopPropagation();
            targetShip(ship.id, headerBtn);
          };

          detailsDiv.appendChild(desc);
          detailsDiv.appendChild(selectBtn);
        } else {
          const lockedText = document.createElement("div");
          lockedText.innerHTML = "<strong>Требования:</strong>";

          const costList = document.createElement("ul");
          costList.className = "unlock-cost-list";
          costList.innerHTML = "<li>⏳ Загрузка требований...</li>";

          detailsDiv.appendChild(lockedText);
          detailsDiv.appendChild(costList);

          const createUnlockButton = () => {
            const unlockBtn = document.createElement("button");
            unlockBtn.className = "unlock-ship-btn";
            unlockBtn.innerText = "🛠 РАЗБЛОКИРОВАТЬ";
            unlockBtn.onclick = async (event) => {
              event.stopPropagation();
              if (!confirm(`Разблокировать ${ship.name}?`)) return;

              const res = await postJson("/api/unlock_ship", { user_id: userId, ship_id: ship.id });
              alert(res.message);
              if (res.status === "ok") {
                loadChoiceShipData();
              }
            };
            return unlockBtn;
          };

          try {
            const shipInfo = await postJson("/api/get_ship_info", { ship_id: ship.id });
            costList.innerHTML = "";

            if (shipInfo.requirements && shipInfo.requirements.length > 0) {
              shipInfo.requirements.forEach((req) => {
                const li = document.createElement("li");
                li.innerText = `- ${req.item_name}: ${req.count}`;
                costList.appendChild(li);
              });
            } else {
              costList.innerHTML = "<li>Бесплатный</li>";
            }

            detailsDiv.appendChild(createUnlockButton());
          } catch (err) {
            costList.innerHTML = "<li>Ошибка получения цены</li>";
          }
        }

        headerBtn.onclick = (event) => {
          event.stopPropagation();
          document.querySelectorAll(".cave-details").forEach((el) => {
            if (el !== detailsDiv) el.classList.remove("open");
          });
          detailsDiv.classList.toggle("open");
        };

        wrapper.appendChild(headerBtn);
        wrapper.appendChild(detailsDiv);
        choiceShipList.appendChild(wrapper);
      }
    } catch (e) {
      console.error(e);
      choiceShipList.innerHTML = '<div style="color:red; padding:10px;">Ошибка загрузки списка!</div>';
    }
  }

  async function targetShip(shipId, buttonElement) {
    try {
      const userId = getUserId(); // Получаем ID игрока

      const data = await postJson("/api/choice_ship", {
        user_id: userId,
        ship_id: shipId
      });
      if (data.status === "error") {
        alert(`Ошибка: ${data.message}`);
        return;
      }

      alert(`${data.message}`);
    } catch (error) {
      console.error("Ошибка выбора корабля:", error);
      alert("Ошибка сети!");
    }
  }

}
