/* LAN IP + Sync status bar — educational health endpoint is public, sync APIs stay protected. */
function syncJalali(value = new Date()) {
  const d = value instanceof Date ? value : new Date(value);
  return Number.isNaN(d.getTime()) ? "—" : new Intl.DateTimeFormat("fa-IR-u-ca-persian", {year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false}).format(d);
}
async function loadLanAndSync() {
  const lanEl = document.getElementById("lanIp");
  const hintEl = document.getElementById("androidHint");
  const statusEl = document.getElementById("syncStatus");
  if (!lanEl) return;
  try {
    const r = await fetch("/api/health");
    if (!r.ok) throw new Error("HTTP " + r.status);
    const hello = await r.json();
    const ip = hello.lan_ip || "127.0.0.1";
    lanEl.textContent = ip;
    if (hintEl) hintEl.textContent = "http://" + ip + ":5050";
    if (statusEl) {
      const s = hello.stats || {};
      statusEl.textContent =
        "دستگاه: " + (hello.device || "—") +
        " · فصل " + (s.chapters || 0) +
        " · درس " + (s.lessons || 0) +
        " · schema " + (hello.schema_version || 1);
    }
  } catch (e) {
    lanEl.textContent = "خطا";
    if (statusEl) statusEl.textContent = String(e.message || e);
  }
}

document.getElementById("btnCopyIp")?.addEventListener("click", async () => {
  const ip = document.getElementById("lanIp")?.textContent || "";
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
    const r = await fetch("/api/health");
    if (!r.ok) throw new Error("HTTP " + r.status);
    const h = await r.json();
    const s = h.stats || {};
    statusEl.textContent =
      "API سالم · " + (s.chapters || 0) + " فصل · " + (s.lessons || 0) + " درس · " +
      (s.scenarios || 0) + " سناریو · تاریخ شمسی " + syncJalali();
  } catch (e) {
    if (statusEl) statusEl.textContent = "خطا: " + (e.message || e);
  }
});

loadLanAndSync();
