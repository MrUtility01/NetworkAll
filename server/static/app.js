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

function jalaliDate(value = new Date(), withTime = false) {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  const options = withTime ? {calendar:"persian",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false} : {calendar:"persian",year:"numeric",month:"2-digit",day:"2-digit"};
  return new Intl.DateTimeFormat("fa-IR-u-ca-persian", options).format(date);
}

async function loadStats() {
  const dateEl = document.getElementById("currentDate");
  if (dateEl) dateEl.textContent = "تاریخ شمسی: " + jalaliDate();
  try {
    const s = await api("/api/stats");
    statsEl.textContent = `${s.chapters} فصل · ${s.levels} زیر‌فصل · ${s.lessons} درس · ${s.scenarios} سناریو · دارای محتوا: ${s.with_content}`;
  } catch (e) {
    statsEl.textContent = "خطا در آمار";
  }
}

function chapterSummary(ch) {
  const purpose = {
    62:"پایش عملیات روزانه، مدیریت Incident/Problem/Change، شیفت NOC و شاخص‌های SLA/SLO.",
    63:"نوشتن Runbook قابل اجرا، ثبت دارایی‌ها و وابستگی‌ها در CMDB و تحویل شیفت.",
    64:"کنترل نسخه، branch/merge، Pull Request، حل conflict و گردش‌کار امن GitHub.",
    65:"ارزیابی دفاعی تهدیدها، Hardening، پاسخ به حادثه، امنیت Wi‑Fi و آزمایش مجاز.",
    66:"طراحی و عیب‌یابی OSPF چندناحیه‌ای، BGP، policy و Redistribution بدون loop.",
    67:"ساخت VPN سازمانی IPsec/SSL، بررسی Phase 1/2، Route، NAT، Selector و packet counter.",
    68:"جست‌وجوی دستور بر اساس سازنده/موضوع، معنی پارامترها، مثال عملی، خروجی Verify و خطاهای رایج."
  };
  const order = Number(ch.order_index || ch.order || 0);
  if (purpose[order]) return purpose[order];
  const title = String(ch.title_fa || "این موضوع").replace(/^فصل\s*[۰-۹0-9]+\s*[:：\-–]?\s*/, "");
  return "هدف: یادگیری مفاهیم «" + title + "»، اجرای مثال کاربردی، راستی‌آزمایی نتیجه و عیب‌یابی گام‌به‌گام.";
}

