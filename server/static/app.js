/* بارگذاری تنبل: فصل‌ها یک‌جا؛ سطح و درس فقط با کلیک */
const $ = (s) => document.querySelector(s);
const chaptersEl = $("#chapters");
const viewer = $("#viewer");
const breadcrumb = $("#breadcrumb");
const statsEl = $("#stats");

const state = {
  chapters: [],
  openCh: null,
  openLv: null,
  levelsCache: {}, // chapterId -> levels[]
  lessonsCache: {}, // levelId -> lessons[]
};

async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function loadStats() {
  try {
    const s = await api("/api/stats");
    statsEl.textContent = `${s.chapters} فصل · ${s.levels} زیر‌فصل · ${s.lessons} درس · ${s.scenarios} سناریو · دارای محتوا: ${s.with_content}`;
  } catch (e) {
    statsEl.textContent = "خطا در آمار";
  }
}

async function loadChapters() {
  chaptersEl.innerHTML = `<div class="loading">بارگذاری فهرست فصل‌ها…</div>`;
  const list = await api("/api/chapters");
  state.chapters = list;
  chaptersEl.innerHTML = "";
  if (!list.length) {
    chaptersEl.innerHTML = `<div class="loading">درخت فصل‌ها خالی است؛ نصب تازه و Seed محتوا را بررسی کنید.</div>`;
    return;
  }
  list.forEach((ch) => {
    const wrap = document.createElement("div");
    wrap.className = "ch-item";
    wrap.dataset.cid = ch.id;
    wrap.innerHTML = `
      <button type="button" class="ch-btn" data-id="${ch.id}">
        <span class="caret">▶</span>
        <span class="ch-title">${escapeHtml(ch.title_fa)}</span>
        <span class="badge">${ch.order_index}</span>
      </button>
      <div class="nested" id="ch-nest-${ch.id}"></div>`;
    chaptersEl.appendChild(wrap);
  });
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

chaptersEl.addEventListener("click", async (e) => {
  const chBtn = e.target.closest(".ch-btn");
  const lvBtn = e.target.closest(".lv-btn");
  const lesBtn = e.target.closest(".les-btn");
  if (chBtn) return onChapterClick(chBtn);
  if (lvBtn) return onLevelClick(lvBtn);
  if (lesBtn) return onLessonClick(lesBtn);
});

async function onChapterClick(btn) {
  const id = +btn.dataset.id;
  const nest = document.getElementById(`ch-nest-${id}`);
  const caret = btn.querySelector(".caret");
  const isOpen = nest.classList.contains("open");

  // بستن بقیه اختیاری — فقط همین را toggle
  if (isOpen) {
    nest.classList.remove("open");
    caret.textContent = "▶";
    btn.classList.remove("active");
    return;
  }

  document.querySelectorAll(".ch-btn.active").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  caret.textContent = "▼";
  nest.classList.add("open");
  nest.innerHTML = `<div class="loading">بارگذاری زیر‌فصل‌ها…</div>`;
  breadcrumb.textContent = btn.querySelector(".ch-title").textContent;

  try {
    let levels = state.levelsCache[id];
    if (!levels) {
      const data = await api(`/api/chapters/${id}/levels`);
      levels = Array.isArray(data) ? data : (Array.isArray(data && data.levels) ? data.levels : []);
      state.levelsCache[id] = levels;
    }
    if (!levels.length) {
      nest.innerHTML = `<div class="loading">زیر‌فصلی نیست</div>`;
      return;
    }
    nest.innerHTML = levels
      .map(
        (lv) => `
      <div class="lv-item" data-lid="${lv.id}">
        <button type="button" class="lv-btn" data-id="${lv.id}" data-cid="${id}">
          <span class="caret">▶</span>
          <span class="ch-title">${escapeHtml(lv.title_fa)}</span>
        </button>
        <div class="nested" id="lv-nest-${lv.id}"></div>
      </div>`
      )
      .join("");
  } catch (err) {
    nest.innerHTML = `<div class="loading">خطا: ${escapeHtml(err.message)}</div>`;
  }
}

async function onLevelClick(btn) {
  const id = +btn.dataset.id;
  const nest = document.getElementById(`lv-nest-${id}`);
  const caret = btn.querySelector(".caret");
  if (nest.classList.contains("open")) {
    nest.classList.remove("open");
    caret.textContent = "▶";
    btn.classList.remove("active");
    return;
  }
  document.querySelectorAll(".lv-btn.active").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  caret.textContent = "▼";
  nest.classList.add("open");
  nest.innerHTML = `<div class="loading">بارگذاری درس‌ها…</div>`;

  try {
    let lessons = state.lessonsCache[id];
    if (!lessons) {
      const data = await api(`/api/levels/${id}/lessons`);
      lessons = Array.isArray(data) ? data : (Array.isArray(data && data.lessons) ? data.lessons : []);
      state.lessonsCache[id] = lessons;
    }
    if (!lessons.length) {
      nest.innerHTML = `<div class="loading">درسی نیست</div>`;
      return;
    }
    nest.innerHTML = lessons
      .map(
        (les) => `
      <div class="les-item">
        <button type="button" class="les-btn" data-id="${les.id}">
          <span class="dot ${les.has_content ? "ok" : ""}"></span>
          <span class="ch-title">${escapeHtml(les.title_fa)}</span>
          <span class="badge">${escapeHtml(les.tags || "")}</span>
        </button>
      </div>`
      )
      .join("");
  } catch (err) {
    nest.innerHTML = `<div class="loading">خطا: ${escapeHtml(err.message)}</div>`;
  }
}

async function onLessonClick(btn) {
  const id = +btn.dataset.id;
  document.querySelectorAll(".les-btn.active").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  viewer.innerHTML = `<div class="loading">بارگذاری درس…</div>`;
  try {
    const les = await api(`/api/lessons/${id}`);
    // Specialty material is supplemental and must never prevent the base lesson from opening.
    try {
      const depth = await api(`/api/lessons/${id}/specialized-depth`);
      if (depth && depth.available) les.specialized_depth = depth;
    } catch (depthError) {
      console.warn("Optional specialty content unavailable", depthError);
    }
    breadcrumb.textContent = les.title_fa;
    renderLesson(les);
  } catch (err) {
    viewer.innerHTML = `<div class="loading">خطا: ${escapeHtml(err.message)}</div>`;
  }
}

function renderLesson(les) {
  const tag = (les.tags || "L0").toLowerCase();
  const tabs = [
    { id: "summary", label: "خلاصه", body: les.summary },
    { id: "content", label: "درس کامل", body: les.full_content },
    { id: "commands", label: "دستورات", body: les.commands },
    { id: "examples", label: "مثال‌ها", body: les.examples },
    { id: "notes", label: "عیب‌یابی / نکات", body: les.notes },
    { id: "objectives", label: "اهداف یادگیری", body: les.learning_objectives },
    { id: "meta", label: "Meta / پرامپت", body: formatMeta(les) },
  ];
  if (les.specialized_depth && les.specialized_depth.available) {
    tabs.splice(tabs.length - 1, 0, {
      id: "specialized_depth",
      label: "عمق تخصصی",
      body: formatSpecializedDepth(les.specialized_depth),
    });
  }

  viewer.innerHTML = `
    <div class="lesson-card">
      <h1>${escapeHtml(les.title_fa)}</h1>
      <div class="meta-row">
        <span class="chip ${tag}">${escapeHtml(les.tags || "")}</span>
        <span class="chip">${escapeHtml(les.title_en || "")}</span>
        <span class="chip">وضعیت منبع: ${escapeHtml(les.source_status || "unverified")}</span>
      </div>
      <div class="study-actions"><button id="btnMarkStudied" type="button" class="ghost">✓ یاد گرفتم</button><button id="btnMarkReview" type="button" class="ghost">برای مرور علامت بزن</button><span id="studyMarkStatus" class="muted"></span></div><div class="tabs">
        ${tabs.map((t, i) => `<button type="button" class="tab ${i === 0 ? "active" : ""}" data-tab="${t.id}">${t.label}</button>`).join("")}
      </div>
      ${tabs
        .map(
          (t, i) =>
            `<div class="panel ${i === 0 ? "active" : ""}" id="panel-${t.id}">${
              t.body && String(t.body).trim()
                ? escapeHtml(t.body)
                : `<span class="empty-hint">محتوا هنوز پر نشده — از AI یا ویرایش بعدی پر می‌شود. عنوان و Meta آماده است.</span>`
            }</div>`
        )
        .join("")}
    </div>`;

  const markStudy = async (action) => { try { await api("/api/study/mark", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({uid:les.uid, action})}); const el=document.getElementById("studyMarkStatus"); if(el) el.textContent=action==="studied" ? "در مسیر یادگیری ثبت شد" : "برای مرور دوباره ثبت شد"; } catch(err) { const el=document.getElementById("studyMarkStatus"); if(el) el.textContent="ثبت پیشرفت انجام نشد: "+err.message; } };
  document.getElementById("btnMarkStudied").addEventListener("click", function(){markStudy("studied");});
  document.getElementById("btnMarkReview").addEventListener("click", function(){markStudy("again");});
  viewer.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      viewer.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
      viewer.querySelectorAll(".panel").forEach((x) => x.classList.remove("active"));
      tab.classList.add("active");
      const p = document.getElementById(`panel-${tab.dataset.tab}`);
      if (p) p.classList.add("active");
    });
  });
}

