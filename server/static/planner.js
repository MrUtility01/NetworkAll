/* Local-first planner. Jalali calendar uses the browser's Intl Persian calendar. */
(function () {
  "use strict";
  var $ = function (s) { return document.querySelector(s); };
  var calendar = $("#calendar"), taskBox = $("#tasks"), selectedLabel = $("#selectedLabel"), message = $("#formMessage");
  var TOKEN_KEY = "netenc_api_token";
  var weekdays = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"];
  var partsFmt = new Intl.DateTimeFormat("en-US-u-ca-persian-nu-latn", {year:"numeric", month:"numeric", day:"numeric"});
  var monthFmt = new Intl.DateTimeFormat("fa-IR-u-ca-persian", {year:"numeric", month:"long"});
  var dateFmt = new Intl.DateTimeFormat("fa-IR-u-ca-persian", {year:"numeric", month:"2-digit", day:"2-digit"});
  var selectedDate = new Date(), tasks = [], prompted = false;
  selectedDate.setHours(12,0,0,0);

  function jp(d) {
    var vals = {};
    partsFmt.formatToParts(d).forEach(function (p) {
      if (p.type === "year" || p.type === "month" || p.type === "day") vals[p.type] = Number(p.value);
    });
    return {year:vals.year, month:vals.month, day:vals.day};
  }
  function key(d) {
    return d.getFullYear() + "-" + String(d.getMonth()+1).padStart(2,"0") + "-" + String(d.getDate()).padStart(2,"0");
  }
  function jalali(d) { return dateFmt.format(d); }
  function datesForMonth(year, month) {
    var result = [], start = new Date(selectedDate.getFullYear()-1,0,1,12), end = new Date(selectedDate.getFullYear()+2,0,1,12);
    for (var d = new Date(start); d < end; d.setDate(d.getDate()+1)) {
      var p = jp(d);
      if (p.year === year && p.month === month) result.push(new Date(d));
    }
    return result;
  }
  function shiftMonth(delta) {
    var p = jp(selectedDate), list = datesForMonth(p.year,p.month);
    if (!list.length) return;
    var edge = delta > 0 ? list[list.length-1] : list[0];
    selectedDate = new Date(edge);
    selectedDate.setDate(selectedDate.getDate() + (delta > 0 ? 1 : -1));
    renderCalendar(); renderTasks();
  }
  function button(text, className, click, label) {
    var b = document.createElement("button");
    b.type = "button"; b.textContent = text; b.className = className;
    if (label) b.setAttribute("aria-label",label);
    b.addEventListener("click",click); return b;
  }
  function renderCalendar() {
    var p = jp(selectedDate);
    $("#monthTitle").textContent = monthFmt.format(selectedDate);
    calendar.replaceChildren();
    weekdays.forEach(function (d) { var el=document.createElement("div"); el.className="weekday"; el.textContent=d; calendar.appendChild(el); });
    var dates = datesForMonth(p.year,p.month);
    if (!dates.length) {
      var err=document.createElement("p"); err.className="error";
      err.textContent="تقویم شمسی در این مرورگر پشتیبانی نمی‌شود. مرورگر را به‌روز کنید.";
      calendar.appendChild(err); return;
    }
    var blanks = (dates[0].getDay()+1)%7;
    for (var i=0;i<blanks;i++) { var blank=document.createElement("div"); blank.setAttribute("aria-hidden","true"); calendar.appendChild(blank); }
    var today=key(new Date()), selected=key(selectedDate), counts=new Map();
    tasks.forEach(function (t) { if (t.due_at) { var k=String(t.due_at).slice(0,10); counts.set(k,(counts.get(k)||0)+1); }});
    dates.forEach(function (date) {
      var k=key(date), day=jp(date), b=document.createElement("button"), num=document.createElement("span"), count=document.createElement("span");
      b.type="button"; b.className="day";
      if (k===selected) b.classList.add("selected");
      if (k===today) b.classList.add("today");
      b.setAttribute("aria-label",jalali(date));
      num.className="num"; num.textContent=String(day.day);
      count.className="count"; var n=counts.get(k)||0; count.textContent=n ? String(n)+" کار" : " ";
      b.append(num,count);
      b.addEventListener("click",function(){ selectedDate=new Date(date); renderCalendar(); renderTasks(); });
      calendar.appendChild(b);
    });
  }
  function api(path, options) {
    options = options || {};
    var headers = new Headers(options.headers || {}), token = localStorage.getItem(TOKEN_KEY) || "";
    if (token) headers.set("X-NetEnc-Token",token);
    return fetch(path,Object.assign({},options,{headers:headers})).then(function (r) {
      if (r.status===401 && !prompted) {
        prompted=true;
        var entered=window.prompt("برای این سرور، مقدار NETENC_TOKEN را وارد کنید:");
        if (entered===null) throw new Error("درخواست لغو شد.");
        token=entered.trim();
        if (token) { localStorage.setItem(TOKEN_KEY,token); headers.set("X-NetEnc-Token",token); }
        else { localStorage.removeItem(TOKEN_KEY); headers.delete("X-NetEnc-Token"); }
        return fetch(path,Object.assign({},options,{headers:headers}));
      }
      return r;
    }).then(function (r) {
      return r.json().catch(function(){ return {}; }).then(function (data) {
        if (!r.ok) throw new Error(data.hint || data.error || ("HTTP " + r.status));
        return data;
      });
    });
  }
  function error(err) { message.textContent=err && err.message ? err.message : String(err); message.className="error"; }
  function taskCard(t) {
    var root=document.createElement("article"); root.className="task"+(t.done ? " done":"");
    var check=document.createElement("input"); check.type="checkbox"; check.checked=Boolean(t.done);
    check.setAttribute("aria-label","تغییر وضعیت انجام کار");
    check.addEventListener("change",function(){
      api("/api/planner/tasks/"+encodeURIComponent(t.uid),{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({done:check.checked})})
        .then(loadTasks).catch(function(e){check.checked=!check.checked;error(e);});
    });
    var content=document.createElement("div"), title=document.createElement("div"), body=document.createElement("div"), meta=document.createElement("div");
    title.className="task-title"; title.textContent=t.title||"کار بدون عنوان";
    body.className="task-body"; body.textContent=t.body||"";
    meta.className="meta";
    if (t.due_at) {
      var when=document.createElement("span"), time=String(t.due_at).split("T")[1]||"";
      when.textContent="ساعت "+time.slice(0,5)+" · "+jalali(new Date(String(t.due_at).slice(0,10)+"T12:00:00")); meta.appendChild(when);
    } else { var nd=document.createElement("span"); nd.textContent="بدون سررسید"; meta.appendChild(nd); }
    var priorities={1:"اولویت کم",2:"اولویت معمولی",3:"اولویت زیاد"}, priority=document.createElement("span");
    priority.className="priority"; priority.textContent=priorities[Number(t.priority)]||priorities[2]; meta.appendChild(priority);
    if (t.remind_at) { var rem=document.createElement("span"); rem.textContent="یادآوری فعال"; meta.appendChild(rem); }
    var del=button("حذف","danger",function(){
      if (!window.confirm("کار «"+t.title+"» حذف شود؟")) return;
      api("/api/planner/tasks/"+encodeURIComponent(t.uid),{method:"DELETE"}).then(loadTasks).catch(error);
    });
    del.style.padding="5px 9px"; meta.appendChild(del);
    content.append(title,body,meta); root.append(check,content); return root;
  }
  function renderTasks() {
    taskBox.replaceChildren(); selectedLabel.textContent=jalali(selectedDate);
    var selected=key(selectedDate), today=key(new Date());
    var todays=tasks.filter(function(t){ return t.due_at && String(t.due_at).slice(0,10)===selected; });
    var undated=selected===today ? tasks.filter(function(t){return !t.due_at;}) : [];
    var visible=todays.concat(undated).sort(function(a,b){
      return Number(Boolean(a.done))-Number(Boolean(b.done)) ||
        Number(b.priority||1)-Number(a.priority||1) ||
        String(a.due_at||"").localeCompare(String(b.due_at||""));
    });
    if (!visible.length) { var empty=document.createElement("div"); empty.className="empty"; empty.textContent="برای این روز کاری ثبت نشده است."; taskBox.appendChild(empty); return; }
    visible.forEach(function(t){ taskBox.appendChild(taskCard(t)); });
  }
  function loadTasks() {
    return api("/api/planner/tasks?limit=1000").then(function(data){
      tasks=Array.isArray(data.items)?data.items:[];
      renderCalendar(); renderTasks();
    }).catch(function(e){
      taskBox.replaceChildren(); var el=document.createElement("div"); el.className="error";
      el.textContent="بارگذاری کارها ناموفق بود: "+(e.message||e); taskBox.appendChild(el);
    });
  }
  $("#prevMonth").addEventListener("click",function(){shiftMonth(-1);});
  $("#nextMonth").addEventListener("click",function(){shiftMonth(1);});
  $("#todayBtn").addEventListener("click",function(){selectedDate=new Date();selectedDate.setHours(12,0,0,0);renderCalendar();renderTasks();});
  $("#taskForm").addEventListener("submit",function(ev){
    ev.preventDefault(); message.textContent="در حال ذخیره…"; message.className="muted";
    var title=$("#title").value.trim(), body=$("#body").value.trim(), time=$("#dueTime").value;
    var due=time ? key(selectedDate)+"T"+time : key(selectedDate);
    var reminder=$("#reminder").checked && Boolean(due);
    api("/api/planner/tasks",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({title:title,body:body,due_at:due,priority:Number($("#priority").value),reminder:reminder})})
      .then(function(){
        $("#taskForm").reset(); $("#priority").value="2"; $("#reminder").checked=true;
        message.textContent=reminder?"ذخیره شد؛ یادآوری روی رایانه فعال است، به شرط روشن و در حال اجرا بودن برنامه.":"ذخیره شد.";
        message.className="muted"; return loadTasks();
      }).catch(error);
  });
  renderCalendar(); loadTasks();
})();