async function loadChapters() {
  chaptersEl.innerHTML = `<div class="loading">بارگذاری فهرست فصل‌ها…</div>`;
  const list = await api("/api/chapters");
  state.chapters = list;
  chaptersEl.innerHTML = "";
  if (!list.length) {
    chaptersEl.innerHTML = `<div class="loading">فصلی نیست — بازسازی ساختار را بزنید</div>`;
    return;
  }
  list.forEach((ch) => {
    const wrap = document.createElement("div");
    wrap.className = "ch-item";
    wrap.dataset.cid = ch.id;
    wrap.innerHTML = `
      <button type="button" class="ch-btn" data-id="${ch.id}">
        <span class="caret">▶</span>
        <span class="chapter-copy"><span class="ch-title">${escapeHtml(ch.title_fa)}</span><span class="ch-subtitle">${escapeHtml(chapterSummary(ch))}</span></span>
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
      levels = Array.isArray(data) ? data : (Array.isArray(data?.levels) ? data.levels : []);
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
      lessons = Array.isArray(data) ? data : (Array.isArray(data?.lessons) ? data.lessons : []);
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

  viewer.innerHTML = `
    <div class="lesson-card">
      <h1>${escapeHtml(les.title_fa)}</h1>
      <div class="meta-row">
        <span class="chip">آخرین به‌روزرسانی: ${escapeHtml(jalaliDate(les.last_updated || new Date()))}</span>
        <span class="chip ${tag}">${escapeHtml(les.tags || "")}</span>
        <span class="chip">${escapeHtml(les.title_en || "")}</span>
        <span class="chip">وضعیت منبع: ${escapeHtml(les.source_status || "unverified")}</span>
      </div>
      <div class="study-actions">
        <span>یادگیری فعال · مرور فاصله‌دار</span>
        <button type="button" data-study="again">دوباره</button><button type="button" data-study="hard">سخت</button><button type="button" data-study="good">خوب</button><button type="button" data-study="easy">آسان</button>
        <span id="study-feedback" aria-live="polite"></span>
      </div>
      <div class="tabs">
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

  viewer.querySelectorAll("[data-study]").forEach((button) => {
    button.addEventListener("click", async () => {
      const feedback = document.getElementById("study-feedback");
      try {
        const result = await api("/api/study/mark", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({uid:String(les.id), action:button.dataset.study})});
        if (feedback) feedback.textContent = "مرور بعدی: " + jalaliDate(result.next_review, true);
      } catch (err) { if (feedback) feedback.textContent = "خطا در ثبت مرور: " + err.message; }
    });
  });
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
  viewer.innerHTML = `<div class="loading">بارگذاری سناریوها…</div>`;
  breadcrumb.textContent = "سناریوهای Capstone";
  const list = await api("/api/scenarios");
  const safeList = Array.isArray(list) ? list : (Array.isArray(list?.items) ? list.items : []);
  viewer.innerHTML = `
    <h1 style="margin-top:0">${safeList.length} سناریوی سازمانی و عیب‌یابی</h1>
    <div class="scenario-list">
      ${safeList
        .map(
          (s) => `
        <div class="scenario-card" data-sid="${s.id}">
          <h3>${escapeHtml(s.code)} — ${escapeHtml(s.title_fa)}</h3>
          <div class="meta-row">
            <span class="chip">${escapeHtml(s.level)}</span>
            <span class="chip">${escapeHtml(s.difficulty)}</span>
            <span class="chip">به‌روزرسانی: ${escapeHtml(jalaliDate(s.last_updated || new Date()))}</span>
            <span class="chip">${s.users || 0} کاربر</span>
            <span class="chip">${s.sites || 0} سایت</span>
            <span class="chip">${s.estimated_hours || 0} ساعت</span>
          </div>
        </div>`
        )
        .join("")}
    </div>`;
  viewer.querySelectorAll(".scenario-card").forEach((card) => {
    card.addEventListener("click", async () => {
      const sc = await api(`/api/scenarios/${card.dataset.sid}`);
      breadcrumb.textContent = sc.title_fa;
      viewer.innerHTML = `
        <div class="scenario-detail">
          <h1>${escapeHtml(sc.code)} — ${escapeHtml(sc.title_fa)}</h1>
          <div class="meta-row">
            <span class="chip">${escapeHtml(sc.vendors || "")}</span>
            <span class="chip">${escapeHtml(sc.category || "")}</span>
          </div>
          ${section("بافت کسب‌وکار", sc.business_context)}
          ${section("نیازمندی‌ها", sc.requirements)}
          ${section("محدودیت‌ها", sc.constraints_text)}
          ${section("وضعیت اولیه", sc.initial_state)}
          ${section("حادثه / علائم", [sc.incident, sc.symptoms].filter(Boolean).join("\n"))}
          ${section("اهداف", sc.objectives)}
          ${section("وظایف", sc.tasks)}
          ${section("راهنمایی", sc.hints)}
          ${section("نتیجه مورد انتظار", sc.expected_result)}
          ${section("راستی‌آزمایی", sc.verification)}
          ${section("مهارت‌های لازم", sc.skills_required)}
        </div>`;
    });
  });
}

function section(title, body) {
  if (!body || !String(body).trim()) return "";
  return `<h2>${escapeHtml(title)}</h2><pre>${escapeHtml(body)}</pre>`;
}

async function showLearningHub() {
  viewer.innerHTML = '<div class="loading">در حال بارگذاری مرکز یادگیری…</div>';
  breadcrumb.textContent = "مرکز یادگیری عمیق";
  let st = {}, due = [];
  try { st = await api("/api/study/stats"); } catch (_) {}
  try { const d = await api("/api/study/due?limit=10"); due = Array.isArray(d) ? d : (d.items || []); } catch (_) {}
  const scenarioCount = await safeScenarioCount();
  viewer.innerHTML = '<div class="learning-hub"><h1>مرکز یادگیری عمیق</h1>' +
    '<p>تاریخ امروز: <strong>' + escapeHtml(jalaliDate()) + '</strong> · مسیر یادگیری شامل مطالعه، تمرین، سنجش و مرور فاصله‌دار است.</p>' +
    '<div class="learning-stats"><div><b>' + Number(st.tracked || 0) + '</b><span>درس‌های پیگیری‌شده</span></div>' +
    '<div><b>' + Number(st.known || 0) + '</b><span>تسلط‌یافته</span></div><div><b>' + Number(st.due || due.length || 0) +
    '</b><span>مرور سررسیدشده</span></div><div><b>' + Number(st.learning || 0) + '</b><span>در حال یادگیری</span></div></div>' +
    '<div class="learning-actions"><button type="button" data-hub="quiz">آزمون کوتاه ۵ پرسشی</button>' +
    '<button type="button" data-hub="packet">تحلیل گام‌به‌گام پکت</button><button type="button" data-hub="scenarios">تمرین سناریوها (' + scenarioCount + ')</button>' +
    '<a href="/resources/network-book.docx">دریافت جزوهٔ جامع شبکه</a><a href="/resources/packet-journey-reference.png" target="_blank" rel="noopener">مشاهدهٔ تصویر مسیر پکت</a></div>' +
    '<h2>مرورهای سررسیدشده</h2>' + (due.length ? '<div class="due-list">' + due.map(x => '<div><b>' +
    escapeHtml(x.title_fa || x.lesson_uid || x.uid || "درس") + '</b><span>' + escapeHtml(jalaliDate(x.next_review || new Date(), true)) +
    '</span></div>').join("") + '</div>' : '<p class="empty-hint">مروری در سرور ثبت نشده است؛ برای مرور محلی از کارت‌های یادگیری اندروید استفاده کنید.</p>') +
    '<h2>روش کار پیشنهادی</h2><ol><li>یک مفهوم را از درخت درس‌ها باز کنید.</li><li>مثال یا آزمایشگاه را اجرا کرده و شواهد را یادداشت کنید.</li>' +
    '<li>پس از مطالعه، یکی از گزینه‌های مرور فاصله‌دار را ثبت کنید.</li><li>در سناریوها تشخیص، اصلاح، راستی‌آزمایی و Runbook را تمرین کنید.</li></ol></div>';
  viewer.querySelector('[data-hub="quiz"]').addEventListener("click", showQuickQuiz);
  viewer.querySelector('[data-hub="packet"]').addEventListener("click", () => window.PacketLab?.open());
  viewer.querySelector('[data-hub="scenarios"]').addEventListener("click", showScenarios);
}
async function safeScenarioCount() {
  try { const rows = await api("/api/scenarios"); return Array.isArray(rows) ? rows.length : (rows.items || []).length; }
  catch (_) { return 0; }
}
function showQuickQuiz() {
  const questions = [
    {q:"در Ethernet داخل همان VLAN، مقصد فریم چه آدرسی است؟",a:["MAC میزبان مقصد","MAC دروازهٔ پیش‌فرض","MAC DNS"],ok:0,why:"برای مقصد محلی، ARP آدرس MAC میزبان هدف را پیدا می‌کند؛ برای مقصد خارج subnet معمولاً MAC دروازه استفاده می‌شود."},
    {q:"کدام فیلد IPv4 در هر روتر معمولاً یک واحد کم می‌شود؟",a:["TTL","Source Port","TCP Window"],ok:0,why:"TTL کاهش می‌یابد و checksum سرآیند IPv4 به‌روزرسانی می‌شود."},
    {q:"TCP SYN-ACK معمولاً چه چیزی را نشان می‌دهد؟",a:["پاسخ به SYN و پذیرش شروع اتصال","پاسخ DNS","تغییر MAC توسط روتر"],ok:0,why:"SYN-ACK مرحلهٔ دوم handshake سه‌مرحله‌ای TCP است."},
    {q:"اگر Phase 1 در IPsec برقرار و Phase 2 پایین باشد، چه چیزی مهم است؟",a:["Traffic selectors/PFS و proposalهای Phase 2","رنگ کابل شبکه","نام SSID"],ok:0,why:"Selectors، proposal، PFS و route/NAT از علت‌های متداول‌اند."},
    {q:"آیا یک capture در یک سمت ثابت می‌کند packet در سمت دیگر drop شده؟",a:["خیر؛ capture دوطرفه و counters لازم است","بله همیشه","فقط با ping"],ok:0,why:"برای تعیین نقطهٔ drop، capture هماهنگ دو سوی مسیر و interface counters را مقایسه کنید."}
  ];
  let current = 0, score = 0;
  const render = () => {
    const q = questions[current];
    viewer.innerHTML = '<div class="learning-hub"><h1>آزمون کوتاه شبکه</h1><p>پرسش ' + (current+1) + ' از ' + questions.length +
      ' · امتیاز ' + score + '</p><h2>' + escapeHtml(q.q) + '</h2><div class="quiz-options">' +
      q.a.map((v,i) => '<button type="button" data-answer="' + i + '">' + escapeHtml(v) + '</button>').join("") +
      '</div><p id="quizFeedback"></p><button type="button" id="nextQuestion" disabled>' +
      (current===questions.length-1 ? "پایان آزمون" : "پرسش بعدی") + '</button></div>';
    viewer.querySelectorAll("[data-answer]").forEach(b => b.addEventListener("click", () => {
      viewer.querySelectorAll("[data-answer]").forEach(x => x.disabled = true);
      const ok = Number(b.dataset.answer) === q.ok; if (ok) score++;
      document.getElementById("quizFeedback").textContent = (ok ? "درست است. " : "پاسخ درست: " + q.a[q.ok] + ". ") + q.why;
      document.getElementById("nextQuestion").disabled = false;
    }));
    document.getElementById("nextQuestion").addEventListener("click", () => {
      current++;
      if (current >= questions.length) {
        viewer.innerHTML = '<div class="learning-hub"><h1>نتیجه آزمون</h1><p>امتیاز شما: ' + score + ' از ' + questions.length +
          '</p><button type="button" id="retryQuiz">تکرار آزمون</button><button type="button" id="backLearning">بازگشت به مرکز یادگیری</button></div>';
        document.getElementById("retryQuiz").addEventListener("click", () => { current=0; score=0; render(); });
        document.getElementById("backLearning").addEventListener("click", showLearningHub);
      } else render();
    });
  };
  render();
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
$("#btnLearning")?.addEventListener("click", showLearningHub);
$("#btnReseed").addEventListener("click", async () => {
  if (!confirm("ساختار از نو ساخته می‌شود (عناوین). ادامه؟")) return;
  viewer.innerHTML = `<div class="loading">بازسازی… ممکن است یک دقیقه طول بکشد</div>`;
  try {
    const info = await api("/api/reseed", { method: "POST" });
    state.levelsCache = {};
    state.lessonsCache = {};
    await loadChapters();
    await loadStats();
    viewer.innerHTML = `<pre>${escapeHtml(JSON.stringify(info, null, 2))}</pre>`;
  } catch (e) {
    viewer.innerHTML = `<div class="loading">خطا: ${escapeHtml(e.message)}</div>`;
  }
});

(async function init() {
  await loadChapters();
  await loadStats();
})();