function formatSpecializedDepth(depth) {
  const parts = [];
  if (depth.notice_fa) parts.push(`وضعیت: ${depth.review_status || "review_required"}\n${depth.notice_fa}`);
  if (depth.extra_full) parts.push(String(depth.extra_full));
  if (depth.extra_commands) parts.push(`## دستورات تکمیلی\n\n${depth.extra_commands}`);
  if (depth.extra_lab) parts.push(`## لابراتوار تکمیلی\n\n${depth.extra_lab}`);
  if (depth.extra_notes) parts.push(`## نکات تکمیلی\n\n${depth.extra_notes}`);
  return parts.join("\n\n");
}

function formatMeta(les) {
  const m = les.meta || {};
  const lines = [
    "=== پرامپت تدریس ===",
    m.ai_teach_prompt || "",
    "",
    "=== پرامپت جستجو ===",
    m.ai_search_prompt || les.search_query || "",
    "",
    "=== پرامپت عیب‌یابی ===",
    m.ai_troubleshoot_prompt || "",
    "",
    "=== حلقه مهندسی ===",
    (m.engineering_loop || []).join(" → "),
  ];
  return lines.join("\n");
}

async function showScenarios() {
  breadcrumb.textContent = "سناریوهای Incident و عیب‌یابی واقعی";
  viewer.innerHTML = '<div class="loading">بارگذاری Runbookهای عیب‌یابی…</div>';
  try {
    const rows = await api("/api/incidents");
    viewer.innerHTML =
      '<div class="page-head"><div><div class="eyebrow">INCIDENT RESPONSE / RUNBOOK</div><h1>سناریوی واقعی؛ از علائم تا علت ریشه‌ای</h1>' +
      '<p class="muted">هر سناریو شامل محیط، اثر کسب‌وکار، شواهد، فرمان‌های Verify، شاخهٔ تصمیم، Fix، Rollback و معیار پذیرش است.</p></div>' +
      '<button type="button" id="btnShowCapstones" class="ghost">سناریوهای طراحی (Capstone)</button></div>' +
      '<div class="incident-list">' + rows.map(function (s) {
        const symptoms = Array.isArray(s.symptoms) ? s.symptoms.slice(0, 2).join(" · ") : "";
        return '<article class="incident-card" role="button" tabindex="0" data-id="' + escapeHtml(s.id) + '">' +
          '<div class="eyebrow">' + escapeHtml(s.code) + ' · ' + escapeHtml(s.domain) + '</div>' +
          '<h3>' + escapeHtml(s.title_fa) + '</h3><div class="meta-row">' +
          '<span class="chip">' + escapeHtml(s.severity) + '</span><span class="chip">' + escapeHtml(s.duration) + '</span></div>' +
          '<p>' + escapeHtml(s.impact) + '</p><p><strong>علائم:</strong> ' + escapeHtml(symptoms) + '</p>' +
          '<div class="open-hint">بازکردن Runbook مرحله‌به‌مرحله ←</div></article>';
      }).join("") + '</div>';
    document.getElementById("btnShowCapstones").addEventListener("click", showCapstones);
    viewer.querySelectorAll(".incident-card").forEach(function (card) {
      card.addEventListener("click", function () { loadIncidentDetail(card.dataset.id); });
      card.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") { event.preventDefault(); loadIncidentDetail(card.dataset.id); }
      });
    });
  } catch (err) {
    viewer.innerHTML = '<div class="card"><h2>Runbookها بارگذاری نشدند</h2><p>' + escapeHtml(err.message) + '</p><button id="btnRetryIncidents" type="button">تلاش دوباره</button></div>';
    document.getElementById("btnRetryIncidents").addEventListener("click", showScenarios);
  }
}

