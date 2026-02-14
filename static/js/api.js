// js/api.js
export const tg = window.Telegram.WebApp;

export function getUserId() {
  const user = tg.initDataUnsafe?.user;
  return user?.id;
}

export async function postJson(url, bodyObj) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bodyObj),
  });

  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`HTTP ${r.status} ${text}`);
  }

  return r.json();
}
