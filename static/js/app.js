// js/app.js
import { getUserId, postJson } from "./api.js";
import { initMenu } from "./menu.js";

initMenu();

async function travelToPlanet(planetId, planetName) {
  if (!confirm(`Отправиться на ${planetName}?`)) return;

  try {
    const user_id = getUserId();
    if (!user_id) return alert("Открыто не из Telegram");

    const data = await postJson("/api/set_target_planet", {
      user_id,
      target_planet_id: planetId,
    });

    alert(data.message);
  } catch (e) {
    console.error(e);
    alert("Ошибка связи с кораблем!");
  }
}

document.getElementById("get_planet").onclick = async () => {
  const out = document.getElementById("res");
  out.innerHTML = "<p>📡 Поиск сигналов...</p>";

  try {
    const user_id = getUserId();
    if (!user_id) {
      out.innerText = "Открыто не из Telegram";
      return;
    }

    const data = await postJson("/api/get_planets", { user_id });

    if (data.planets && data.planets.length > 0) {
      out.innerHTML = "";
      out.innerHTML += `<p><b>${data.user_coordinates.x}:${data.user_coordinates.y}</b> - Ваши координаты</p>`;

      data.planets.forEach((planet) => {
        const btn = document.createElement("button");
        btn.className = "planet-btn btn-travel";
        btn.innerHTML = `🚀 <b>${planet.name}</b> <br><small>Координаты: ${planet.coordinate_x}:${planet.coordinate_y}</small>`;
        btn.onclick = () => travelToPlanet(planet.id, planet.name);
        out.appendChild(btn);
      });
    } else {
      out.innerText = "В этой галактике пусто...";
    }
  } catch (e) {
    console.error(e);
    out.innerText = "Связь потеряна.";
  }
};