async function loadIncidentDetail(id) {
  viewer.innerHTML = '<div class="loading">بارگذاری شواهد و مراحل حادثه…</div>';
  try {
    const sc = await api("/api/incidents/" + encodeURIComponent(id));
    breadcrumb.textContent = sc.code + " — " + sc.title_fa;
    renderIncidentDetail(sc);
  } catch (err) {
    viewer.innerHTML = '<div class="card">خطا در بارگذاری سناریو: ' + escapeHtml(err.message) +
      '<p><button type="button" id="btnRetryIncidentDetail">تلاش دوباره</button> <button type="button" id="btnBackIncidents" class="ghost">بازگشت</button></p></div>';
    document.getElementById("btnRetryIncidentDetail").addEventListener("click", function () { loadIncidentDetail(id); });
    document.getElementById("btnBackIncidents").addEventListener("click", showScenarios);
  }
}

function incidentFlowHtml(sc) {
  const symptom = Array.isArray(sc.symptoms) ? sc.symptoms.slice(0, 2).join(" · ") : String(sc.symptoms || "");
  const steps = Array.isArray(sc.diagnostic_steps) ? sc.diagnostic_steps : [];
  const evidence = steps.length ? steps[0].title + " — " + (steps[0].purpose || "") : "ثبت شاهد از لاگ، Counter یا Capture";
  const nodes = [
    ["۱", "علائم", symptom || sc.impact || "علامت را از کاربر ثبت کن"],
    ["۲", "تعیین دامنه", sc.domain || "سرویس، VLAN یا subnet تحت‌تأثیر را پیدا کن"],
    ["۳", "شواهد", evidence],
    ["۴", "علت ریشه‌ای", sc.root_cause || "فرضیه را با شاهد تأیید کن"],
    ["۵", "اصلاح کنترل‌شده", sc.fix_summary || "کمترین تغییر قابل بازگشت"],
    ["۶", "Verify / Rollback", sc.verification || "معیار قبولی را دوباره تست کن"]
  ];
  return '<section class="card incident-flow"><div class="eyebrow">INCIDENT FLOW / RCA</div>' +
    '<h2>نقشهٔ جریان این حادثه</h2><p class="muted">از چپ به راست/در ترتیب شماره‌ها حرکت کن. اگر شاهد با انتظار نمی‌خواند، به فرضیهٔ بعدی برگرد؛ مستقیم سراغ تغییر پیکربندی نرو.</p>' +
    '<div class="incident-flow-grid">' + nodes.map(function (node, index) {
      const detail = String(node[2] || "").trim();
      const shortDetail = detail.length > 132 ? detail.slice(0, 129) + "…" : detail;
      return '<article class="incident-flow-node"><span class="flow-number">' + node[0] + '</span>' +
        '<h3>' + escapeHtml(node[1]) + '</h3><p>' + escapeHtml(shortDetail) + '</p></article>' +
        (index < nodes.length - 1 ? '<span class="incident-flow-arrow" aria-hidden="true">←</span>' : "");
    }).join("") + '</div></section>';
}

