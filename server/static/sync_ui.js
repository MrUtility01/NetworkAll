/* LAN IP + Sync status bar */
async function syncApi(path) {
  const token = localStorage.getItem("netenc_api_token") || "";
  const headers = token ? { "X-NetEnc-Token": token } : {};
  return fetch(path, { headers });
}

async function loadLanAndSync() {
  const lanEl = document.getElementById("lanIp");
  const hintEl = document.getElementById("androidHint");
  const statusEl = document.getElementById("syncStatus");
  if (!lanEl) return;
  try {
    const r = await syncApi("/api/sync/hello");
    const hello = await r.json();
    if (!r.ok) throw new Error(hello.hint || hello.error || `HTTP ${r.status}`);
    const ip = hello.lan_ip || "127.0.0.1";
    const lanEnabled = hello.lan_enabled === true;
    lanEl.textContent = lanEnabled ? ip : "LAN غیرفعال";
    if (hintEl) hintEl.textContent = lanEnabled
      ? ("http://" + ip + ":5050")
      : "http://127.0.0.1:5050 · فقط همین رایانه";
    if (statusEl) {
      const s = hello.stats || {};
      statusEl.textContent =
        (lanEnabled ? "Sync شبکه فعال" : "حالت امن محلی؛ برای اتصال گوشی LAN را صریحاً فعال کنید") +
        " · فصل " + (s.chapters || 0) +
        " · درس " + (s.lessons || 0) +
        " · schema " + (hello.schema_version || 1);
    }
  } catch (e) {
    lanEl.textContent = "—";
    if (statusEl) statusEl.textContent = "برای Sync توکن را وارد کنید؛ " + String(e.message || e);
  }
}

document.getElementById("btnCopyIp")?.addEventListener("click", async () => {
  const ip = document.getElementById("lanIp")?.textContent || "";
  if (ip === "—") return;
  if (!ip || ip === "—" || ip === "LAN غیرفعال") return;
  const url = "http://" + ip + ":5050";
  try {
    await navigator.clipboard.writeText(url);
    const st = document.getElementById("syncStatus");
    if (st) st.textContent = "کپی شد: " + url;
  } catch {
    prompt("آدرس را کپی کنید:", url);
  }
});

document.getElementById("btnSyncStatus")?.addEventListener("click", async () => {
  const statusEl = document.getElementById("syncStatus");
  if (statusEl) statusEl.textContent = "در حال بررسی…";
  try {
    const r = await syncApi("/api/sync/manifest");
    const m = await r.json();
    if (!r.ok) throw new Error(m.hint || m.error || `HTTP ${r.status}`);
    const n = (m.items || []).length;
    statusEl.textContent =
      "manifest: " + n + " رکورد · schema " + (m.schema_version || 1) +
      " · " + (m.generated_at || "");
  } catch (e) {
    if (statusEl) statusEl.textContent = "خطا: " + (e.message || e);
  }
});

window.addEventListener("netenc-token-set", loadLanAndSync);
loadLanAndSync();