function renderIncidentDetail(sc) {
  const symptoms = Array.isArray(sc.symptoms) ? sc.symptoms.map(function (x) { return "• " + x; }).join("\n") : sc.symptoms;
  const environment = sc.environment || "";
  const steps = Array.isArray(sc.diagnostic_steps) ? sc.diagnostic_steps : [];
  const details = [
    section("محیط و توپولوژی نمونه", environment),
    section("زمان‌بندی حادثه", sc.timeline),
    section("وضعیت اولیه", sc.initial_state),
    section("اثر روی کاربران / کسب‌وکار", sc.impact),
    section("علائم ثبت‌شده", symptoms),
  ].join("");
  const end = [
    section("علت ریشه‌ای و شواهد تأییدکننده", sc.root_cause),
    section("اصلاح پیشنهادی", sc.fix_summary),
    section("معیار پذیرش / Verify", sc.verification),
    section("Rollback امن", sc.rollback),
    section("پیشگیری از تکرار", sc.prevention),
  ].join("");
  viewer.innerHTML =
    '<div class="page-head"><div><div class="eyebrow">' + escapeHtml(sc.code) + ' · ' + escapeHtml(sc.domain) +
    '</div><h1>' + escapeHtml(sc.title_fa) + '</h1><div class="meta-row"><span class="chip">' + escapeHtml(sc.severity) +
    '</span><span class="chip">' + escapeHtml(sc.duration) + '</span><span class="chip">' + escapeHtml(sc.title_en || "") +
    '</span></div></div><button id="btnBackIncidents" type="button" class="ghost">← فهرست سناریوها</button></div>' +
    '<div class="notice">این یک محیط تمرینی با IP/hostname نمونه است. فرمان‌های مشاهده را ابتدا اجرا کن؛ فرمان تغییردهنده را فقط بعد از تأیید توپولوژی، ذخیرهٔ baseline، مجوز Change و آماده‌بودن Rollback اجرا کن.</div>' +
    details + incidentFlowHtml(sc) +
    '<div class="card"><div class="page-head"><div><h2>مراحل تشخیص و رفع</h2><p class="muted">هر گام را بعد از ثبت شاهد تیک بزن. اگر خروجی با انتظار فرق دارد، شاخهٔ «اگر نتیجه فرق داشت» را دنبال کن؛ مراحل را تصادفی رد نکن.</p></div>' +
    '<button id="btnResetRunbook" type="button" class="ghost">پاک‌کردن تیک‌ها</button></div>' +
    '<div class="runbook-progress"><span id="runbookProgressBar"></span></div><div id="runbookProgressLabel" class="muted">۰ از ' + steps.length + ' گام تأیید شده</div></div>' +
    steps.map(function (step, index) {
      const commands = String(step.commands || "");
      return '<article class="runbook-step"><label class="step-check-label"><input type="checkbox" class="step-check" data-step="' + index +
        '"> انجام شد؛ شاهد را ثبت کرده‌ام</label><h3>' + escapeHtml(step.title) + '</h3><p>' + escapeHtml(step.purpose || "") +
        '</p><div class="step-label">فرمان / ابزار</div><pre>' + escapeHtml(commands) + '</pre><button type="button" class="ghost copy-command" data-copy="' +
        escapeHtml(commands) + '">کپی فرمان‌ها</button><div class="step-label">خروجی مورد انتظار</div><div class="expected">' +
        escapeHtml(step.expected || "") + '</div><div class="step-label">اگر خروجی با انتظار فرق داشت</div><div class="branch"><strong>بر اساس شاهد:</strong> ' +
        escapeHtml(step.if_match || "") + '<br><br><strong>اگر شاهد تأیید نشد:</strong> ' + escapeHtml(step.if_not_match || "") +
        '</div></article>';
    }).join("") +
    '<h2>بستن حادثه</h2>' + end +
    '<div class="actions"><button id="btnBackIncidentsBottom" type="button" class="ghost">بازگشت به فهرست</button>' +
    '<button id="btnCopyIncidentSummary" type="button">کپی خلاصهٔ Runbook</button></div>';
  document.getElementById("btnBackIncidents").addEventListener("click", showScenarios);
  document.getElementById("btnBackIncidentsBottom").addEventListener("click", showScenarios);
  function updateRunbookProgress() {
    const boxes = Array.from(viewer.querySelectorAll(".step-check"));
    const done = boxes.filter(function (box) { return box.checked; }).length;
    const bar = document.getElementById("runbookProgressBar");
    const label = document.getElementById("runbookProgressLabel");
    if (bar) bar.style.width = (boxes.length ? Math.round(done * 100 / boxes.length) : 0) + "%";
    if (label) label.textContent = done + " از " + boxes.length + " گام تأیید شده";
  }
  viewer.querySelectorAll(".step-check").forEach(function (box) { box.addEventListener("change", updateRunbookProgress); });
  document.getElementById("btnResetRunbook").addEventListener("click", function () {
    viewer.querySelectorAll(".step-check").forEach(function (box) { box.checked = false; });
    updateRunbookProgress();
  });
  viewer.querySelectorAll(".copy-command").forEach(function (button) {
    button.addEventListener("click", async function () {
      const ok = await copyText(button.getAttribute("data-copy") || "");
      button.textContent = ok ? "کپی شد ✓" : "کپی نشد؛ متن را دستی انتخاب کن";
    });
  });
  document.getElementById("btnCopyIncidentSummary").addEventListener("click", async function () {
    const summary = [sc.code, sc.title_fa, sc.environment, sc.timeline, sc.root_cause, sc.fix_summary,
      sc.verification, "Rollback: " + sc.rollback].join("\n\n");
    const ok = await copyText(summary);
    this.textContent = ok ? "خلاصه کپی شد ✓" : "کپی نشد";
  });
  updateRunbookProgress();
}

async function copyText(value) {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(value);
      return true;
    }
  } catch (e) {}
  try {
    const box = document.createElement("textarea");
    box.value = value;
    box.style.position = "fixed";
    box.style.opacity = "0";
    document.body.appendChild(box);
    box.select();
    const ok = document.execCommand("copy");
    box.remove();
    return ok;
  } catch (e) {
    return false;
  }
}

async function showCapstones() {
  viewer.innerHTML = '<div class="loading">بارگذاری Capstoneهای طراحی…</div>';
  breadcrumb.textContent = "Capstoneهای طراحی سازمان";
  try {
    const list = await api("/api/scenarios");
    viewer.innerHTML = '<div class="page-head"><div><h1>Capstoneهای معماری و طراحی</h1><p class="muted">این بخش پروژه‌های طراحی کلان را نگه می‌دارد؛ برای incident عملیاتی و گام‌های RCA، سناریوهای واقعی را انتخاب کن.</p></div>' +
      '<button type="button" id="btnBackIncidentList" class="ghost">سناریوهای واقعی</button></div><div class="scenario-list">' +
      list.map(function (s) {
        return '<div class="scenario-card" data-sid="' + s.id + '"><h3>' + escapeHtml(s.code) + ' — ' + escapeHtml(s.title_fa) +
          '</h3><div class="meta-row"><span class="chip">' + escapeHtml(s.level) + '</span><span class="chip">' +
          escapeHtml(s.difficulty) + '</span><span class="chip">' + (s.users || 0) + ' کاربر</span><span class="chip">' +
          (s.sites || 0) + ' سایت</span></div></div>';
      }).join("") + '</div>';
    document.getElementById("btnBackIncidentList").addEventListener("click", showScenarios);
    viewer.querySelectorAll(".scenario-card").forEach(function (card) {
      card.addEventListener("click", async function () {
        const sc = await api("/api/scenarios/" + card.dataset.sid);
        breadcrumb.textContent = sc.title_fa;
        viewer.innerHTML = '<div class="scenario-detail"><h1>' + escapeHtml(sc.code) + ' — ' + escapeHtml(sc.title_fa) +
          '</h1>' + section("بافت کسب‌وکار", sc.business_context) + section("نیازمندی‌ها", sc.requirements) +
          section("محدودیت‌ها", sc.constraints_text) + section("وضعیت اولیه", sc.initial_state) +
          section("حادثه / علائم", [sc.incident, sc.symptoms].filter(Boolean).join("\n")) +
          section("اهداف", sc.objectives) + section("وظایف", sc.tasks) + section("راهنمایی", sc.hints) +
          section("نتیجهٔ مورد انتظار", sc.expected_result) + section("راستی‌آزمایی", sc.verification) +
          section("مهارت‌های لازم", sc.skills_required) + '<button id="btnBackIncidentList" type="button" class="ghost">بازگشت</button></div>';
        document.getElementById("btnBackIncidentList").addEventListener("click", showCapstones);
      });
    });
  } catch (err) {
    viewer.innerHTML = '<div class="card">خطا در بارگذاری Capstoneها: ' + escapeHtml(err.message) + '</div>';
  }
}

function section(title, body) {
  if (!body || !String(body).trim()) return "";
  return `<h2>${escapeHtml(title)}</h2><pre>${escapeHtml(body)}</pre>`;
}


function formatJalaliDateTime(value) {
  try {
    const d = value ? new Date(value) : new Date();
    if (Number.isNaN(d.getTime())) return String(value || "");
    return new Intl.DateTimeFormat("fa-IR-u-ca-persian", {year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}).format(d);
  } catch (_) { return String(value || ""); }
}
function payloadArray(value, key) {
  if (Array.isArray(value)) return value;
  return value && Array.isArray(value[key]) ? value[key] : [];
}
async function showLearningHub() {
  breadcrumb.textContent = "مرکز یادگیری و پیگیری پیشرفت";
  const chapters = payloadArray(state.chapters, "chapters");
  const [studyStats, bankStats] = await Promise.all([api("/api/study/stats").catch(() => ({})),api("/api/stats").catch(() => ({}))]);
  const goal = Math.max(1, Math.min(100, Number(localStorage.getItem("networkall_daily_goal") || 15)));
  viewer.innerHTML = '<div class="page-head"><div><div class="eyebrow">LEARNING CENTER</div><h1>مرکز یادگیری؛ از مفهوم تا عیب‌یابی</h1><p class="muted">تاریخ امروز: ' + escapeHtml(formatJalaliDateTime(new Date().toISOString()).split("،")[0]) + ' · ابتدا مفهوم را بخوان، سپس با مثال و آزمون آن را تثبیت کن.</p></div></div>' +
    '<div class="meta-row"><span class="chip">فصل‌ها: ' + (bankStats.chapters || chapters.length || 68) + '</span><span class="chip">درس‌ها: ' + (bankStats.lessons || 0) + '</span><span class="chip">ثبت‌شده در مسیر مطالعه: ' + (studyStats.tracked || 0) + '</span><span class="chip">مسلط: ' + (studyStats.known || 0) + '</span><span class="chip">در حال یادگیری: ' + (studyStats.learning || 0) + '</span><span class="chip">نیازمند مرور: ' + (studyStats.due || 0) + '</span></div>' +
    '<div class="card"><div class="page-head"><div><h2>هدف روزانه</h2><p class="muted">هدف در همین مرورگر ذخیره می‌شود؛ پیشرفت هر درس جداگانه ثبت می‌شود.</p></div><div><input id="learningDailyGoal" type="number" min="1" max="100" value="' + goal + '" style="width:90px"><button id="btnSaveLearningGoal" type="button">ذخیره هدف</button></div></div></div>' +
    '<div class="card"><h2>انتخاب فصل و زیرشاخه</h2><p class="muted">برای جلوگیری از بارگیری هزاران درس یک‌باره، ابتدا فصل، سپس زیرشاخه و در نهایت درس را انتخاب کن.</p><div id="learningChapterList" class="learning-chapters">' +
    chapters.map(function(ch){return '<button type="button" class="ghost learning-chapter" data-chapter-id="'+ch.id+'"><strong>'+escapeHtml(ch.title_fa)+'</strong><small>فصل '+ch.order_index+'</small></button>';}).join("") +
    '</div><div id="learningPathDetails"></div></div>' +
    '<div class="meta-row"><button type="button" id="learningQuiz" class="ghost">شروع آزمون</button><button type="button" id="learningIncidents" class="ghost">سناریوهای عیب‌یابی</button><button type="button" id="learningPacketLab" class="ghost" onclick="window.location.href=\'/diagrams#packet-lab\'">آزمایشگاه تحلیل پکت</button><button type="button" id="learningDiagrams" class="ghost" onclick="window.location.href=\'/diagrams\'">دیاگرام‌ها</button></div>';
  document.getElementById("btnSaveLearningGoal").addEventListener("click",function(){const n=Math.max(1,Math.min(100,Number(document.getElementById("learningDailyGoal").value)||15));localStorage.setItem("networkall_daily_goal",String(n));document.getElementById("btnSaveLearningGoal").textContent="هدف ذخیره شد ✓";});
  viewer.querySelectorAll(".learning-chapter").forEach(function(btn){btn.addEventListener("click",function(){openLearningChapter(btn.dataset.chapterId,btn.querySelector("strong").textContent);});});
  document.getElementById("learningQuiz").addEventListener("click",showQuiz);
  document.getElementById("learningIncidents").addEventListener("click",showScenarios);
}
async function openLearningChapter(chapterId,title) {
  const panel=document.getElementById("learningPathDetails");if(!panel)return;panel.innerHTML='<div class="loading">بارگذاری زیرشاخه‌های '+escapeHtml(title)+'…</div>';
  try {
    const payload=await api("/api/chapters/"+encodeURIComponent(chapterId)+"/levels"),levels=payloadArray(payload,"levels");
    if(!levels.length){panel.innerHTML='<div class="loading">برای این فصل زیرشاخه‌ای ثبت نشده است.</div>';return;}
    panel.innerHTML='<h3>زیرشاخه‌های '+escapeHtml(title)+'</h3><div class="learning-levels">'+levels.map(function(lv){return '<button type="button" class="ghost" data-learning-level="'+lv.id+'">'+escapeHtml(lv.title_fa)+'</button>';}).join("")+'</div><div id="learningLessonList"></div>';
    panel.querySelectorAll("[data-learning-level]").forEach(function(btn){btn.addEventListener("click",function(){openLearningLevel(btn.dataset.learningLevel,btn.textContent);});});
  } catch(err){panel.innerHTML='<div class="loading">خطا در دریافت زیرشاخه: '+escapeHtml(err.message)+'</div>';}
}
async function openLearningLevel(levelId,title) {
  const list=document.getElementById("learningLessonList");if(!list)return;list.innerHTML='<div class="loading">بارگذاری درس‌ها…</div>';
  try {
    const payload=await api("/api/levels/"+encodeURIComponent(levelId)+"/lessons"),lessons=payloadArray(payload,"lessons");
    if(!lessons.length){list.innerHTML='<div class="loading">در این زیرشاخه درس ثبت نشده است.</div>';return;}
    list.innerHTML='<h3>درس‌های '+escapeHtml(title)+'</h3><div class="learning-lessons">'+lessons.map(function(les){return '<button type="button" class="ghost" data-learning-lesson="'+les.id+'">'+escapeHtml(les.title_fa)+' <small>'+escapeHtml(les.tags||"")+'</small></button>';}).join("")+'</div>';
    list.querySelectorAll("[data-learning-lesson]").forEach(function(btn){btn.addEventListener("click",function(){openLearningLesson(btn.dataset.learningLesson);});});
  } catch(err){list.innerHTML='<div class="loading">خطا در دریافت درس‌ها: '+escapeHtml(err.message)+'</div>';}
}
async function openLearningLesson(lessonId) {
  viewer.innerHTML='<div class="loading">بازکردن درس…</div>';
  try {
    const les=await api("/api/lessons/"+encodeURIComponent(lessonId));
    try{const depth=await api("/api/lessons/"+encodeURIComponent(lessonId)+"/specialized-depth");if(depth&&depth.available)les.specialized_depth=depth;}catch(_){}
    breadcrumb.textContent=les.title_fa||"درس";renderLesson(les);
  } catch(err){viewer.innerHTML='<div class="loading">خطا در بازکردن درس: '+escapeHtml(err.message)+'</div>';}
}

async function showQuiz() {
  breadcrumb.textContent = "مرکز آزمون عیب‌یابی";
  const bank = [
    {topic:"DNS و AD",q:"کلاینت به IP عمومی ping دارد، اما پیدا کردن Domain Controller و GPO شکست می‌خورد. اولین شاهد کدام است؟",choices:["خاموش و روشن‌کردن سوئیچ Core","DNS واقعی روی NIC و رکوردهای SRV با DNS داخلی","افزودن NAT روی روتر","افزایش MTU همهٔ VLANها"],answer:1,why:"مسیر IP ممکن است سالم باشد، ولی DC Locator به رکوردهای SRV داخلی نیاز دارد. DNS client و query مستقیم SRV فرضیه را می‌سنجد."},
    {topic:"Switching",q:"VLAN 30 وجود دارد و پورت Access درست است. فقط کاربران پشت یک uplink Gateway ندارند. کدام گام بیشترین ارزش تشخیصی را دارد؟",choices:["تعویض Gateway کلاینت‌ها","ریستارت همهٔ سوئیچ‌ها","مقایسهٔ allowed/forwarding VLAN در دو سر trunk","تغییر DNS به عمومی"],answer:2,why:"باید عبور VLAN از trunk و وضعیت STP را در هر دو سمت ببینی؛ تغییر Gateway علت عبور نکردن Tag را رفع نمی‌کند."},
    {topic:"MikroTik NAT",q:"از خود MikroTik ping اینترنت موفق است، ولی کلاینت LAN به IP عمومی دسترسی ندارد و masquerade counter صفر است. چه چیزی را اول بررسی می‌کنی؟",choices:["عضویت WAN interface جدید در interface-list و شرط NAT","DNS cache کلاینت فقط","تنظیمات OSPF همهٔ روترها","گواهی TLS وب‌سایت"],answer:0,why:"ترافیک تولیدشده توسط روتر و ترافیک forwardشده از LAN مسیر یکسانی ندارند. Counter صفر همراه interface-list mismatch می‌تواند NAT match را توضیح دهد."},
    {topic:"OSPF",q:"OSPF روی EXSTART مانده، IP ping روی لینک موفق است و MTU دو سمت 1500 و 1400 است. قدم درست چیست؟",choices:["ip ospf mtu-ignore را روی همهٔ روترها بزن","بدون backup رابط را reload کن","MTU واقعی مسیر و log/پارامترهای adjacency را تأیید و سپس هماهنگ اصلاح کن","Route استاتیک پیش‌فرض را حذف کن"],answer:2,why:"اختلاف MTU می‌تواند در تبادل Database Description مشکل ایجاد کند؛ ابتدا شواهد را با سایر علل EXSTART تطبیق بده. mtu-ignore وصلهٔ عمومی نیست."},
    {topic:"VPN",q:"Tunnel در وضعیت UP است ولی ترافیک subnet مرکز قطع است و route lookup به default WAN اشاره می‌کند. نتیجه چیست؟",choices:["UP بودن یعنی route درست است","احتمال route اشتباه؛ مسیر دقیق مقصد را با Change کنترل‌شده به VPN برگردان","DNS عمومی را روی همهٔ سرورها تنظیم کن","فاز IKE را هر دقیقه restart کن"],answer:1,why:"IKE وضعیت control-plane را نشان می‌دهد؛ route اشتباه می‌تواند جریان data-plane را از اینترنت خارج کند. SA counters، policy و return route نیز Verify شوند."},
    {topic:"DHCP",q:"کلاینت‌های قدیمی سالم و کلاینت‌های تازه دارای 169.254.x.x هستند. کدام شاهد Scope exhausted را از DHCP relay failure جدا می‌کند؟",choices:["فقط تعداد دستگاه‌های متصل به AP","Scope utilization/leaseها و مشاهدهٔ DORA روی VLAN","پینگ به یک وب‌سایت","تغییر WPA2 به WPA3"],answer:1,why:"Scope statistics و lease list ظرفیت را نشان می‌دهند؛ Capture تعیین می‌کند Discover به سرور می‌رسد و Offer/ACK برمی‌گردد یا نه."},
    {topic:"Packet flow",q:"Route در RIB وجود دارد، اما اتصال TCP برقرار نمی‌شود. چه کاری پیش از تغییر routing انجام می‌دهی؟",choices:["RIB/FIB/CEF، ACL/session و مسیر برگشت را بررسی می‌کنی","تمام Routeها را پاک می‌کنی","Subnet را کوچک‌تر می‌کنی","Gateway همهٔ کلاینت‌ها را عوض می‌کنی"],answer:0,why:"وجود route در RIB لزوماً عبور dataplane را ثابت نمی‌کند؛ forwarding adjacency، ACL، session و return path باید با شاهد بررسی شوند."},
    {topic:"MTU / HTTPS",q:"پینگ‌های کوچک و DNS موفق‌اند ولی HTTPS نیمه‌باز می‌ماند. کدام مسیر آزمایش مناسب‌تر است؟",choices:["فرض کن ISP قطع است","همهٔ DNSها را به 8.8.8.8 تغییر بده","MTU/DF/PMTUD، TCP retransmission و ICMP policy را اندازه بگیر","VLAN ID را تغییر بده"],answer:2,why:"الگوی size-dependent failure ممکن است به MTU/PMTUD مربوط باشد؛ با DF probe و packet capture تأیید کن، نه با تغییر تصادفی همهٔ تنظیمات."},
    {topic:"Troubleshooting",q:"قبل از اعمال Change روی firewall یا trunk چه چیزی باید آماده باشد؟",choices:["فقط یک ping موفق","Baseline/backup، دامنهٔ دقیق Change، معیار Verify و Rollback","پاک‌کردن counterها و logها","تغییر هم‌زمان چهار پارامتر"],answer:1,why:"بدون baseline نمی‌توان اثر Change را تشخیص داد و بدون Rollback ریسک قطعی بیشتر می‌شود. تغییر را کوچک و قابل‌اندازه‌گیری نگه دار."},
    {topic:"Firewall",q:"Packet روی ingress دیده می‌شود اما روی egress نه. بهترین کار بعدی چیست؟",choices:["تعویض کابل قبل از هر مشاهده","بررسی route lookup، policy match، NAT و session counters روی همان tuple","تعویض کلید Wi-Fi","Flush DNS در همهٔ کلاینت‌ها"],answer:1,why:"جریان باید با source/destination/protocol/port مشخص بررسی شود؛ route، deny logs، policy order و NAT counters می‌توانند محل drop را مشخص کنند."},
    {topic:"Wireless",q:"کلاینت به SSID وصل شده اما IP ندارد. کدام مسیر منطقی است؟",choices:["ابتدا اینترنت عمومی را blame کن","فقط تست TLS بگیر","Association/Auth → VLAN mapping → DHCP DORA → Gateway → DNS","روتر را Factory Reset کن"],answer:2,why:"Association فقط لایهٔ بی‌سیم را ثابت می‌کند. IP نداشتن باید از VLAN و DORA شروع شود؛ در غیر این صورت لایه‌ها را اشتباه قاطی می‌کنی."},
    {topic:"Evidence",q:"کدام گزارهٔ Incident Response دقیق‌تر است؟",choices:["یک ping موفق همهٔ سرویس‌ها را سالم ثابت می‌کند","اگر status سبز بود عیب‌یابی پایان یافته","شواهد چند نقطه‌ای، فرضیهٔ واحد، Change کنترل‌شده و تست End-to-End لازم است","همیشه قبل از جمع‌آوری logها Ruleها را تغییر بده"],answer:2,why:"Ping، tunnel UP یا adjacency FULL فقط یک بخش از مسیر را می‌سنجد؛ نتیجه باید با counter/log/capture و تست برنامه تطبیق داشته باشد."}
  ];
  const shuffled = bank.slice().sort(function () { return Math.random() - 0.5; }).slice(0, 8);
  viewer.innerHTML = '<div class="page-head"><div><div class="eyebrow">PRACTICAL TROUBLESHOOTING EXAM</div><h1>مرکز آزمون شبکه و عیب‌یابی</h1><p class="muted">۸ سؤال تصادفی از بانک عملیاتی؛ پس از تصحیح، پاسخ درست و منطق انتخاب را ببین. نتیجه در مرورگر همین دستگاه ثبت می‌شود.</p></div>' +
    '<button id="btnNewQuiz" type="button" class="ghost">آزمون تازه</button></div>' +
    '<div class="meta-row"><span class="chip">DNS/AD</span><span class="chip">Switching</span><span class="chip">MikroTik</span><span class="chip">OSPF/VPN</span><span class="chip">DHCP/MTU/Firewall</span></div>' +
    '<form id="quizForm">' + shuffled.map(function (q, i) {
      return '<article class="quiz-question" data-question="' + i + '"><div class="eyebrow">سؤال ' + (i + 1) + ' · ' + escapeHtml(q.topic) +
        '</div><h3>' + escapeHtml(q.q) + '</h3>' + q.choices.map(function (choice, j) {
          return '<label class="quiz-choice"><input type="radio" name="quiz-' + i + '" value="' + j + '"><span>' + escapeHtml(choice) + '</span></label>';
        }).join("") + '<div class="quiz-feedback-slot"></div></article>';
    }).join("") + '<button type="submit">تصحیح آزمون و نمایش منطق پاسخ</button></form><div id="quizResult"></div>';
  document.getElementById("btnNewQuiz").addEventListener("click", showQuiz);
  document.getElementById("quizForm").addEventListener("submit", function (event) {
    event.preventDefault();
    let score = 0;
    shuffled.forEach(function (q, i) {
      const chosen = viewer.querySelector('input[name="quiz-' + i + '"]:checked');
      const slot = viewer.querySelector('[data-question="' + i + '"] .quiz-feedback-slot');
      const ok = chosen && Number(chosen.value) === q.answer;
      if (ok) score++;
      slot.innerHTML = '<div class="quiz-feedback ' + (ok ? "ok" : "bad") + '"><strong>' +
        (ok ? "درست ✓" : "نیاز به بازبینی") + ' — پاسخ صحیح: ' + escapeHtml(q.choices[q.answer]) +
        '</strong><br>' + escapeHtml(q.why) + '</div>';
    });
    const percent = Math.round(score * 100 / shuffled.length);
    const result = document.getElementById("quizResult");
    result.innerHTML = '<div class="score-strip"><strong>نتیجه: ' + score + ' از ' + shuffled.length +
      ' (' + percent + '%)</strong><p>' + (percent >= 80 ? "خوب است؛ روی توجیه فنی پاسخ‌ها تمرکز کن." :
      percent >= 60 ? "مفاهیم پایه قابل قبول‌اند؛ سناریوهای مربوط به پاسخ‌های غلط را باز کن." :
      "بهتر است Runbookها را اجرا و شواهد را بررسی کنی، سپس آزمون تازه بدهی.") + '</p></div>';
    try {
      const key = "networkall_exam_history_v1";
      const history = JSON.parse(localStorage.getItem(key) || "[]");
      history.unshift({ date: new Date().toISOString(), score: score, total: shuffled.length, percent: percent });
      localStorage.setItem(key, JSON.stringify(history.slice(0, 20)));
      result.innerHTML += '<p class="muted">آخرین نمره در این مرورگر ثبت شد؛ تاریخچهٔ ذخیره‌شده: ' + Math.min(20, history.length) + ' آزمون.</p>';
    } catch (e) {}
    result.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
}

async function doSearch() {
  const q = $("#q").value.trim();
  if (!q) return;
  viewer.innerHTML = `<div class="loading">جستجو…</div>`;
  breadcrumb.textContent = `نتایج: ${q}`;
  const rows = await api(`/api/search?q=${encodeURIComponent(q)}`);
  if (!rows.length) {
    viewer.innerHTML = `<p class="empty-hint">موردی پیدا نشد.</p>`;
    return;
  }
  viewer.innerHTML = `<ul class="search-results">${rows
    .map(
      (r) => `<li data-id="${r.id}">
      <div>${escapeHtml(r.title_fa)}</div>
      <div class="path">${escapeHtml(r.chapter_title)} / ${escapeHtml(r.level_title)} · ${escapeHtml(r.tags || "")}</div>
    </li>`
    )
    .join("")}</ul>`;
  viewer.querySelectorAll("li").forEach((li) => {
    li.addEventListener("click", async () => {
      const les = await api(`/api/lessons/${li.dataset.id}`);
      breadcrumb.textContent = les.title_fa;
      renderLesson(les);
    });
  });
}

$("#btnSearch").addEventListener("click", doSearch);
$("#q").addEventListener("keydown", (e) => {
  if (e.key === "Enter") doSearch();
});
$("#btnScenarios").addEventListener("click", showScenarios);
const btnLearning = document.getElementById("btnLearning");
if (btnLearning) btnLearning.addEventListener("click", showLearningHub);


const btnQuiz = document.getElementById("btnQuiz");
if (btnQuiz) btnQuiz.addEventListener("click", showQuiz);

(async function init() {
  await loadChapters();
  await loadStats();
  const params = new URLSearchParams(window.location.search);
  const view = params.get("view");
  if (view === "incidents") await showScenarios();
  else if (view === "quiz") await showQuiz();
  else if (view === "learning") await showLearningHub();
})();
